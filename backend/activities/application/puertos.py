from typing import Protocol

from .dto import ConfirmacionInscripcion


class ErrorNotificacion(Exception):
    """El mecanismo no pudo entregar la confirmación."""


class Notificador(Protocol):
    def enviar(self, confirmacion: ConfirmacionInscripcion) -> None:
        """Entrega la confirmación o lanza ErrorNotificacion."""
