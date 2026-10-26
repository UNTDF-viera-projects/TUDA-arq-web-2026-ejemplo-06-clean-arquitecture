from ...application.dto import ConfirmacionInscripcion
from ...application.puertos import ErrorNotificacion


class NotificadorFallo:
    """Falla siempre: reproduce un servidor de correo caído de forma predecible."""

    def enviar(self, confirmacion: ConfirmacionInscripcion) -> None:
        raise ErrorNotificacion("Fallo simulado")
