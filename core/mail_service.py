# core/mail_service.py
from django.core.mail import send_mail
from django.conf import settings

class EmailService:
    @staticmethod
    def send_email(subject: str, message: str, recipients: list[str]):
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost")
        for recipient in recipients:
            send_mail(
                subject,
                message,
                from_email,
                [recipient],
                fail_silently=False,
            )

    @staticmethod
    def send_verification(email: str, code: str, minutos: int = 15):
        subject = "Comedores Comunitarios – Verificación de correo electrónico"
        message = (
            f"Hola,\n\n"
            f"Gracias por registrarte en Comedores Comunitarios.\n\n"
            f"Para completar tu registro, ingresá el siguiente código: {code}\n\n"
            f"⚠️ Este código vence en {minutos} minutos.\n\n"
            f"Si no solicitaste este registro, podés ignorar este correo.\n\n"
            f"Equipo Comedores Comunitarios"
        )
        EmailService.send_email(subject, message, [email])

    @staticmethod
    def send_new_publication(emails: list[str], comedor_nombre: str, titulo: str):
        subject = f"Nueva publicación en {comedor_nombre}"
        message = (
            f"¡Hola!\n\n"
            f"El comedor {comedor_nombre} realizó una nueva publicación:\n\n"
            f"📰 {titulo}\n\n"
            f"Te avisamos para que estés al tanto.\n\n"
            f"Equipo Comedores Comunitarios"
        )
        EmailService.send_email(subject, message, emails)

    @staticmethod
    def send_new_donation(email: str, comedor_nombre: str, publicacion_titulo: str, donante: str, articulos: list[str]):
        """
        Envía una notificación al dueño del comedor cuando se recibe una nueva donación.
        """
        subject = f"Nueva donación recibida en {comedor_nombre}"

        articulos_txt = "\n".join(f"• {a}" for a in articulos)
        message = (
            f"Hola,\n\n"
            f"Recibiste una nueva donación en tu comedor '{comedor_nombre}'.\n\n"
            f"📦 Publicación: {publicacion_titulo}\n"
            f"🤝 Donante: {donante}\n\n"
            f"🧺 Artículos donados:\n{articulos_txt}\n\n"
            f"¡Gracias por seguir ayudando a la comunidad!\n\n"
            f"Equipo Comedores Comunitarios"
        )

        EmailService.send_email(subject, message, [email])
