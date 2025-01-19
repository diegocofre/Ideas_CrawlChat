from playwright.async_api import async_playwright
from dcProgresoBase import  ProgresoBase
from urllib.parse import urlparse

class dcCrawler (ProgresoBase):
    """
    Clase para rastrear sitios web y extraer contenido de texto plano.
    Autor: diego.cofre@gmail.com 
    12-2024, BUE, Argentina, 3ra roca desde el Sol, Vía Láctea
    """
    
    def __init__(self, base_url, max_depth = 1, max_chars=5000, max_pages=100, max_pages_per_site=3):
        """
        Inicializa el crawler.
        
        Args:
            base_url (str): URL inicial para rastrear.
            max_depth (int): Profundidad máxima de rastreo.
        """
        super().__init__()
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_chars = max_chars
        self.max_pages = max_pages 
        self.max_pages_per_site = max_pages_per_site
        self.visited = set()
        self.analizar = set()   
        self.domain_counts = {}
        self.base_domain = self.get_domain(base_url)    
       
    
    async def fetch_page_content(self, url):
        """Extrae el contenido de texto plano de una página web."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                text_content = await page.evaluate("document.body.innerText")
                return text_content[:self.max_chars]  # Limit content length
            except Exception as e:
                self.notificar_progreso(f"Error al cargar la página {url}: {e}")
                return None
            finally:
                await browser.close()

    def check_max_pages(self):
        """Check if the maximum number of pages has been reached."""
        if len(self.visited) >= self.max_pages:
            #self.notificar_progreso(f"Sitio # {self.max_sites} alcanzado. Deteniendo el rastreo.")
            return True
        return False
    
    def check_max_pages_per_site(self, url):
        """Check if the maximum number of pages per site has been reached."""
        domain = self.get_domain(url)

        if(bool (domain and domain.strip()) == False):
            return True    
        
        # if(domain == self.base_domain):
        #     return True
        
        if domain not in self.domain_counts:
            self.domain_counts[domain] = 0

        if self.domain_counts[domain] < self.max_pages_per_site:
            self.domain_counts[domain] += 1
            self.notificar_progreso(f"{domain} aparecio {self.domain_counts[domain]} veces")
            return False
        
        return True

    def get_domain(self,url):
        return urlparse(url).netloc
    
    async def crawl_bfs(self):        
        """Realiza el rastreo BFS hasta la profundidad máxima."""
        queue = [(self.base_url, 0)]  # Cola de tuplas (URL, profundidad)
        self.visited.add(self.base_url.lower())
        while queue:
            url, depth = queue.pop(0)  # Extrae el primer elemento de la cola

            if depth > self.max_depth or self.check_max_pages() :
                break

            self.notificar_progreso(f"Extrayendo links de: {url} ({len(self.visited)} de {self.max_pages}) Prof: {depth}")

            # Extrae enlaces y guarda contenido
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    await page.goto(url, timeout=60000)
                    await page.wait_for_load_state("domcontentloaded")

                    # Extrae enlaces                    
                    links = await self.extract_valid_links(page)

                    for link in set(links):
                        link = link.lower()

                        if (self.check_max_pages_per_site(link)== False):
                            analizara = " & analizará"
                            self.analizar.add(link)   
                        else:
                            analizara = ""                         

                        if link not in self.visited:
                            self.visited.add(link)
                            queue.append((link, depth + 1))
                            self.notificar_progreso(f"Se visitará{analizara} {link} ({len(self.visited)}/{self.max_pages}) Prof: {depth + 1}")
                            if self.check_max_pages():
                                break


                except Exception as e:
                    self.notificar_progreso(f"Error al procesar la página {url}: {e}")                   

                finally:
                    await browser.close()

            if(queue == []):
                break

    async def extract_valid_links(self, page):
        #a.target !== '_blank' &&
        return await page.evaluate("""() => {
                        return Array.from(document.querySelectorAll('a[href]'))
                            .filter(a =>                                 
                                !a.href.startsWith('javascript:') && 
                                !a.href.startsWith('#') && 
                                !a.href.includes('mailto:') &&
                                !a.href.includes('tel:')
                            )
                            .map(a => a.href);
                    }""")

    async def crawl_recursive(self, url, depth):
        """Rastrea una página específica y extrae enlaces internos."""
        if url.lower() in self.visited or depth > self.max_depth or self.check_max_pages():
            return []
        
        self.visited.add(url.lower())
        self.notificar_progreso(f"Visitando: {url} - Visitados: {len(self.visited)} de {self.max_pages} - Profundidad: {depth}")

        if self.check_max_pages(): 
            return list(self.visited)

        # Extrae enlaces para rastrear
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                links = await self.extract_valid_links(page)
            except Exception as e:
                self.notificar_progreso(f"Error al extraer enlaces de {url}: {e}")
                links = []
            finally:
                await browser.close()

        # Rastrear cada enlace interno
        for link in set(links):
            if self.check_max_pages(): 
                break
            if(self.check_max_pages_per_site(link) == False):  
                await self.crawl_recursive(link, depth + 1)

        return list(self.visited)