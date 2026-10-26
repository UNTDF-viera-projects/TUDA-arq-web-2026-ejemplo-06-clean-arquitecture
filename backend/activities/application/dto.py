from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConfirmacionInscripcion:
    """Lo que la aplicación necesita comunicar, sin detalles de correo."""

    destinatario: str
    nombre: str
    actividad: str
    inicia_en: datetime
