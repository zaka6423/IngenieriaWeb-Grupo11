# core/utils.py
import secrets
import time

from django.core.cache import cache
from django.conf import settings

EMAIL_SUBJECT_VERIFICATION = "Comedores Comunitarios – Verificación de correo electrónico"
COOLDOWN_S = getattr(settings, "VERIFICATION_RESEND_COOLDOWN_SECONDS", 60)
RESEND_WINDOW_S = getattr(settings, "VERIFICATION_RESEND_WINDOW_SECONDS", 60)
RESEND_MAX_NO_WAIT = getattr(settings, "VERIFICATION_RESEND_MAX_NO_WAIT", 3)

def generar_codigo():
    return f"{secrets.randbelow(10**6):06d}"

def _cooldown_key(email: str) -> str:
    return f"verify_cd:{email}"

def start_cooldown(email: str) -> None:
    """Inicia cooldown. Esto evita spam al enviar codigo"""
    if COOLDOWN_S > 0:
        cache.add(_cooldown_key(email), int(time.time()), timeout=COOLDOWN_S)

def cooldown_remaining(email: str) -> int:
    """
    Devuelve segundos restantes del cooldown, o 0 si no hay.
    """
    if COOLDOWN_S <= 0:
        return 0
    ts = cache.get(_cooldown_key(email))
    if ts is None:
        return 0
    elapsed = int(time.time()) - int(ts)
    remaining = COOLDOWN_S - elapsed
    return remaining if remaining > 0 else 0

def _resend_bucket_key(email: str) -> str:
    return f"verify_resend_bucket:{email}"

def can_reenviar_now(email: str) -> tuple[bool, int]:
    """
    Devuelve (permitido, remaining_seconds_si_no).
    Permite 2 reenvíos "free" por ventana de 60s; el 3º requiere esperar a que venza la ventana.
    """
    key = _resend_bucket_key(email)
    data = cache.get(key)
    now = int(time.time())

    if not data:
        # (count, window_start)
        cache.set(key, (0, now), timeout=RESEND_WINDOW_S)
        data = (0, now)

    count, window_start = data

    # si la ventana ya venció, resetea
    if now - window_start >= RESEND_WINDOW_S:
        cache.set(key, (0, now), timeout=RESEND_WINDOW_S)
        count, window_start = 0, now

    if count >= RESEND_MAX_NO_WAIT:
        # bloqueado hasta que termine la ventana
        remaining = RESEND_WINDOW_S - (now - window_start)
        return (False, remaining if remaining > 0 else 0)

    return (True, 0)

def mark_reenviado(email: str) -> None:
    """Incrementa el contador dentro de la ventana."""
    key = _resend_bucket_key(email)
    data = cache.get(key)
    now = int(time.time())
    if not data:
        cache.set(key, (1, now), timeout=RESEND_WINDOW_S)
        return
    count, window_start = data
    if now - window_start >= RESEND_WINDOW_S:
        cache.set(key, (1, now), timeout=RESEND_WINDOW_S)
    else:
        cache.set(key, (count + 1, window_start), timeout=RESEND_WINDOW_S)
