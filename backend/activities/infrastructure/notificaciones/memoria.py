from ...application.dto import ConfirmacionInscripcion


class NotificadorMemoria:
    """Guarda las confirmaciones en una lista: sirve para tests y demos sin correo."""

    def __init__(self):
        self.enviadas: list[ConfirmacionInscripcion] = []

    def enviar(self, confirmacion: ConfirmacionInscripcion) -> None:
        self.enviadas.append(confirmacion)
