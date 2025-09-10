from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from smtplib import SMTPException
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import F
from .forms import CustomUserCreationForm, ComedorForm
from .models import UserProfile, Comedor
from .utils import enviar_codigo, start_cooldown, cooldown_remaining, can_reenviar_now, mark_reenviado

import hmac

SESSION_KEY = "pending_registration"
WINDOW_MIN = getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15)
MAX_TRIES  = getattr(settings, "VERIFICATION_MAX_TRIES", 3)

import logging
logger = logging.getLogger(__name__)

def home(request):
    logger.info('Entrando a la vista home')
    try:
        comedores_count = Comedor.objects.count()
        total_capacity = Comedor.objects.aggregate(total=models.Sum('capacidad'))['total'] or 0
        barrios_count = Comedor.objects.values('barrio').distinct().count()
        tipos_count = Comedor.objects.values('tipo').distinct().count()
        comedores_recientes = Comedor.objects.all().order_by('-id')[:6]
        logger.info(f"Comedores: {comedores_count}, Capacidad: {total_capacity}")
    except Exception as e:
        logger.error(f"Error en vista home: {e}")
        comedores_count = 0
        total_capacity = 0
        barrios_count = 0
        tipos_count = 0
        comedores_recientes = []
    context = {
        'comedores_count': comedores_count,
        'total_capacity': total_capacity,
        'barrios_count': barrios_count,
        'tipos_count': tipos_count,
        'comedores_recientes': comedores_recientes,
    }
    logger.info('Renderizando template core/home.html')
    return render(request, 'core/home.html', context)

@login_required
def privada(request):
    # Obtener estadísticas reales de comedores
    comedores_count = Comedor.objects.count()
    total_capacity = Comedor.objects.aggregate(total=models.Sum('capacidad'))['total'] or 0
    barrios_count = Comedor.objects.values('barrio').distinct().count()
    tipos_count = Comedor.objects.values('tipo').distinct().count()
    
    # Obtener comedores recientes para mostrar en el dashboard
    comedores_recientes = Comedor.objects.all().order_by('-id')[:10]
    
    context = {
        'comedores_count': comedores_count,
        'total_capacity': total_capacity,
        'barrios_count': barrios_count,
        'tipos_count': tipos_count,
        'comedores_recientes': comedores_recientes,
    }
    return render(request, 'core/privada.html', context)

def activate_account(request, token):
    """
    Activar cuenta de usuario mediante token de email
    """
    try:
        profile = UserProfile.objects.get(activation_token=token)
        if not profile.email_verified:
            profile.email_verified = True
            profile.user.is_active = True
            profile.user.save()
            profile.save()
            messages.success(request, '¡Cuenta activada exitosamente! Ya puedes iniciar sesión.')
        else:
            messages.info(request, 'Esta cuenta ya está activada.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Token de activación inválido.')

    return redirect('login')

# Vista para crear comedor
@login_required
def crear_comedor(request):
    if request.method == 'POST':
        form = ComedorForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar el comedor
            comedor = form.save()

            # Log de imagen subida
            if comedor.imagen:
                logger.info("Image uploaded: %s -> %s", comedor.imagen.name, comedor.imagen.url)

            return redirect('core:listar_comedores')
    else:
        form = ComedorForm()
    return render(request, 'core/crear_comedor.html', {'form': form})

# Vista para listar comedores con filtros
def listar_comedores(request):
    barrio = request.GET.get('barrio', '')
    tipo = request.GET.get('tipo', '')
    capacidad = request.GET.get('capacidad', '')
    comedores = Comedor.objects.all()
    if barrio:
        comedores = comedores.filter(barrio__icontains=barrio)
    if tipo:
        comedores = comedores.filter(tipo__icontains=tipo)
    if capacidad:
        try:
            comedores = comedores.filter(capacidad__gte=int(capacidad))
        except ValueError:
            pass
    return render(request, 'core/listar_comedores.html', {
        'comedores': comedores,
        'barrio': barrio,
        'tipo': tipo,
        'capacidad': capacidad
    })

# Vista para detalle de comedor
def detalle_comedor(request, pk):
    comedor = get_object_or_404(Comedor, pk=pk)

    # Log de visualización
    if comedor.imagen:
        print(f"Viewing comedor: {comedor.nombre} - Image: {comedor.imagen.url}")

    return render(request, 'core/detalle_comedor.html', {'comedor': comedor})

from django.contrib.auth import authenticate


