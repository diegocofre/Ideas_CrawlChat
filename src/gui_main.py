import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui_historicos import Historicos
from gui_nuevo_batch import NuevoBatch
from mainApp import MainApp 
from dotenv import load_dotenv
from gui_splash import show_splash_screen


def main():
    """
    Función principal para iniciar la aplicación GUI.

    Autor: diego.cofre@gmail.com 
    12-2024, BUE, Argentina, 3ra roca desde el Sol, Vía Láctea
    """
    root = ttk.Window(themename="superhero")  # Estilo moderno
    #splash_root = show_splash_screen()
    setStyle()

    load_dotenv()
    app = MainApp()
    # Crear la ventana principal

    root.title("Crawler GPT")
    root.geometry("400x300")
    root.resizable(False, False)

    # Crear un marco principal para centrar los botones
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True)

    # Título de la aplicación
    title_label = ttk.Label(
        frame,
        text="Web Crawler GPT",
        font=("Verdana", 19, "bold"),  # Incrementado de 18 a 19
        anchor=CENTER,
    )

    title_label.pack(pady=(0, 20))  # Espaciado inferior



    # Botones
    btn_nuevo_batch = ttk.Button(
        frame, text="Nuevo Batch", style="primary.TButton", command=lambda:NuevoBatch(root, app)
    )
    btn_nuevo_batch.pack(fill=X, pady=10)  # Botón 1

    btn_ver_historicos = ttk.Button(
        frame, text="Ver Históricos", style="info.TButton", command=lambda:Historicos(root,app)
    )
    btn_ver_historicos.pack(fill=X, pady=10)  # Botón 2

    btn_salir = ttk.Button(
        frame, text="Salir", style="danger.TButton", command=root.quit
    )
    btn_salir.pack(fill=X, pady=10)  # Botón 3

    #splash_root.destroy()
    # Iniciar el loop principal
    root.mainloop()

def setStyle():
    """
    Configura los estilos de los widgets de la aplicación.
    """
    # Configurar estilo de fuente para botones
    style = ttk.Style()

    # Configurar estilos con altura fija
    style.configure("primary.TButton", font=("Verdana", 11))
    style.configure("info.TButton", font=("Verdana", 11))
    style.configure("danger.TButton", font=("Verdana", 11))
    style.configure("success.TButton", font=("Verdana", 11))
    style.configure("TButton", foreground="#ffffff", font=("Verdana", 11))
    style.map("TButton", background=[("active", "#3e3e3e")])

    # Aumentar tamaño de fuente y configurar alto de filas
    style.configure("info.Treeview", 
                   font=("Verdana", 11),
                   rowheight=30)  # Aumentar alto de filas
    style.configure("info.Treeview.Heading", 
                   font=("Verdana", 11, "bold"),
                   padding=(5, 5))  # Añadir padding a los encabezados
    style.configure("success.SmallButton", padding=2, font=("Verdana", 11, "bold"))
    style.configure("info.SmallButton", padding=2, font=("Verdana", 11, "bold"))

if __name__ == "__main__":
    main()
