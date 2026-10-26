from django.db import transaction

from ...domain.errores import ActividadNoEncontrada
from ...domain.modelos import Actividad, Inscripcion
from ...models import Activity, Enrollment


class RepositorioDjango:
    """Implementa RepositorioInscripciones con el ORM de Django."""

    def transaccion(self):
        return transaction.atomic()

    def obtener_actividad_para_inscribir(self, actividad_id):
        try:
            fila = Activity.objects.select_for_update().get(id=actividad_id)
        except Activity.DoesNotExist as error:
            raise ActividadNoEncontrada() from error
        return Actividad(
            id=fila.id,
            titulo=fila.title,
            inicia_en=fila.starts_at,
            capacidad=fila.capacity,
            inscriptos=fila.enrollments.count(),
        )

    def buscar_inscripcion(self, participante_id, actividad_id):
        fila = Enrollment.objects.filter(
            participant_id=participante_id,
            activity_id=actividad_id,
        ).first()
        return None if fila is None else _a_inscripcion(fila)

    def crear_inscripcion(self, participante_id, actividad_id):
        fila = Enrollment.objects.create(
            participant_id=participante_id,
            activity_id=actividad_id,
        )
        return _a_inscripcion(fila)


def _a_inscripcion(fila: Enrollment) -> Inscripcion:
    return Inscripcion(
        participante_id=fila.participant_id,
        actividad_id=fila.activity_id,
        creada_en=fila.enrolled_at,
    )
