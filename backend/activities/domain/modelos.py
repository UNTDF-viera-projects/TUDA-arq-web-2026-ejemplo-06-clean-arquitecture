"""Entidades del dominio: datos con significado, sin saber cómo se guardan."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Participante:
    id: UUID
    nombre: str
    email: str


@dataclass(frozen=True)
class Actividad:
    id: UUID
    titulo: str
    inicia_en: datetime
    capacidad: int
    inscriptos: int


@dataclass(frozen=True)
class Inscripcion:
    participante_id: UUID
    actividad_id: UUID
    creada_en: datetime
