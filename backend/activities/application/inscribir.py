from dataclasses import dataclass

from django.db import transaction

from ..emails import send_enrollment_confirmation
from ..models import Activity, Enrollment


@dataclass
class ResultadoInscripcion:
    # "creada", "existente", "actividad_inexistente" o "sin_cupo"
    estado: str
    inscripcion: Enrollment | None = None


def inscribir(participante, actividad_id):
    with transaction.atomic():
        try:
            actividad = Activity.objects.select_for_update().get(id=actividad_id)
        except Activity.DoesNotExist:
            return ResultadoInscripcion("actividad_inexistente")

        inscripcion = Enrollment.objects.filter(
            participant=participante,
            activity=actividad,
        ).first()
        if inscripcion is not None:
            return ResultadoInscripcion("existente", inscripcion)

        if actividad.enrollments.count() >= actividad.capacity:
            return ResultadoInscripcion("sin_cupo")

        inscripcion = Enrollment.objects.create(
            participant=participante,
            activity=actividad,
        )

    send_enrollment_confirmation(participante.user, actividad)
    return ResultadoInscripcion("creada", inscripcion)