def registro(request):
    """
        Registro con solo dos casos:
        1) Si email y username NO existen -> crea usuario, genera código y envía mail.
        2) Si email O username existen -> devuelve error correspondiente (sin reenviar código).
    """
    next_url = request.GET.get('next', '')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = (form.cleaned_data["username"] or "").strip()
            email = (form.cleaned_data["email"] or "").strip().lower()
            raw_password = form.cleaned_data["password1"]

            # 1) Validar email (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                logger.warning("[registro] Email en uso: %s", email)
                messages.error(request, "El correo ingresado ya se encuentra registrado.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            # 2) Validar username (case-insensitive)
            if User.objects.filter(username__iexact=username).exists():
                logger.warning("[registro] Username en uso: %s", username)
                messages.error(request, "El nombre de usuario ingresado ya se encuentra en uso.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            # 3) Crear usuario y perfil (pendiente de verificación) y se envia el código
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=raw_password,
                        is_active=True,
                    )
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.set_new_code(minutes=settings.VERIFICATION_WINDOW_MINUTES)
                    profile.email_verified = False
                    profile.save(update_fields=[
                        "email_verification_code", "verification_expires_at",
                        "verification_tries", "email_verified"
                    ])
            except IntegrityError:
                # Airbag contra condiciones de carrera (entre exists() y create_user)
                logger.exception("[registro] Conflicto de unicidad creando usuario: email=%s username=%s", email, username)
                messages.error(request, "No se pudo crear la cuenta porque los datos ya están en uso.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            try:
                enviar_codigo(email, profile.email_verification_code, minutos=settings.VERIFICATION_WINDOW_MINUTES)
                messages.success(request, "Cuenta creada. Te enviamos un código para verificar tu correo.")
                return redirect('core:verificar_email')
            except SMTPException:
                logger.exception("[registro] Falló el envío de verificación a %s", email)
                messages.error(request, "No pudimos enviar el email de verificación. Intentá más tarde.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})
        else:
            logger.warning("[registro] form inválido: %s", form.errors.as_json())
            messages.error(request, "Revisá los datos del formulario.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

def verificar_email(request):
    if request.method == "POST":
        email = (request.POST.get('email') or "").strip().lower()
        code_in = (request.POST.get('code') or "").strip()

        if not email or not code_in:
            messages.error(request, "Completá email y código.")
            return render(request, 'registration/verificar_email.html')

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .filter(email__iexact=email)
                    .first()
                )
                if not user:
                    messages.error(request, "No existe una cuenta con ese correo.")
                    return render(request, 'registration/verificar_email.html')

                profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

                if profile.email_verified:
                    messages.info(request, "Tu correo ya está verificado. Podés iniciar sesión.")
                    return redirect('login')

                now = timezone.now()

                # Expirado
                if not profile.verification_expires_at or now > profile.verification_expires_at:
                    messages.error(request, "El código expiró. Podés solicitar uno nuevo.")
                    return render(request, 'registration/verificar_email.html')

                # Código incorrecto
                if not _code_is_valid(profile.email_verification_code, code_in):
                    profile.verification_tries = F("verification_tries") + 1
                    profile.save(update_fields=["verification_tries"])
                    profile.refresh_from_db(fields=["verification_tries"])

                    if profile.verification_tries >= MAX_TRIES:
                        # Se superó el máximo → resetear y activar cooldown de 60s
                        profile.verification_tries = 0
                        profile.save(update_fields=["verification_tries"])
                        start_cooldown(email)
                        messages.error(
                            request,
                            "Superaste el número de intentos. Esperá 1 minuto y luego podés reenviar un nuevo código."
                        )
                        return render(request, 'registration/verificar_email.html')

                    restantes = MAX_TRIES - profile.verification_tries
                    messages.error(request, f"Código incorrecto. Te quedan {restantes} intento(s).")
                    return render(request, 'registration/verificar_email.html')

                # Éxito
                profile.email_verified = True
                profile.email_verification_code = None
                profile.verification_expires_at = None
                profile.verification_tries = 0
                profile.save(update_fields=[
                    "email_verified", "email_verification_code",
                    "verification_expires_at", "verification_tries"
                ])

            messages.success(request, "¡Email verificado correctamente! Ya podés iniciar sesión.")
            return redirect('login')

        except Exception as e:
            logger.exception("[verificar_email] Error general: %s", e)
            messages.error(request, "Ocurrió un error. Probá de nuevo más tarde.")
            return render(request, 'registration/verificar_email.html')

    # GET
    return render(request, 'registration/verificar_email.html')

def reenviar_codigo(request):
    if request.method != "POST":
        return redirect('core:verificar_email')

    email = (request.POST.get("email") or "").strip().lower()
    if not email:
        messages.error(request, "Ingresá tu correo.")
        return redirect('core:verificar_email')

    remaining_cd = cooldown_remaining(email)
    if remaining_cd > 0:
        messages.error(request, f"Debés esperar {remaining_cd} segundo(s) antes de reenviar un nuevo código.")
        return redirect('core:verificar_email')

    allowed, remaining_bucket = can_reenviar_now(email)
    if not allowed:
        messages.error(request, f"Alcanzaste el límite de envíos. Esperá {remaining_bucket} segundo(s) para reenviar.")
        return redirect('core:verificar_email')

    try:
        with transaction.atomic():
            user = (
                User.objects
                .select_for_update()
                .filter(email__iexact=email)
                .first()
            )
            if not user:
                messages.error(request, "No existe una cuenta con ese correo.")
                return redirect('core:verificar_email')

            profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

            if profile.email_verified:
                messages.info(request, "Ese correo ya está verificado. Iniciá sesión.")
                return redirect('login')

            # Generar y enviar un nuevo código
            profile.set_new_code(minutes=WINDOW_MIN)
            profile.verification_tries = 0  # limpio intentos al reenviar
            profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])

            enviar_codigo(email, profile.email_verification_code, minutos=WINDOW_MIN)
            mark_reenviado(email)  # cuenta este envío dentro de la ventana

            messages.success(request, "Te enviamos un nuevo código. Revisá tu correo.")

    except Exception as e:
        logger.exception("[reenviar_codigo] Error: %s", e)
        messages.error(request, "No pudimos reenviar el código. Probá más tarde.")

    return redirect('core:verificar_email')

def _code_is_valid(stored: str | None, given: str | None) -> bool:
    return hmac.compare_digest((stored or ""), (given or ""))