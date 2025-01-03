import asyncio
import datetime
from typing import List
from dcCrawler import dcCrawler
from dcOracle import dcOracle
import data
from dcBase import print_ts, ProgresoBase
import logging
from data import *
import os

# Disable SQLAlchemy logging for SQLite
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
# Configurar playwright para usar un directorio de navegadores específico
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "ms-playwright"
os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://playwright.azureedge.net"

class MainApp(ProgresoBase):
    """
    Clase principal de la aplicación para gestionar el rastreo web y el procesamiento.
    
    Autor: diego.cofre@gmail.com 12-2024, 3ra roca desde el Sol, Vía Láctea
    """
    def __init__(self):
        """
        Inicializa la aplicación principal y configura la base de datos.
        """
        super().__init__()

        self.engine = asyncio.run(data.init_db())
        self.async_sessionmaker = data.sessionmaker(
            bind=self.engine, class_=data.AsyncSession, expire_on_commit=False
        )

    async def init_batch(self, batch: Batch):
        """
        Inicializa y procesa un lote de tareas de rastreo web.
        
        Args:
            batch (Batch): El objeto batch que contiene los parámetros para el rastreo.
        """
        try:
            self.notificar_progreso("Iniciando batch...")
            # guardar el batch en la base de datos
            async with self.async_sessionmaker() as session:
                new_prompts = batch.new_prompts
                batch = await data.create_batch(
                    session,
                    batch.url_inicial,
                    batch.profundidad,
                    batch.sitios,
                    batch.caracteres,
                )
                batch_id = batch.id

                # guardar los prompts en la base de datos
                for p in new_prompts:
                    await data.create_batch_prompt(session, batch_id, p)

                self.notificar_progreso(
                    f"Batch #{batch_id} guardado. Iniciando crawler..."
                )

                crawler = dcCrawler(
                    batch.url_inicial, batch.profundidad, batch.caracteres, batch.sitios
                )
                crawler.registrar_notificador(self.notificar_progreso)
                oracle = dcOracle()
                await crawler.crawl_bfs()

                total_sites = len(crawler.visited)

                self.notificar_progreso(
                    f"{total_sites} sitios encontrados. Obteniendo contenido..."
                )
                for index, url in enumerate(crawler.visited, start=0):
                    content = await crawler.fetch_page_content(url)
                    await data.create_batch_site(session, batch_id, url, content)
                    self.notificar_progreso(
                        f"{url} contenido guardado ({index + 1}/{total_sites})"
                    )


                sites = await data.get_batch_sites(session, batch_id)
                prompts = await data.get_batch_prompts(session, batch_id)
                # recorrer cada sitio y procesar con GPT
                for index, site in enumerate(sites, start=0):
                    self.notificar_progreso(
                        f"{site.url} procesando con GPT ({index+1}/{len(sites)})..."
                    )
                    for prompt in prompts:
                        response = oracle.process_web(site.contenido, prompt.prompt)
                        await data.create_batch_prompt_response(
                            session, batch_id, site.id, prompt.id, response
                        )
                        self.notificar_progreso(f"P: {prompt.prompt}\nR: {response}")

                await data.update_batch(session, batch_id, fecha_terminado=datetime.now())
                self.notificar_progreso(f"Batch #{batch_id} finalizado!")
        except asyncio.CancelledError:
            self.notificar_progreso("Batch cancelado.")
            raise
        except Exception as e:
            self.notificar_progreso(f"Error: {e}")
            raise

    async def get_batches_historicos(self):
        """
        Recupera todos los batches históricos de la base de datos.
        
        Returns:
            List[Batch]: Una lista de todos los batches históricos.
        """
        async with self.async_sessionmaker() as session:
            return await data.get_batches(session)

    async def get_batch_by_id(self, batch_id, eagger=False):
        """
        Recupera un batch por su ID.
        
        Args:
            batch_id (int): El ID del batch a recuperar.
            eagger (bool): Si se deben cargar los datos relacionados de forma anticipada.
        
        Returns:
            Batch: El objeto batch con el ID especificado.
        """
        async with self.async_sessionmaker() as session:
            return await data.get_batch(session, batch_id, eagger)

    async def get_batchresponses(self, batch_id):
        """
        Recupera todas las respuestas para un batch dado.
        
        Args:
            batch_id (int): El ID del batch para recuperar respuestas.
        
        Returns:
            List[BatchPromptResponse]: Una lista de todas las respuestas para el batch especificado.
        """
        async with self.async_sessionmaker() as session:
            return await data.get_batch_responses(session, batch_id)


if __name__ == "__main__":
    app = MainApp()
    app.registrar_notificador(print_ts)

    b = Batch()
    b.url_inicial = "https://www.yellowpages.com/state-fl"
    b.profundidad = 4
    b.caracteres = 2000
    b.sitios = 100
    b.new_prompts = [
        "Cuál es el propósito del sitio?",
        "Analyze the following text and indicate how many grammatical and/or orthographic mistakes you find, and what they are.",
    ]

    asyncio.run(app.init_batch(b))
