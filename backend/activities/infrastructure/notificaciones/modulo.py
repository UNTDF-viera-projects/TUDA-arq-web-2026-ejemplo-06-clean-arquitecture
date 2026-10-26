from notificaciones import api as notificaciones

from ...application.dto import ConfirmacionInscripcion
from ...application.puertos import ErrorNotificacion


class NotificadorModulo:
    """Implementa el puerto Notificador con la interfaz pública del módulo notificaciones.

    Para inscripciones, el otro módulo es un mecanismo más detrás de su puerto.
    """

    def enviar(self, confirmacion: ConfirmacionInscripcion) -> None:
        correo = notificaciones.Correo(
            destinatario=confirmacion.destinatario,
            asunto=f"Inscripción confirmada: {confirmacion.actividad}",
            cuerpo=(
                f"Hola {confirmacion.nombre},\n\n"
                f"Tu inscripción a «{confirmacion.actividad}» quedó confirmada.\n"
                f"Inicio: {confirmacion.inicia_en.isoformat()}\n\n"
                "Arquitecturas Web — UNTDF\n"
            ),
        )
        try:
            notificaciones.enviar(correo)
        except notificaciones.ErrorDeEnvio as error:
            raise ErrorNotificacion(str(error)) from error
