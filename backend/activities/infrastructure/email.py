import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_enrollment_confirmation(user, activity):
    recipient = (getattr(user, "email", None) or "").strip()
    if not recipient:
        logger.warning(
            "No se envió email de inscripción: el usuario %s no tiene email.",
            getattr(user, "username", user),
        )
        return

    subject = f"Inscripción confirmada: {activity.title}"
    body = (
        f"Hola {user.get_full_name() or user.username},\n\n"
        f"Tu inscripción a «{activity.title}» quedó confirmada.\n"
        f"Inicio: {activity.starts_at.isoformat()}\n\n"
        "Arquitecturas Web — UNTDF\n"
    )
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "No se pudo enviar el email de inscripción a %s",
            recipient,
        )
