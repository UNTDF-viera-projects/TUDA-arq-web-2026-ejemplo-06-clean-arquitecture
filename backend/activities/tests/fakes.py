"""Adaptadores de prueba: implementan los puertos sin base de datos."""

from contextlib import nullcontext
from datetime import datetime, timezone

from ..domain.errores import ActividadNoEncontrada
from ..domain.modelos import Actividad, Inscripcion


class RepositorioEnMemoria:
    def __init__(self, actividades=()):
        self.actividades = {actividad.id: actividad for actividad in actividades}
        self.inscripciones: list[Inscripcion] = []

    def transaccion(self):
        return nullcontext()

    def obtener_actividad_para_inscribir(self, actividad_id):
        try:
            actividad = self.actividades[actividad_id]
        except KeyError as error:
            raise ActividadNoEncontrada() from error
        inscriptos = sum(1 for i in self.inscripciones if i.actividad_id == actividad_id)
        return Actividad(
            id=actividad.id,
            titulo=actividad.titulo,
            inicia_en=actividad.inicia_en,
            capacidad=actividad.capacidad,
            inscriptos=inscriptos,
        )

    def buscar_inscripcion(self, participante_id, actividad_id):
        for inscripcion in self.inscripciones:
            if (inscripcion.participante_id, inscripcion.actividad_id) == (
                participante_id,
                actividad_id,
            ):
                return inscripcion
        return None

    def crear_inscripcion(self, participante_id, actividad_id):
        inscripcion = Inscripcion(
            participante_id=participante_id,
            actividad_id=actividad_id,
            creada_en=datetime.now(timezone.utc),
        )
        self.inscripciones.append(inscripcion)
        return inscripcion
