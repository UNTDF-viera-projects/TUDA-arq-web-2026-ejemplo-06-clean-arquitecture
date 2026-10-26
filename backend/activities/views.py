from uuid import UUID

from django.db.models import Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .application.errores import ActividadNoEncontrada, CupoAgotado
from .application.inscribir import inscribir
from .models import Activity, Enrollment, Participant
from .serializers import (
    ActivityOutSerializer,
    EnrollmentOutSerializer,
    ErrorOutSerializer,
)


ACTIVITY_NOT_FOUND = {
    "code": "activity_not_found",
    "message": "La actividad no existe.",
}
CAPACITY_EXHAUSTED = {
    "code": "capacity_exhausted",
    "message": "No hay cupos disponibles.",
}
INVALID_REQUEST = {
    "code": "invalid_request",
    "message": "PUT no recibe un body en esta versión.",
}
REQUEST_NOT_VALID = {
    "code": "invalid_request",
    "message": "Los parámetros del request no son válidos.",
}

ACTIVITY_ID_PARAMETER = OpenApiParameter(
    name="activity_id",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    required=True,
    description="Identificador único de la actividad.",
)
METHOD_NOT_ALLOWED = OpenApiResponse(description="Método no permitido.")
NO_CONTENT = OpenApiResponse(description="Inscripción cancelada.")
UNAUTHORIZED = OpenApiResponse(description="Credenciales ausentes o JWT inválido.")


def current_participant(user):
    participant, _ = Participant.objects.get_or_create(
        user=user,
        defaults={"name": user.get_full_name() or user.username},
    )
    return participant


def parse_activity_id(activity_id):
    try:
        return UUID(activity_id)
    except (TypeError, ValueError):
        return None

class ActivityListView(APIView):
    @extend_schema(
        operation_id="listActivities",
        summary="Listar actividades",
        description="Devuelve todas las actividades ordenadas por fecha de inicio.",
        tags=["Activities"],
        responses={
            200: ActivityOutSerializer(many=True),
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        activities = Activity.objects.annotate(
            enrolled_count=Count("enrollments")
        ).order_by("starts_at")
        serializer = ActivityOutSerializer(activities, many=True)
        return Response(serializer.data)


class ActivityDetailView(APIView):
    @extend_schema(
        operation_id="getActivity",
        summary="Consultar una actividad",
        description="Recupera una actividad concreta a partir de su UUID.",
        tags=["Activities"],
        parameters=[ACTIVITY_ID_PARAMETER],
        responses={
            200: ActivityOutSerializer,
            400: ErrorOutSerializer,
            404: ErrorOutSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request, activity_id):
        activity_id = parse_activity_id(activity_id)
        if activity_id is None:
            return Response(REQUEST_NOT_VALID, status=status.HTTP_400_BAD_REQUEST)

        try:
            activity = Activity.objects.annotate(
                enrolled_count=Count("enrollments")
            ).get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(ACTIVITY_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        return Response(ActivityOutSerializer(activity).data)


class EnrollmentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="listMyEnrollments",
        summary="Listar mis inscripciones",
        description=(
            "Lista las inscripciones del participante asociado al usuario "
            "autenticado. Devuelve una colección vacía si no tiene inscripciones."
        ),
        tags=["Enrollments"],
        responses={
            200: EnrollmentOutSerializer(many=True),
            401: UNAUTHORIZED,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        participant = current_participant(request.user)
        enrollments = Enrollment.objects.filter(participant=participant).order_by(
            "enrolled_at"
        )
        serializer = EnrollmentOutSerializer(enrollments, many=True)
        return Response(serializer.data)


class EnrollmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="putMyEnrollment",
        summary="Inscribirme en una actividad",
        description=(
            "Crea una inscripción sin body. Responde 201 si la crea y 200 con la "
            "inscripción existente si se repite el mismo PUT."
        ),
        tags=["Enrollments"],
        parameters=[ACTIVITY_ID_PARAMETER],
        request=None,
        responses={
            200: EnrollmentOutSerializer,
            201: EnrollmentOutSerializer,
            400: ErrorOutSerializer,
            401: UNAUTHORIZED,
            404: ErrorOutSerializer,
            409: ErrorOutSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def put(self, request, activity_id):
        activity_id = parse_activity_id(activity_id)
        if activity_id is None:
            return Response(REQUEST_NOT_VALID, status=status.HTTP_400_BAD_REQUEST)

        participant = current_participant(request.user)
        if request.body:
            return Response(INVALID_REQUEST, status=status.HTTP_400_BAD_REQUEST)

        try:
            resultado = inscribir(participant, activity_id)
        except ActividadNoEncontrada:
            return Response(ACTIVITY_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        except CupoAgotado:
            return Response(CAPACITY_EXHAUSTED, status=status.HTTP_409_CONFLICT)

        status_code = (
            status.HTTP_201_CREATED if resultado.creada else status.HTTP_200_OK
        )
        return Response(
            EnrollmentOutSerializer(resultado.inscripcion).data,
            status=status_code,
        )

    @extend_schema(
        operation_id="deleteMyEnrollment",
        summary="Cancelar mi inscripción",
        description=(
            "Elimina la inscripción del participante y libera el cupo. "
            "La operación es idempotente y responde siempre 204 si la actividad "
            "existe."
        ),
        tags=["Enrollments"],
        parameters=[ACTIVITY_ID_PARAMETER],
        responses={
            204: NO_CONTENT,
            400: ErrorOutSerializer,
            401: UNAUTHORIZED,
            404: ErrorOutSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def delete(self, request, activity_id):
        activity_id = parse_activity_id(activity_id)
        if activity_id is None:
            return Response(REQUEST_NOT_VALID, status=status.HTTP_400_BAD_REQUEST)

        participant = current_participant(request.user)

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(ACTIVITY_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        Enrollment.objects.filter(
            participant=participant,
            activity=activity,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
