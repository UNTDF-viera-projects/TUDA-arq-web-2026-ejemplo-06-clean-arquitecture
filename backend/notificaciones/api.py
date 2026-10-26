"""Interfaz pública del módulo de notificaciones."""

from . import canales
from .tipos import Correo, ErrorDeEnvio

__all__ = ["Correo", "ErrorDeEnvio", "enviar"]


def enviar(correo: Correo) -> None:
    """Envía el correo por el canal configurado (NOTIFICADOR) o lanza ErrorDeEnvio."""
    canales.canal_configurado().enviar(correo)
