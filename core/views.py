from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models

from datetime import timedelta
import secrets
import time
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings

from .forms import CustomUserCreationForm, ComedorForm
from .models import UserProfile, Comedor
from .utils import generar_codigo, enviar_codigo, expira_en

SESSION_KEY = "pending_registration"

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
        Alta con estado 'pendiente de verificación'.
        - email libre -> crea usuario + genera código + envía
        - email existe y verificado -> error
        - email existe y PENDIENTE -> reenvía código y redirige a verificar
    """
    next_url = request.GET.get('next', '')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            raw_password = form.cleaned_data["password1"]

            # Primero validamos mail y estado
            existing_by_mail = User.objects.filter(email__iexact=email).first()
            if existing_by_mail:
                profile = existing_by_mail.userprofile
                if profile.email_verified:
                    # correo ya tomado y verificado
                    logger.warning("El correo que desea ingresar ya se encuentra en uso")
                    messages.error(request, "Ese correo ya está registrado y verificado.")
                    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

                # correo existente PERO pendiente de validar --> reenviar el codigo y no crear otro usuario
                profile.set_new_code(minutes=settings.VERIFICATION_WINDOW_MINUTES)
                profile.save(update_fields=["email_verification_code","verification_expires_at","verification_tries"])
                try:
                    enviar_codigo(existing_by_mail.email, profile.email_verification_code,
                                  minutos=settings.VERIFICATION_WINDOW_MINUTES)
                    messages.info(request, "Ese correo ya estaba registrado pero pendiente. Te reenviamos el código.")
                    return redirect('core:verificar_email')
                except Exception as e:
                    logger.exception("Error reenviando código a %s: %s", email, e)
                    messages.error(request, "No pudimos reenviar el código. Probá más tarde.")
                    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            # 2) Si el mail esta libre, recien ahora validar USERNAME
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, "El nombre de usuario ingresado ya se encuentra en uso.")
                logger.warning("[registro] El nombre de usuario ingresado ya se encuentra en uso. %s", username)
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            #3) Crear usuario 'pendiente' y enviar codigo
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

            try:
                enviar_codigo(email, profile.email_verification_code, minutos=settings.VERIFICATION_WINDOW_MINUTES)
                messages.success(request, "Cuenta creada. Te enviamos un código para verificar tu correo.")
                return redirect('core:verificar_email')
            except SMTPException:
                logger.exception("[registro] SMTPException enviando a %s", email)
                messages.error(request, "No pudimos enviar el email de verificación. Intentá más tarde.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})
        else:
            logger.warning("[registro] form inválido: %s", form.errors.as_json())
            messages.error(request, "Revisá los datos del formulario.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})


def verificar_email(request):
    """
    Paso 2: valida email + código contra UserProfile.
    - Si expiró => genera y reenvía uno nuevo.
    - Si supera el límite de intentos => genera y reenvía uno nuevo.
    - Si es correcto => marca email_verified=True (y opcionalmente user.is_active=True).
    """
    if request.method == "POST":
        email = (request.POST.get('email') or "").strip()
        code_in = (request.POST.get('code') or "").strip()

        if not email or not code_in:
            messages.error(request, "Completá email y código.")
            return render(request, 'registration/verificar_email.html')

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, "No existe una cuenta con ese correo.")
            return render(request, 'registration/verificar_email.html')

        # Asegura perfil (por si faltara para algún usuario viejo)
        profile, _ = UserProfile.objects.get_or_create(user=user)

        if profile.email_verified:
            messages.info(request, "Tu correo ya está verificado. Podés iniciar sesión.")
            return redirect('login')

        # 1) Código vencido -> regenerar y reenviar
        if not profile.verification_expires_at or timezone.now() > profile.verification_expires_at:
            messages.error(request, "El código expiró. Te enviamos uno nuevo.")
            profile.set_new_code(minutes=getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15))
            profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])
            try:
                enviar_codigo(email, profile.email_verification_code, minutos=getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15))
            except Exception as e:
                logger.exception("[verificar_email] Error reenviando código vencido a %s: %s", email, e)
                messages.error(request, "No pudimos reenviar el código. Probá más tarde.")
            return redirect('core:verificar_email')

        # 2) Límite de intentos
        max_tries = getattr(settings, "VERIFICATION_MAX_TRIES", 5)
        if profile.verification_tries >= max_tries:
            messages.error(request, "Demasiados intentos fallidos. Te enviamos un nuevo código.")
            profile.set_new_code(minutes=getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15))
            profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])
            try:
                enviar_codigo(email, profile.email_verification_code, minutos=getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15))
            except Exception as e:
                logger.exception("[verificar_email] Error reenviando tras superar intentos a %s: %s", email, e)
                messages.error(request, "No pudimos reenviar el código. Probá más tarde.")
            return redirect('core:verificar_email')

        # 3) Validar código
        if not profile.code_is_valid(code_in):
            profile.verification_tries += 1
            profile.save(update_fields=["verification_tries"])
            restantes = max_tries - profile.verification_tries
            if restantes <= 0:
                messages.error(request, "Demasiados intentos fallidos. Te enviamos un nuevo código.")
                profile.set_new_code(minutes=getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15))
                profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])
                try:
                    enviar_codigo(email, profile.email_verification_code, minutos=getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15))
                except Exception as e:
                    logger.exception("[verificar_email] Error reenviando nuevo código a %s: %s", email, e)
                    messages.error(request, "No pudimos reenviar el código. Probá más tarde.")
                return redirect('core:verificar_email')

            messages.error(request, f"Código incorrecto. Te quedan {restantes} intento(s).")
            return render(request, 'registration/verificar_email.html')

        # 4) Éxito: marcar verificado (+ opcional activar user)
        with transaction.atomic():
            profile.email_verified = True
            profile.email_verification_code = None
            profile.verification_expires_at = None
            profile.verification_tries = 0
            profile.save(update_fields=["email_verified", "email_verification_code", "verification_expires_at", "verification_tries"])

            # Si preferís bloquear login hasta verificar:
            # user.is_active = True
            # user.save(update_fields=["is_active"])

        messages.success(request, "¡Email verificado correctamente! Ya podés iniciar sesión.")
        return redirect('login')

    # GET
    return render(request, 'registration/verificar_email.html')


def reenviar_verificacion(request):
    email = (request.POST.get('email') or request.GET.get('email') or "").strip()
    if not email:
        messages.error(request, "Indicá el correo con el que te registraste.")
        return redirect('core:verificar_email')

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        messages.error(request, "No encontramos una cuenta con ese correo.")
        return redirect('core:registro')

    profile = user.userprofile
    if profile.email_verified:
        messages.info(request, "Ese correo ya está verificado. Iniciá sesión.")
        return redirect('login')

    profile.set_new_code(minutes=settings.VERIFICATION_WINDOW_MINUTES)
    profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])

    try:
        enviar_codigo(email, profile.email_verification_code, minutos=settings.VERIFICATION_WINDOW_MINUTES)
        messages.success(request, "Te reenviamos el código a tu correo.")
    except Exception:
        messages.error(request, "No pudimos reenviar el código. Probá más tarde.")
    return redirect('core:verificar_email')