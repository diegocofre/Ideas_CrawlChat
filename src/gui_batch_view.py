import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from mainApp import *
from data import Batch
from dcProgresoBase import format_date  

class BatchView(tk.Toplevel):
    """
    Clase GUI para mostrar los detalles de un batch.   
    
    Autor: diego.cofre@gmail.com 
    12-2024, BUE, Argentina, 3ra roca desde el Sol, Vía Láctea
    """
    def __init__(self, master, app : MainApp, batch_id):
        """
        Inicializa la ventana de vista de batch.

        Args:
            master (tk.Tk): La ventana principal.
            app (MainApp): La instancia de la aplicación principal.
            batch_id (int): El ID del batch a mostrar.
        """
        super().__init__(master)
        self.title(f"Batch #{batch_id}")
        self.geometry("800x600")
        self.app = app
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Crear un contenedor para la caja de texto y el scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=BOTH, expand=True)
        
        # Caja de texto con nuevo estilo
        self.report_text = tk.Text(
            text_frame, 
            font=("Segoe UI", 12),
            bg="white",
            fg="#2e2e2e",
            insertbackground="#2e2e2e",
            padx=15,
            pady=15,
            wrap=tk.WORD,
            relief="flat",
            borderwidth=1
        )
        self.report_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(
            text_frame, 
            orient="vertical", 
            command=self.report_text.yview
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Vincular scrollbar a la caja de texto
        self.report_text.config(yscrollcommand=scrollbar.set)
        
        
        # Vincular scrollbar a la caja de texto
        self.report_text.config(yscrollcommand=scrollbar.set)
        
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(10, 0))
        
        # Botón copiar
        def copy_to_clipboard():
            content = self.report_text.get("1.0", tk.END)
            self.clipboard_clear()
            self.clipboard_append(content)
            copy_btn.configure(text="Copiado!")
            self.after(1500, lambda: copy_btn.configure(text="Copiar al portapapeles"))
        
        copy_btn = ttk.Button(
            button_frame,
            text="Copiar al portapapeles",
            style="info.TButton",
            command=copy_to_clipboard
        )
        copy_btn.pack(side=LEFT, padx=5)
        
        close_btn = ttk.Button(
            button_frame,
            text="Cerrar",
            style="secondary.TButton",
            command=self.destroy
        )
        close_btn.pack(side=RIGHT, padx=5)
        asyncio.run(self.load_batch_details(batch_id))

    async def load_batch_details(self, batch_id):
        """
        Carga los detalles del batch y los muestra en la ventana.

        Args:
            batch_id (int): El ID del batch a cargar.
        """
        batch : Batch = await self.app.get_batch_by_id(batch_id, eagger=True)   
        sites : List[BatchSite] = batch.batch_sites
        prompts : List[BatchPrompt] = batch.batch_prompts
        respuestas : List[BatchPromptResponse] = await self.app.get_batchresponses(batch_id)
        report = f"📦 BATCH #{batch.id} {batch.url_inicial.upper()}\n\n"
        report += f"📅 Fecha Inicio: {format_date(batch.fecha_creado)}\t\t\t Fecha Fin: {format_date(batch.fecha_terminado)}\n"
        report += f"📑 Sitios Analizados: {len(sites)}\t\t\tProfundidad: {batch.profundidad}\t\t\tCaracteres: {batch.caracteres}\n"
        
        numero = 1
        for site in sites:
            report += f"_"*50 + "\n"
            report += f"🔗 {numero}. {site.url}\n\n"            
            for prompt in prompts:
                report += f"• PROMPT: {prompt.prompt}\n"

                # Buscar respuesta correspondiente  
                for respuesta in respuestas:
                    if respuesta.batch_site_id == site.id and respuesta.batch_prompt_id == prompt.id:
                        report += f"• RESPUESTA: {respuesta.respuesta}\n"
                        break
                report += "\n"
            
            report += f"\n📄 CONTENIDO:\n{site.contenido}\n\n"
            numero += 1

        # Mostrar informe en el widget de texto
        self.report_text.insert(tk.END, report)
        self.report_text.config(state=tk.DISABLED)

# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # ID de ejemplo para el batch
    batch_id = 1

    report_window = BatchView(root, batch_id)
    root.mainloop()