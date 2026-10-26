from .errores import CupoAgotado


def hay_cupo(capacidad: int, inscriptos: int) -> bool:
    return inscriptos < capacidad


def exigir_cupo(capacidad: int, inscriptos: int) -> None:
    if not hay_cupo(capacidad, inscriptos):
        raise CupoAgotado()
