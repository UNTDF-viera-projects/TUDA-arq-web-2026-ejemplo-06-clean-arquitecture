"""Detalle interno del módulo: cómo se envía. Nadie de afuera lo importa."""

from smtplib import SMTPException

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail

from .tipos import Correo, ErrorDeEnvio


class CanalSMTP:
    def enviar(self, correo: Correo) -> None:
        try:
            send_mail(
                correo.asunto,
                correo.cuerpo,
                settings.DEFAULT_FROM_EMAIL,
                [correo.destinatario],
                fail_silently=False,
            )
        except (SMTPException, OSError) as error:
            raise ErrorDeEnvio(str(error)) from error


class CanalMemoria:
    def __init__(self):
        self.enviados: list[Correo] = []

    def enviar(self, correo: Correo) -> None:
        self.enviados.append(correo)


class CanalFallo:
    def enviar(self, correo: Correo) -> None:
        raise ErrorDeEnvio("Fallo simulado")


memoria = CanalMemoria()
CANALES = {"smtp": CanalSMTP(), "memoria": memoria, "fallo": CanalFallo()}


def canal_configurado():
    try:
        return CANALES[settings.NOTIFICADOR]
    except KeyError as error:
        opciones = ", ".join(CANALES)
        raise ImproperlyConfigured(
            f"NOTIFICADOR={settings.NOTIFICADOR!r} no existe. Opciones: {opciones}"
        ) from error
