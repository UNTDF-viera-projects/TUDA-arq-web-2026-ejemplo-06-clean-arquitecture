from .errores import CupoAgotado
from .modelos import Actividad


def hay_cupo(actividad: Actividad) -> bool:
    return actividad.inscriptos < actividad.capacidad


def exigir_cupo(actividad: Actividad) -> None:
    if not hay_cupo(actividad):
        raise CupoAgotado()
