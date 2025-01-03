from playwright.async_api import async_playwright
from dcBase import  ProgresoBase

class dcCrawler (ProgresoBase):
    """Clase para rastrear sitios web y extraer contenido de texto plano."""
    
    def __init__(self, base_url, max_depth = 1, max_chars=5000, max_sites=100):
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
        self.max_sites = max_sites
        self.visited = set()
       
    
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

        def save_to_file(self, url, content):
            """Guarda el contenido de la página en el archivo."""
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(f"Contenido de la página {url}:\n\n")
                f.write(content if content else "[No se pudo extraer contenido]\n")
                f.write("\n" + "-" * 80 + "\n")

    def check_max_sites(self):
        """Check if the maximum number of sites has been reached."""
        if len(self.visited) >= self.max_sites:
            #self.notificar_progreso(f"Sitio # {self.max_sites} alcanzado. Deteniendo el rastreo.")
            return True
        return False

    async def crawl_recursive(self, url, depth):
        """Rastrea una página específica y extrae enlaces internos."""
        if url.lower() in self.visited or depth > self.max_depth or self.check_max_sites():
            return []
        self.visited.add(url.lower())
        self.notificar_progreso(f"Visitando: {url} - Visitados: {len(self.visited)} de {self.max_sites} - Profundidad: {depth}")

        if self.check_max_sites(): 
            return list(self.visited)

        # Extrae enlaces para rastrear
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                links = await page.evaluate("""
                    Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                """)
            except Exception as e:
                self.notificar_progreso(f"Error al extraer enlaces de {url}: {e}")
                links = []
            finally:
                await browser.close()

        # Rastrear cada enlace interno
        for link in set(links):
            if self.check_max_sites(): 
                break
            await self.crawl_page(link, depth + 1)

        return list(self.visited)

    async def crawl_bfs(self):
        """Realiza el rastreo BFS hasta la profundidad máxima."""
        queue = [(self.base_url, 0)]  # Cola de tuplas (URL, profundidad)

        while queue:
            url, depth = queue.pop(0)  # Extrae el primer elemento de la cola

            if depth > self.max_depth or self.check_max_sites() :
                break

            self.notificar_progreso(f"Extrayendo links de: {url} - Extraidos: {len(self.visited)} de {self.max_sites} - Profundidad: {depth}")

            # Extrae enlaces y guarda contenido
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    await page.goto(url, timeout=60000)
                    await page.wait_for_load_state("domcontentloaded")

                    # Extrae enlaces
                    links = await page.evaluate("""
                        Array.from(document.querySelectorAll('a[href]'))
                        .map(a => a.href)
                    """)

                    for link in set(links):
                        if link.lower() not in self.visited:
                            self.visited.add(link)
                            queue.append((link, depth + 1))
                            self.notificar_progreso(f"Se agrega {link} ({len(self.visited)}/{self.max_sites}) Prof: {depth + 1}")   
                            if self.check_max_sites():
                                break   

                except Exception as e:
                    self.notificar_progreso(f"Error al procesar la página {url}: {e}")

                finally:
                    await browser.close()

    def save_to_file_bak(self, url, content):
        """Guarda el contenido de la página en el archivo."""
        with open(self.output_file, "a", encoding="utf-8") as f:
            #f.write(f"Contenido de la página {url}:\n")
            f.write(content)
            #f.write("\n" + "-" * 80 + "\n")
    
    async def run_crawl_getcontent_bak(self):
        """Inicia el rastreo del sitio web."""
        self.notificar_progreso(f"Inicia Crawl de {self.base_url}")
        await self.crawl_bfs()
        urls = list(self.visited)
        total_urls = len(urls)
        self.notificar_progreso(f"Se obtuvieron {total_urls} URLs")

        for index, url in enumerate(urls[1:], start=0):  # Start from the second element
            self.notificar_progreso(f"Obteniendo contenido de {url} ({index + 1}/{total_urls})...")
            content = await self.fetch_page_content(url)
            if content:
                header = f"\n*** Inicio: {url} ({index + 1}/{total_urls}) ***\n"
                self.save_to_file(url, header + content)
                self.notificar_progreso(f"Contenido de {url} guardado.")
            else:
                self.notificar_progreso(f"No se pudo obtener contenido de {url}.")



