import logging
from dataclasses import dataclass

from django.db import transaction

from ..domain.errores import ActividadNoEncontrada
from ..domain.reglas import exigir_cupo
from ..models import Activity, Enrollment
from .dto import ConfirmacionInscripcion
from .puertos import ErrorNotificacion, Notificador

logger = logging.getLogger(__name__)


@dataclass
class ResultadoInscripcion:
    inscripcion: Enrollment
    creada: bool


class Inscribir:
    def __init__(self, notificador: Notificador):
        self.notificador = notificador

    def ejecutar(self, participante, actividad_id) -> ResultadoInscripcion:
        with transaction.atomic():
            try:
                actividad = Activity.objects.select_for_update().get(id=actividad_id)
            except Activity.DoesNotExist as error:
                raise ActividadNoEncontrada() from error

            inscripcion = Enrollment.objects.filter(
                participant=participante,
                activity=actividad,
            ).first()
            if inscripcion is not None:
                return ResultadoInscripcion(inscripcion, creada=False)

            exigir_cupo(actividad.capacity, actividad.enrollments.count())

            inscripcion = Enrollment.objects.create(
                participant=participante,
                activity=actividad,
            )

        self._notificar(participante.user, actividad)
        return ResultadoInscripcion(inscripcion, creada=True)

    def _notificar(self, usuario, actividad):
        destinatario = (usuario.email or "").strip()
        if not destinatario:
            logger.warning(
                "No se envió la confirmación: %s no tiene email.", usuario.username
            )
            return

        confirmacion = ConfirmacionInscripcion(
            destinatario=destinatario,
            nombre=usuario.get_full_name() or usuario.username,
            actividad=actividad.title,
            inicia_en=actividad.starts_at,
        )
        try:
            self.notificador.enviar(confirmacion)
        except ErrorNotificacion:
            # La inscripción ya quedó confirmada: el correo se pierde, pero se registra.
            logger.exception("No se pudo enviar la confirmación a %s", destinatario)
