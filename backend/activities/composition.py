"""Raíz de composición: el único lugar que conoce las implementaciones concretas."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .application.inscribir import Inscribir
from .infrastructure.db.repositorio_django import RepositorioDjango
from .infrastructure.notificaciones.fallo import NotificadorFallo
from .infrastructure.notificaciones.memoria import NotificadorMemoria
from .infrastructure.notificaciones.smtp import NotificadorSMTP

NOTIFICADORES = {
    "smtp": NotificadorSMTP,
    "memoria": NotificadorMemoria,
    "fallo": NotificadorFallo,
}


def construir_notificador():
    try:
        return NOTIFICADORES[settings.NOTIFICADOR]()
    except KeyError as error:
        opciones = ", ".join(NOTIFICADORES)
        raise ImproperlyConfigured(
            f"NOTIFICADOR={settings.NOTIFICADOR!r} no existe. Opciones: {opciones}"
        ) from error


def construir_inscribir() -> Inscribir:
    return Inscribir(
        repositorio=RepositorioDjango(),
        notificador=construir_notificador(),
    )
