from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail

from ...application.dto import ConfirmacionInscripcion
from ...application.puertos import ErrorNotificacion


class NotificadorSMTP:
    """Implementa el puerto Notificador con el correo de Django (Mailpit en desarrollo)."""

    def enviar(self, confirmacion: ConfirmacionInscripcion) -> None:
        asunto = f"Inscripción confirmada: {confirmacion.actividad}"
        cuerpo = (
            f"Hola {confirmacion.nombre},\n\n"
            f"Tu inscripción a «{confirmacion.actividad}» quedó confirmada.\n"
            f"Inicio: {confirmacion.inicia_en.isoformat()}\n\n"
            "Arquitecturas Web — UNTDF\n"
        )
        try:
            send_mail(
                asunto,
                cuerpo,
                settings.DEFAULT_FROM_EMAIL,
                [confirmacion.destinatario],
                fail_silently=False,
            )
        except (SMTPException, OSError) as error:
            raise ErrorNotificacion(str(error)) from error
