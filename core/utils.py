# core/utils.py
import secrets
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

def generar_codigo():
    return f"{secrets.randbelow(10**6):06d}"

def enviar_codigo(email, code, minutos=15):
    subject = "Código de verificación de cuenta"
    message = f"Tu código de verificación es: {code}\nExpira en {minutos} minutos."
    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost"),
        [email],
        fail_silently=False,
    )

def expira_en(minutos):
    return (timezone.now() + timedelta(minutes=minutos)).isoformat()
