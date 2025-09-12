# core/utils.py
import secrets
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

EMAIL_SUBJECT_VERIFICATION = "Comedores Comunitarios – Verificación de correo electrónico"

def generar_codigo():
    return f"{secrets.randbelow(10**6):06d}"

def enviar_codigo(email, code, minutos=15):
    subject = EMAIL_SUBJECT_VERIFICATION
    message = (
        f"Hola,\n\n"
        f"Gracias por registrarte en Comedores Comunitarios.\n\n"
        f"Para completar tu registro, ingresá el siguiente código de verificación: {code}\n\n"
        f"⚠️ Este código vence en {minutos} minutos.\n\n"
        f"Si vos no solicitaste este registro, podés ignorar este correo.\n\n"
        f"Equipo Comedores Comunitarios"
    )

    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost"),
        [email],
        fail_silently=False,
    )

def expira_en(minutos):
    return (timezone.now() + timedelta(minutes=minutos)).isoformat()
