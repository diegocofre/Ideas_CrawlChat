import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from gui_batch_view import BatchView
from gui_nuevo_batch import NuevoBatch
from mainApp import *
from data import Batch
import asyncio

class Historicos(tk.Toplevel):
    """
    Clase GUI para mostrar los históricos de batches.

    Autor: diego.cofre@gmail.com 
    12-2024, BUE, Argentina, 3ra roca desde el Sol, Vía Láctea
    """
    def __init__(self, master, app: MainApp):
        """
        Inicializa la ventana de históricos de batches.

        Args:
            master (tk.Tk): La ventana principal.
            app (MainApp): La instancia de la aplicación principal.
        """
        super().__init__(master)
        self.app = app
        self.title("Históricos de Batches")
        self.geometry("900x500")
        self.resizable(False, False)

        # Crear un contenedor para la tabla y el scrollbar
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill=BOTH)

        # Configurar estilos de fuente
        style = ttk.Style()

        # Crear la tabla con Treeview
        columnas = ("ID", "URL", "Fecha", "Reiniciar", "Ver")
        self.tree = ttk.Treeview(
            frame, columns=columnas, show="headings", height=10, style="info.Treeview"
        )
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.tree.yview, style="info.Vertical.TScrollbar"
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Definir encabezados de las columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("URL", text="Url Inicial", anchor=W)
        self.tree.heading("Fecha", text="Fecha Hora")
        self.tree.heading("Reiniciar", text="")
        self.tree.heading("Ver", text="")

        # Ajustar ancho de las columnas para el nuevo tamaño de fuente
        self.tree.column("ID", width=60, anchor=CENTER)
        self.tree.column("URL", width=550, anchor=W)
        self.tree.column("Fecha", width=150, anchor=CENTER)
        self.tree.column("Reiniciar", width=15, anchor=CENTER)
        self.tree.column("Ver", width=15, anchor=CENTER)

        # Eliminar la carga de imágenes y reemplazar con estilos
        style.configure("success.SmallButton", padding=2)
        style.configure("info.SmallButton", padding=2)

        # Cargar datos históricos
        self.load_historicos()

        # Configurar colores según el estado
        # self.tree.tag_configure("completado", foreground="green")
        # self.tree.tag_configure("error", foreground="red")
        # self.tree.tag_configure("pendiente", foreground="orange")

        # Vincular eventos
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_historicos(self):
        """
        Carga los datos históricos de batches en la tabla.
        """
        datos_historicos = asyncio.run(self.app.get_batches_historicos())

        # Agregar datos a la tabla con botones estilizados
        for batch in datos_historicos:
            id_ = batch.id
            url = batch.url_inicial
            fecha = batch.fecha_creado.strftime("%d-%m-%y %H:%M")

            # Crear botones estilizados para cada fila
            reiniciar_btn = "↻"  # Símbolo de reinicio
            ver_btn = "👁"  # Símbolo de ojo

            self.tree.insert(
                "",
                "end",
                values=(id_, url, fecha, reiniciar_btn, ver_btn),
                # tags=(estado.lower(),)  # Usar el estado como tag para colorear
            )

    def on_tree_select(self, event):
        """
        Maneja la selección de un elemento en la tabla.

        Args:
            event (tk.Event): El evento de selección.
        """
        selected_item = self.tree.focus()
        values = self.tree.item(selected_item, "values")
        if values:
            column_clicked = self.tree.identify_column(event.x)
            if column_clicked == "#4":  # Columna Reiniciar
                batch = asyncio.run(self.app.get_batch_by_id(values[0], eagger=True))

                NuevoBatch(self, self.app, batch)
            elif column_clicked == "#5":  # Columna Ver
                batch_id = values[0]
                BatchView(self, self.app, batch_id)

# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp()
    Historicos(root, app)
    root.mainloop()