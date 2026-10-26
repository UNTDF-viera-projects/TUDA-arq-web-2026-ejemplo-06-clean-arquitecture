from contextlib import AbstractContextManager
from typing import Protocol
from uuid import UUID

from ..domain.modelos import Actividad, Inscripcion
from .dto import ConfirmacionInscripcion


class ErrorNotificacion(Exception):
    """El mecanismo no pudo entregar la confirmación."""


class Notificador(Protocol):
    def enviar(self, confirmacion: ConfirmacionInscripcion) -> None:
        """Entrega la confirmación o lanza ErrorNotificacion."""


class RepositorioInscripciones(Protocol):
    def transaccion(self) -> AbstractContextManager:
        """Agrupa las operaciones siguientes: se confirman todas o ninguna."""

    def obtener_actividad_para_inscribir(self, actividad_id: UUID) -> Actividad:
        """Reserva la actividad hasta el fin de la transacción.

        Lanza ActividadNoEncontrada si no existe.
        """

    def buscar_inscripcion(
        self, participante_id: UUID, actividad_id: UUID
    ) -> Inscripcion | None: ...

    def crear_inscripcion(self, participante_id: UUID, actividad_id: UUID) -> Inscripcion: ...
