from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from . import api, canales

CORREO = api.Correo(destinatario="ada@example.com", asunto="Hola", cuerpo="...")


class ApiDeNotificacionesTests(SimpleTestCase):
    @override_settings(
        NOTIFICADOR="smtp",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_smtp_envia_un_correo(self):
        api.enviar(CORREO)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ada@example.com"])

    @override_settings(NOTIFICADOR="memoria")
    def test_memoria_guarda_el_correo(self):
        canales.memoria.enviados.clear()

        api.enviar(CORREO)

        self.assertEqual(canales.memoria.enviados, [CORREO])

    @override_settings(NOTIFICADOR="fallo")
    def test_fallo_lanza_error_de_envio(self):
        with self.assertRaises(api.ErrorDeEnvio):
            api.enviar(CORREO)

    @override_settings(NOTIFICADOR="paloma")
    def test_canal_desconocido_es_un_error_de_configuracion(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "NOTIFICADOR='paloma'"):
            api.enviar(CORREO)
