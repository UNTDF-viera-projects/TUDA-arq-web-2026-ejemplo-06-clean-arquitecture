"""Raíz de composición: el único lugar que conoce las implementaciones concretas."""

from .application.inscribir import Inscribir
from .infrastructure.db.repositorio_django import RepositorioDjango
from .infrastructure.notificaciones.modulo import NotificadorModulo


def construir_inscribir() -> Inscribir:
    # El canal (smtp, memoria o fallo) ahora lo elige el módulo notificaciones.
    return Inscribir(
        repositorio=RepositorioDjango(),
        notificador=NotificadorModulo(),
    )
