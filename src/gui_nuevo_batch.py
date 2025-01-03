import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, IntVar, messagebox, Listbox, Tk
from gui_batch_console import BatchConsole
from data import *
from mainApp import *
from dcBase import validate_number

class NuevoBatch(ttk.Toplevel):
    """
    Clase GUI para crear y configurar un nuevo batch.

    Autor: diego.cofre@gmail.com 12-2024, 3ra roca desde el Sol, Vía Láctea
    """
    def __init__(self, master, app: MainApp, batch: Batch = None):
        """
        Inicializa la ventana para crear un nuevo batch.

        Args:
            master (tk.Tk): La ventana principal.
            app (MainApp): La instancia de la aplicación principal.
            batch (Batch, opcional): Un objeto batch existente para editar. Si no se proporciona, se crea uno nuevo.
        """
        super().__init__(master)
        self.title("Nuevo Batch")
        self.geometry("500x500")
        self.resizable(False, False)
        self.app = app

        # Si no se proporciona un batch, crear uno con valores predeterminados
        if batch is None:
            batch = Batch(
                url_inicial="http://www.ejemplo.com",
                caracteres=5000,
                profundidad=3,
                sitios=100,
                batch_prompts=[]
            )

        self.batch = batch

        # Variables para los parámetros
        self.url_inicial = StringVar(value=self.batch.url_inicial)
        self.max_caracteres = IntVar(value=self.batch.caracteres)
        self.profundidad = IntVar(value=self.batch.profundidad)
        self.max_paginas = IntVar(value=self.batch.sitios)
        self.prompts = [prompt.prompt for prompt in self.batch.batch_prompts]

        # Crear el marco principal
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        # URL inicial
        ttk.Label(frame, text="URL Inicial", font=("Verdana", 11),  foreground="white").pack(anchor=W)
        url_entry = ttk.Entry(frame, textvariable=self.url_inicial)
        url_entry.pack(fill=X, pady=4)
        url_entry.configure(style="TEntry", foreground="white")

        # Frame horizontal para parámetros numéricos
        params_frame = ttk.Frame(frame)
        params_frame.pack(fill=X, pady=10)

        vcmd = self.register(validate_number)

        # Parámetros numéricos en línea
        # Max caracteres
        max_chars_frame = ttk.Frame(params_frame)
        max_chars_frame.pack(side=LEFT, padx=(0, 5))
        ttk.Label(max_chars_frame, text="Max Caracteres", font=("Verdana", 11), foreground="white").pack(anchor=W)
        max_caracteres_entry = ttk.Entry(max_chars_frame, textvariable=self.max_caracteres, width=8, 
                                       validate="key", validatecommand=(vcmd, '%P'))
        max_caracteres_entry.pack(fill=X)

        # Profundidad
        prof_frame = ttk.Frame(params_frame)
        prof_frame.pack(side=LEFT, padx=(5, 5), expand=True)
        ttk.Label(prof_frame, text="Prof", font=("Verdana", 11), foreground="white").pack(anchor=W)
        profundidad_entry = ttk.Entry(prof_frame, textvariable=self.profundidad, width=8,
                                    validate="key", validatecommand=(vcmd, '%P'))
        profundidad_entry.pack(fill=X)

        # Max páginas
        max_pag_frame = ttk.Frame(params_frame)
        max_pag_frame.pack(side=RIGHT, padx=(5, 0))
        ttk.Label(max_pag_frame, text="Max Sitios", font=("Verdana", 11), foreground="white").pack(anchor=W)
        max_paginas_entry = ttk.Entry(max_pag_frame, textvariable=self.max_paginas, width=8,
                                    validate="key", validatecommand=(vcmd, '%P'))
        max_paginas_entry.pack(fill=X)

        # Sección para prompts
        ttk.Label(frame, text="Prompts", font=("Verdana", 11),  foreground="white").pack(anchor=W, pady=(8, 0))

        # Entrada y botones para prompts
        prompt_frame = ttk.Frame(frame)
        prompt_frame.pack(fill=X, pady=5)

        self.prompt_entry = ttk.Entry(prompt_frame)
        self.prompt_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.prompt_entry.configure(style="TEntry",  foreground="white")

        ttk.Button(prompt_frame, text="+", style="success.TButton", command=self.agregar_prompt).pack(side=LEFT)
        ttk.Button(prompt_frame, text="-", style="danger.TButton", command=self.eliminar_prompt).pack(side=LEFT)

        # Listbox para mostrar los prompts agregados
        self.prompt_listbox = Listbox(frame, height=8, bg="black", fg="white", selectbackground="gray", highlightbackground="white", relief=FLAT)
        self.prompt_listbox.pack(fill=BOTH, expand=True, pady=(5, 10))

        # Cargar los prompts en el Listbox
        for prompt in self.prompts:
            self.prompt_listbox.insert(END, prompt)

        # Botón para iniciar el batch
        btn_iniciar_batch = ttk.Button(
            frame,
            text="Guardar e Iniciar",
            style="TButton",
            command=self.iniciar_batch
        )
        btn_iniciar_batch.pack(fill=X, pady=(20, 0))

    def agregar_prompt(self):
        """
        Agrega un nuevo prompt a la lista de prompts.
        """
        prompt = self.prompt_entry.get().strip()
        if prompt:
            self.prompts.append(prompt)
            self.prompt_listbox.insert(END, prompt)
            self.prompt_entry.delete(0, END)

    def eliminar_prompt(self):
        """
        Elimina el prompt seleccionado de la lista de prompts.
        """
        selected = self.prompt_listbox.curselection()
        if selected:
            index = selected[0]
            self.prompts.pop(index)
            self.prompt_listbox.delete(index)

    def iniciar_batch(self):
        """
        Guarda los parámetros del batch y lo inicia.
        """
        if not self.url_inicial.get():
            messagebox.showerror("Error", "La URL inicial es obligatoria.")
            return

        # Validar que haya por lo menos un prompt
        if not self.prompts:
            messagebox.showerror("Error", "Debe agregar al menos un prompt.")
            return
        
        self.batch.new_prompts = self.prompts
        self.batch.url_inicial = self.url_inicial.get()
        self.batch.profundidad = self.profundidad.get()
        self.batch.caracteres = self.max_caracteres.get()   
        self.batch.sitios = self.max_paginas.get()  
        
        self.withdraw()
        BatchConsole(self, self.app, self.batch)
        #self.destroy()
        self.mainloop()       


# Ejemplo de uso
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal

    app = MainApp()
    NuevoBatch(root, app)
    root.mainloop()

