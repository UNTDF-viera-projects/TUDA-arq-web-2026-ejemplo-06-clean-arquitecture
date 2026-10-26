import logging
from dataclasses import dataclass

from django.db import transaction

from ..domain.errores import ActividadNoEncontrada
from ..domain.modelos import Actividad, Inscripcion, Participante
from ..domain.reglas import exigir_cupo
from ..models import Activity, Enrollment
from .dto import ConfirmacionInscripcion
from .puertos import ErrorNotificacion, Notificador

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoInscripcion:
    inscripcion: Inscripcion
    creada: bool


class Inscribir:
    def __init__(self, notificador: Notificador):
        self.notificador = notificador

    def ejecutar(self, participante: Participante, actividad_id) -> ResultadoInscripcion:
        with transaction.atomic():
            try:
                fila = Activity.objects.select_for_update().get(id=actividad_id)
            except Activity.DoesNotExist as error:
                raise ActividadNoEncontrada() from error
            # Traducir del ORM al dominio: todavía lo hace el caso de uso.
            actividad = Actividad(
                id=fila.id,
                titulo=fila.title,
                inicia_en=fila.starts_at,
                capacidad=fila.capacity,
                inscriptos=fila.enrollments.count(),
            )

            existente = Enrollment.objects.filter(
                participant_id=participante.id,
                activity_id=actividad.id,
            ).first()
            if existente is not None:
                return ResultadoInscripcion(_a_inscripcion(existente), creada=False)

            exigir_cupo(actividad)

            nueva = Enrollment.objects.create(
                participant_id=participante.id,
                activity_id=actividad.id,
            )

        self._notificar(participante, actividad)
        return ResultadoInscripcion(_a_inscripcion(nueva), creada=True)

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


def _a_inscripcion(fila: Enrollment) -> Inscripcion:
    return Inscripcion(
        participante_id=fila.participant_id,
        actividad_id=fila.activity_id,
        creada_en=fila.enrolled_at,
    )
