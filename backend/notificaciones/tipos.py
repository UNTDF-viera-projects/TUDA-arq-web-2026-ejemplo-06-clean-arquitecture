from dataclasses import dataclass


@dataclass(frozen=True)
class Correo:
    destinatario: str
    asunto: str
    cuerpo: str


class ErrorDeEnvio(Exception):
    """El canal no pudo enviar el correo."""
