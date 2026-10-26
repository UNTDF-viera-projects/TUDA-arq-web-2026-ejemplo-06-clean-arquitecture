import logging
from dataclasses import dataclass

from ..domain.modelos import Actividad, Inscripcion, Participante
from ..domain.reglas import exigir_cupo
from .dto import ConfirmacionInscripcion
from .puertos import ErrorNotificacion, Notificador, RepositorioInscripciones

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoInscripcion:
    inscripcion: Inscripcion
    creada: bool


class Inscribir:
    def __init__(self, repositorio: RepositorioInscripciones, notificador: Notificador):
        self.repositorio = repositorio
        self.notificador = notificador

    def ejecutar(self, participante: Participante, actividad_id) -> ResultadoInscripcion:
        with self.repositorio.transaccion():
            actividad = self.repositorio.obtener_actividad_para_inscribir(actividad_id)

            existente = self.repositorio.buscar_inscripcion(participante.id, actividad.id)
            if existente is not None:
                return ResultadoInscripcion(existente, creada=False)

            exigir_cupo(actividad)
            nueva = self.repositorio.crear_inscripcion(participante.id, actividad.id)

        self._notificar(participante, actividad)
        return ResultadoInscripcion(nueva, creada=True)

    def _notificar(self, participante: Participante, actividad: Actividad):
        if not participante.email:
            logger.warning(
                "No se envió la confirmación: %s no tiene email.", participante.nombre
            )
            return

        confirmacion = ConfirmacionInscripcion(
            destinatario=participante.email,
            nombre=participante.nombre,
            actividad=actividad.titulo,
            inicia_en=actividad.inicia_en,
        )
        try:
            self.notificador.enviar(confirmacion)
        except ErrorNotificacion:
            # La inscripción ya quedó confirmada: el correo se pierde, pero se registra.
            logger.exception("No se pudo enviar la confirmación a %s", participante.email)
