import tkinter as tk
from tkinter import ttk, messagebox
from data import *
from dcBase import format_date
from mainApp import *
import asyncio
import threading

class BatchConsole(tk.Toplevel):
    """
    Clase GUI para mostrar la consola del batch.
    
    Autor: diego.cofre@gmail.com 12-2024, 3ra roca desde el Sol, Vía Láctea
    """
    def __init__(self, master, app: MainApp, batch: Batch):
        super().__init__(master)
        self.title("Consola de Batch")
        self.geometry("800x700")
        #self.configure(bg="#2e2e2e")

        # Frame para la consola y la scrollbar
        console_frame = ttk.Frame(self)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar vertical
        self.scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Widget de texto para la consola
        self.console_text = tk.Text(
            console_frame,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Consolas", 12),
            yscrollcommand=self.scrollbar.set
        )
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.console_text.yview)

        # Frame para los botones
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Botón para copiar al portapapeles
        self.copy_button = ttk.Button(
            button_frame,
            text="Copiar al portapapeles",
            style="info.TButton",
            command=self.copy_to_clipboard,
        )
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancelar Batch",
            style="danger.TButton",
            command=self.confirm_cancel_batch,
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)

        # Inicializar el loop de eventos en un hilo aparte
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._start_event_loop, daemon=True).start()

        # Parámetros del batch
        self.batch = batch
        self.app = app
        self.task = None
        self.app.registrar_notificador(self.write_to_console)

        self.start_batch()

    def _start_event_loop(self):
        """Inicia el loop de eventos asyncio en un hilo separado."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_batch(self):
        """Inicia la tarea de procesamiento del batch."""
        if not self.task:
            self.task = asyncio.run_coroutine_threadsafe(self._start_batch(), self.loop)

    async def _start_batch(self):
        """Método asincrónico para iniciar el procesamiento del batch."""
        try:
            await self.app.init_batch(self.batch)
        except asyncio.CancelledError:
            print("Task was cancelled")

    def write_to_console(self, text):
        """
        Escribe un mensaje en la consola con una marca de tiempo.
        
        Args:
            text (str): El mensaje a escribir en la consola.
        """
        timestamp = format_date(datetime.now())
        self.console_text.insert(tk.END, f"[{timestamp}] {text}" + "\n")
        self.console_text.see(tk.END)

    def copy_to_clipboard(self):
        """Copia el contenido de la consola al portapapeles."""
        content = self.console_text.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(content)
        self.copy_button.configure(text="Copiado!")
        self.after(1500, lambda: self.copy_button.configure(text="Copiar al portapapeles"))

    def confirm_cancel_batch(self):
        """Muestra un cuadro de diálogo de confirmación antes de cancelar el batch."""
        if messagebox.askyesno("Confirmar", f"La tarea se cancelará ¿Está seguro?"):
            self.cancel_batch()

    def cancel_batch(self):
        """Cancela la tarea de procesamiento del batch."""
        if self.task:
            print("Cancelling task...")
            self.task.cancel()
        self.destroy()


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Mock para MainApp
    app = MainApp()

    batch = asyncio.run(app.get_batch_by_id(1, True))

    root.withdraw()
    console = BatchConsole(root, app, batch)
    root.mainloop()
