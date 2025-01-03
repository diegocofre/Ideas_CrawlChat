import tkinter as tk

def show_splash_screen():
    """
    Muestra una pantalla de carga (splash screen) mientras se inicializa la aplicación.

    Returns:
        splash_root (tk.Tk): La ventana de la pantalla de carga.
    """
    splash_root = tk.Tk()
    splash_root.overrideredirect(True)
    splash_root.geometry("400x300+500+300")  # Ajusta el tamaño y la posición según tus necesidades

    splash_label = tk.Label(splash_root, text="Cargando...", font=("Helvetica", 24))
    splash_label.pack(expand=True)

    splash_root.update()
    return splash_root