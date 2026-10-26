"""Adaptador de entrada gRPC: traduce el protocolo al caso de uso Inscribir."""

from uuid import UUID

import grpc
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from ...composition import construir_inscribir
from ...domain.errores import ActividadNoEncontrada, CupoAgotado
from ..identidad import participante_actual
from . import inscripciones_pb2, inscripciones_pb2_grpc


class ServicioInscripciones(inscripciones_pb2_grpc.InscripcionesServicer):
    def Inscribir(self, request, context):
        close_old_connections()  # cada llamada corre en un hilo del servidor gRPC
        try:
            usuario = _usuario_autenticado(context)
            try:
                actividad_id = UUID(request.actividad_id)
            except ValueError:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "actividad_id no es un UUID.")

            try:
                resultado = construir_inscribir().ejecutar(
                    participante_actual(usuario), actividad_id
                )
            except ActividadNoEncontrada:
                context.abort(grpc.StatusCode.NOT_FOUND, "La actividad no existe.")
            except CupoAgotado:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, "No hay cupos disponibles.")

            inscripcion = resultado.inscripcion
            return inscripciones_pb2.InscribirResponse(
                actividad_id=str(inscripcion.actividad_id),
                participante_id=str(inscripcion.participante_id),
                inscripta_en=inscripcion.creada_en.isoformat(),
                creada=resultado.creada,
            )
        finally:
            close_old_connections()


def _usuario_autenticado(context):
    """Misma identidad que la API HTTP: el access JWT, pero en la metadata."""
    metadata = dict(context.invocation_metadata())
    esquema, _, token = metadata.get("authorization", "").partition(" ")
    if esquema != "Bearer" or not token:
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Falta el token Bearer.")
    try:
        user_id = AccessToken(token)["user_id"]
        return get_user_model().objects.get(id=user_id, is_active=True)
    except (TokenError, KeyError, get_user_model().DoesNotExist):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token inválido.")
