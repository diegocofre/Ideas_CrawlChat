import datetime

def print_ts(message):
    """Imprime un mensaje con la marca de tiempo actual."""
    timestamp = format_date(datetime.datetime.now())
    print(f"[{timestamp}] {message}")

def format_date(date):
    """Formatea un objeto de fecha en una cadena."""
    return date.strftime("%d/%m/%y %H:%M") if date else ""

        # Función para validar entrada numérica
def validate_number(P):
    if P == "" or P.isdigit():
        return True
    return False
        

from abc import ABC, abstractmethod

class ProgresoBase(ABC):
    """
    Clase base para el seguimiento de notificaciones de progreso.
    
    Autor: diego.cofre@gmail.com 
    12-2024, BUE, Argentina, 3ra roca desde el Sol, Vía Láctea
    """
    def __init__(self):
        self._observadores = []  # Lista de funciones de callback registradas

    def registrar_notificador(self, callback):
        """
        Registra un callback para recibir mensajes de progreso.
        
        Args:
            callback (function): Una función callable para recibir mensajes de progreso.
        """
        if callable(callback):
            if callback not in self._observadores:
                self._observadores.append(callback)
        else:
            raise ValueError("El callback debe ser una función callable.")

    def notificar_progreso(self, mensaje: str):
        """
        Notifica a todos los callbacks registrados con un mensaje de progreso.
        
        Args:
            mensaje (str): El mensaje de progreso a notificar.
        """
        for callback in self._observadores:
            callback(mensaje)
