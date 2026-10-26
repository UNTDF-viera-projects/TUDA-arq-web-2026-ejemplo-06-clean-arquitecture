from dataclasses import dataclass

from django.db import transaction

from ..emails import send_enrollment_confirmation
from ..models import Activity, Enrollment
from ..domain.errores import ActividadNoEncontrada
from ..domain.reglas import exigir_cupo


@dataclass
class ResultadoInscripcion:
    inscripcion: Enrollment
    creada: bool


def inscribir(participante, actividad_id):
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

    send_enrollment_confirmation(participante.user, actividad)
    return ResultadoInscripcion(inscripcion, creada=True)
