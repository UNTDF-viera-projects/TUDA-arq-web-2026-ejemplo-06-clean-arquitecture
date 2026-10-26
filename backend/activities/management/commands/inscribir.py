"""Adaptador de entrada por consola: el mismo caso de uso que usa la API HTTP."""

from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from activities.composition import construir_inscribir
from activities.domain.errores import ActividadNoEncontrada, CupoAgotado
from activities.presentation.identidad import participante_actual


class Command(BaseCommand):
    help = "Inscribe a un usuario en una actividad."

    def add_arguments(self, parser):
        parser.add_argument("usuario", help="Nombre de usuario, por ejemplo: demo")
        parser.add_argument("actividad_id", type=UUID, help="UUID de la actividad")

    def handle(self, *args, usuario, actividad_id, **options):
        try:
            user = get_user_model().objects.get(username=usuario)
        except get_user_model().DoesNotExist as error:
            raise CommandError(f"El usuario {usuario!r} no existe.") from error

        try:
            resultado = construir_inscribir().ejecutar(
                participante_actual(user), actividad_id
            )
        except ActividadNoEncontrada as error:
            raise CommandError("La actividad no existe.") from error
        except CupoAgotado as error:
            raise CommandError("No hay cupos disponibles.") from error

        if resultado.creada:
            self.stdout.write(self.style.SUCCESS("Inscripción creada."))
        else:
            self.stdout.write("Ya estaba inscripto: no se cambió nada.")
