from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from smtplib import SMTPException
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.db.models import F
from .utils import enviar_codigo, start_cooldown, cooldown_remaining, can_reenviar_now, mark_reenviado
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.db import models
from core.mail_service import EmailService
from django.contrib.auth.models import User
from functools import wraps
from django.http import JsonResponse
import json
from typing import List
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from haystack.query import SearchQuerySet

from .forms import ComedorForm, CustomUserCreationForm, FavoritoForm, DonacionForm, PublicacionForm, PublicacionArticuloFormSet
from .models import Comedor, UserProfile, Favoritos, Donacion, Publicacion, PublicacionArticulo, DonacionItem

import hmac
import logging

SESSION_KEY = "pending_registration"
WINDOW_MIN = getattr(settings, "VERIFICATION_WINDOW_MINUTES", 15)
MAX_TRIES  = getattr(settings, "VERIFICATION_MAX_TRIES", 3)

logger = logging.getLogger(__name__)

def email_verified_required(view_func):
    """
    Decorador que requiere que el usuario tenga el email verificado
    Si no está verificado, muestra un mensaje y redirige a la página de verificación
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            profile = request.user.userprofile
            if not profile.email_verified:
                messages.warning(request, 'Para realizar esta acción necesitás verificar tu email. Te enviamos un código de verificación.')
                
                # Generar y enviar un nuevo código si no hay uno válido
                try:
                    now = timezone.now()
                    if (not profile.verification_expires_at or 
                        now > profile.verification_expires_at):
                        profile.set_new_code(minutes=WINDOW_MIN)
                        profile.verification_tries = 0
                        profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])
                        enviar_codigo(request.user.email, profile.email_verification_code, minutos=WINDOW_MIN)
                    
                    request.session['verify_email'] = request.user.email
                    return redirect('core:verificar_email')
                except Exception as e:
                    logger.exception("[email_verified_required] Error enviando código: %s", e)
                    messages.error(request, 'No pudimos enviar el código de verificación. Intentá más tarde.')
                    return redirect('core:privada')
        except UserProfile.DoesNotExist:
            # Si no hay perfil, crear uno y requerir verificación
            profile = UserProfile.objects.create(user=request.user)
            profile.set_new_code(minutes=WINDOW_MIN)
            profile.save()
            try:
                enviar_codigo(request.user.email, profile.email_verification_code, minutos=WINDOW_MIN)
                messages.warning(request, 'Para realizar esta acción necesitás verificar tu email. Te enviamos un código de verificación.')
                request.session['verify_email'] = request.user.email
                return redirect('core:verificar_email')
            except Exception as e:
                logger.exception("[email_verified_required] Error enviando código: %s", e)
                messages.error(request, 'No pudimos enviar el código de verificación. Intentá más tarde.')
                return redirect('core:privada')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

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
    """
    Vista del perfil privado del usuario
    """
    comedores_count = Comedor.objects.count()
    total_capacity = Comedor.objects.aggregate(total=models.Sum('capacidad'))['total'] or 0
    barrios_count = Comedor.objects.values('barrio').distinct().count()
    tipos_count = Comedor.objects.values('tipo').distinct().count()
    comedores_recientes = Comedor.objects.all().order_by('-id')[:6]
    
    # Verificar estado de verificación del email
    email_verified = False
    try:
        profile = request.user.userprofile
        email_verified = profile.email_verified
    except UserProfile.DoesNotExist:
        email_verified = False
    
    context = {
        'comedores_count': comedores_count,
        'total_capacity': total_capacity,
        'barrios_count': barrios_count,
        'tipos_count': tipos_count,
        'comedores_recientes': comedores_recientes,
        'email_verified': email_verified,
    }
    return render(request, 'core/privada.html', context)

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
            first_name = (form.cleaned_data["first_name"] or "").strip()
            last_name = (form.cleaned_data["last_name"] or "").strip()
            email = (form.cleaned_data["email"] or "").strip().lower()
            raw_password = form.cleaned_data["password1"]
            
            # Validar email (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                logger.warning("[registro] Email en uso: %s", email)
                messages.error(request, f"El correo '{email}' ya se encuentra registrado. Si ya tenés una cuenta, podés iniciar sesión o usar otro correo.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            # Validar username (case-insensitive)
            if User.objects.filter(username__iexact=username).exists():
                logger.warning("[registro] Username en uso: %s", username)
                messages.error(request, f"El nombre de usuario '{username}' ya se encuentra en uso. Elegí otro nombre de usuario.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            # Crear usuario y perfil (pendiente de verificación)
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
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
                logger.exception("[registro] Conflicto de unicidad creando usuario: email=%s username=%s", email, username)
                messages.error(request, "No se pudo crear la cuenta porque los datos ya están en uso.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            try:
                enviar_codigo(email, profile.email_verification_code, minutos=settings.VERIFICATION_WINDOW_MINUTES)
                messages.success(request, f"¡Cuenta creada exitosamente! Te enviamos un código de verificación a {email}. Revisá tu correo y seguí las instrucciones.")
                request.session['verify_email'] = email
                return redirect('core:verificar_email')
            except SMTPException:
                logger.exception("[registro] Falló el envío de verificación a %s", email)
                messages.error(request, "No pudimos enviar el email de verificación. Verificá que el correo sea correcto e intentá más tarde.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})
        else:
            logger.warning("[registro] form inválido: %s", form.errors.as_json())
            messages.error(request, "Por favor, revisá los datos del formulario y corregí los errores marcados.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})
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
            messages.success(request, f'¡Cuenta activada exitosamente! Bienvenido {profile.user.first_name}, ya puedes iniciar sesión.')
        else:
            messages.info(request, 'Esta cuenta ya está activada. Puedes iniciar sesión normalmente.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Token de activación inválido o expirado. Por favor, solicita un nuevo enlace de activación.')

    return redirect('login')

# Vista para crear comedor
@login_required
@email_verified_required
def crear_comedor(request):
    if request.method == 'POST':
        form = ComedorForm(request.POST, request.FILES)
        if form.is_valid():
            comedor = form.save()

            messages.success(request, f"¡Comedor '{comedor.nombre}' creado exitosamente! Ya está disponible para la comunidad.")
            return redirect('core:listar_comedores')
        else:
            messages.error(request, "Por favor, revisá los datos del formulario y corregí los errores marcados.")
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
    
    # Obtener todas las publicaciones del comedor
    publicaciones = (
        Publicacion.objects
        .filter(id_comedor=comedor)
        .select_related("id_comedor", "id_tipo_publicacion")
        .prefetch_related("publicacionarticulo_set")
        .order_by("-fecha_inicio")
    )

    # Log de visualización
    if comedor.imagen:
        print(f"Viewing comedor: {comedor.nombre} - Image: {comedor.imagen.url}")

    return render(request, 'core/detalle_comedor.html', {
        'comedor': comedor,
        'publicaciones': publicaciones
    })


def custom_login(request):
    """
    Vista personalizada de login - permite login sin verificación de email
    """
    if request.user.is_authenticated:
        return redirect('core:privada')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Intentar autenticación
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    # Hacer login directamente sin verificar email
                    auth_login(request, user)
                    
                    # Verificar si el email está verificado para mostrar mensaje apropiado
                    try:
                        profile = user.userprofile
                        if not profile.email_verified:
                            messages.warning(request, f'¡Bienvenido, {user.first_name or user.username}! Tu email no está verificado. Algunas funciones estarán limitadas.')
                        else:
                            messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
                    except:
                        messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
                    
                    next_url = request.GET.get('next', 'core:privada')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
            else:
                # Verificar si el usuario existe pero la contraseña es incorrecta
                try:
                    from django.contrib.auth.models import User
                    user = User.objects.get(username=username)
                    messages.error(request, 'La contraseña es incorrecta. Verifica tu contraseña e intenta nuevamente.')
                except User.DoesNotExist:
                    messages.error(request, 'No existe una cuenta con ese nombre de usuario. Verifica el nombre o regístrate si es tu primera vez.')
        else:
            # El formulario tiene errores, Django los mostrará automáticamente
            if not form.cleaned_data.get('username'):
                messages.error(request, 'Por favor, ingresa tu nombre de usuario.')
            elif not form.cleaned_data.get('password'):
                messages.error(request, 'Por favor, ingresa tu contraseña.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos. Por favor, intenta nuevamente.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def verificar_email(request):
    if request.method == "POST":
        email = (
            (request.POST.get('email') or "").strip().lower()
            or (request.session.get('verify_email', "") or "").strip().lower()
            or (getattr(request.user, "email", "") or "").strip().lower()
        )
        code_in = (request.POST.get('code') or "").strip()

        ctx = {"email": email}  # <-- usar este ctx en TODOS los render del POST

        if not email or not code_in:
            if not email and not code_in:
                messages.error(request, "Por favor, completá tu correo electrónico y el código de verificación.")
            elif not email:
                messages.error(request, "Por favor, ingresá tu correo electrónico.")
            else:
                messages.error(request, "Por favor, ingresá el código de verificación que te enviamos por email.")
            return render(request, 'registration/verificar_email.html', ctx)

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .filter(email__iexact=email)
                    .first()
                )
                if not user:
                    messages.error(request, f"No existe una cuenta con el correo '{email}'. Verificá que hayas ingresado el correo correcto.")
                    return render(request, 'registration/verificar_email.html', ctx)

                profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

                if profile.email_verified:
                    messages.success(request, "¡Tu correo ya está verificado! Podés iniciar sesión ahora.")
                    request.session.pop('verify_email', None)
                    return redirect('login')

                now = timezone.now()

                # Expirado
                if not profile.verification_expires_at or now > profile.verification_expires_at:
                    messages.warning(request, "El código de verificación expiró. Podés solicitar uno nuevo haciendo clic en 'Reenviar código'.")
                    return render(request, 'registration/verificar_email.html', ctx)

                # Código incorrecto
                if not _code_is_valid(profile.email_verification_code, code_in):
                    profile.verification_tries = F("verification_tries") + 1
                    profile.save(update_fields=["verification_tries"])
                    profile.refresh_from_db(fields=["verification_tries"])

                    if profile.verification_tries >= MAX_TRIES:
                        profile.verification_tries = 0
                        profile.save(update_fields=["verification_tries"])
                        start_cooldown(email)
                        messages.error(
                            request,
                            f"Superaste el número máximo de intentos ({MAX_TRIES}). Por seguridad, esperá 1 minuto y luego podés reenviar un nuevo código."
                        )
                        return render(request, 'registration/verificar_email.html', ctx)

                    restantes = MAX_TRIES - profile.verification_tries
                    messages.error(request, f"Código incorrecto. Te quedan {restantes} intento(s) antes de que se bloquee temporalmente.")
                    return render(request, 'registration/verificar_email.html', ctx)

                # Éxito
                profile.email_verified = True
                profile.email_verification_code = None
                profile.verification_expires_at = None
                profile.verification_tries = 0
                profile.save(update_fields=[
                    "email_verified", "email_verification_code",
                    "verification_expires_at", "verification_tries"
                ])

            request.session.pop('verify_email', None)
            messages.success(request, f"¡Excelente! Tu email '{email}' ha sido verificado correctamente. Ya podés iniciar sesión y disfrutar de todos los servicios.")
            return redirect('login')

        except Exception as e:
            logger.exception("[verificar_email] Error general: %s", e)
            messages.error(request, "Ocurrió un error. Probá de nuevo más tarde.")
            return render(request, 'registration/verificar_email.html', ctx)

    # GET
    ctx = {
        "email": request.user.email if request.user.is_authenticated else request.session.get('verify_email', '')
    }
    return render(request, 'registration/verificar_email.html', ctx)

def reenviar_codigo(request):
    if request.method != "POST":
        return redirect('core:verificar_email')

    email = (request.POST.get("email") or "").strip().lower()
    if not email:
        messages.error(request, "Por favor, ingresá tu correo electrónico para reenviar el código.")
        return redirect('core:verificar_email')

    remaining_cd = cooldown_remaining(email)
    if remaining_cd > 0:
        messages.warning(request, f"Por seguridad, debés esperar {remaining_cd} segundo(s) antes de reenviar un nuevo código.")
        return redirect('core:verificar_email')

    allowed, remaining_bucket = can_reenviar_now(email)
    if not allowed:
        messages.warning(request, f"Alcanzaste el límite de envíos por hora. Esperá {remaining_bucket} segundo(s) para reenviar.")
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
                messages.error(request, f"No existe una cuenta con el correo '{email}'. Verificá que hayas ingresado el correo correcto.")
                return redirect('core:verificar_email')

            profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

            if profile.email_verified:
                messages.success(request, "¡Ese correo ya está verificado! Podés iniciar sesión ahora.")
                return redirect('login')

            # Generar y enviar un nuevo código
            profile.set_new_code(minutes=WINDOW_MIN)
            profile.verification_tries = 0  # limpio intentos al reenviar
            profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])

            enviar_codigo(email, profile.email_verification_code, minutos=WINDOW_MIN)
            mark_reenviado(email)  # cuenta este envío dentro de la ventana

            messages.success(request, f"¡Nuevo código enviado! Te enviamos un código de verificación a {email}. Revisá tu correo y seguí las instrucciones.")

    except Exception as e:
        logger.exception("[reenviar_codigo] Error: %s", e)
        messages.error(request, "No pudimos reenviar el código. Verificá que el correo sea correcto e intentá más tarde.")

    return redirect('core:verificar_email')

def verificar_email_obligatorio(request):
    """
    Vista de verificación obligatoria para usuarios no verificados que intentan hacer login
    """
    # Verificar si el usuario necesita verificación
    if not request.session.get('user_needs_verification'):
        return redirect('core:verificar_email')
    
    email = request.session.get('verify_email', '')
    if not email:
        return redirect('core:verificar_email')
    
    if request.method == "POST":
        code_in = (request.POST.get('code') or "").strip()
        
        if not code_in:
            messages.error(request, "Por favor, ingresá el código de verificación que te enviamos por email.")
            return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .filter(email__iexact=email)
                    .first()
                )
                if not user:
                    messages.error(request, f"No existe una cuenta con el correo '{email}'. Verificá que hayas ingresado el correo correcto.")
                    return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

                profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

                if profile.email_verified:
                    # Limpiar sesión y redirigir al login
                    request.session.pop('user_needs_verification', None)
                    request.session.pop('verify_email', None)
                    messages.success(request, "¡Tu correo ya está verificado! Ya podés iniciar sesión.")
                    return redirect('login')

                now = timezone.now()

                # Expirado
                if not profile.verification_expires_at or now > profile.verification_expires_at:
                    messages.warning(request, "El código de verificación expiró. Podés solicitar uno nuevo haciendo clic en 'Reenviar código'.")
                    return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

                # Código incorrecto
                if not _code_is_valid(profile.email_verification_code, code_in):
                    profile.verification_tries = F("verification_tries") + 1
                    profile.save(update_fields=["verification_tries"])
                    profile.refresh_from_db(fields=["verification_tries"])

                    if profile.verification_tries >= MAX_TRIES:
                        profile.verification_tries = 0
                        profile.save(update_fields=["verification_tries"])
                        start_cooldown(email)
                        messages.error(
                            request,
                            f"Superaste el número máximo de intentos ({MAX_TRIES}). Por seguridad, esperá 1 minuto y luego podés reenviar un nuevo código."
                        )
                        return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

                    restantes = MAX_TRIES - profile.verification_tries
                    messages.error(request, f"Código incorrecto. Te quedan {restantes} intento(s) antes de que se bloquee temporalmente.")
                    return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

                # Éxito - verificar email
                profile.email_verified = True
                profile.email_verification_code = None
                profile.verification_expires_at = None
                profile.verification_tries = 0
                profile.save(update_fields=[
                    "email_verified", "email_verification_code",
                    "verification_expires_at", "verification_tries"
                ])

                # Hacer login automático después de verificar
                auth_login(request, user)

            # Limpiar sesión
            request.session.pop('user_needs_verification', None)
            request.session.pop('verify_email', None)
            
            messages.success(request, f"¡Excelente! Tu email '{email}' ha sido verificado correctamente. ¡Bienvenido!")
            return redirect('core:privada')

        except Exception as e:
            logger.exception("[verificar_email_obligatorio] Error general: %s", e)
            messages.error(request, "Ocurrió un error. Probá de nuevo más tarde.")
            return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

    # GET
    return render(request, 'registration/verificar_email_obligatorio.html', {'email': email})

def reenviar_codigo_obligatorio(request):
    """
    Reenviar código para verificación obligatoria
    """
    if request.method != "POST":
        return redirect('core:verificar_email_obligatorio')

    email = request.session.get('verify_email', '')
    if not email:
        messages.error(request, "No se encontró el email en la sesión.")
        return redirect('core:verificar_email_obligatorio')

    remaining_cd = cooldown_remaining(email)
    if remaining_cd > 0:
        messages.warning(request, f"Por seguridad, debés esperar {remaining_cd} segundo(s) antes de reenviar un nuevo código.")
        return redirect('core:verificar_email_obligatorio')

    allowed, remaining_bucket = can_reenviar_now(email)
    if not allowed:
        messages.warning(request, f"Alcanzaste el límite de envíos por hora. Esperá {remaining_bucket} segundo(s) para reenviar.")
        return redirect('core:verificar_email_obligatorio')

    try:
        with transaction.atomic():
            user = (
                User.objects
                .select_for_update()
                .filter(email__iexact=email)
                .first()
            )
            if not user:
                messages.error(request, f"No existe una cuenta con el correo '{email}'. Verificá que hayas ingresado el correo correcto.")
                return redirect('core:verificar_email_obligatorio')

            profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

            if profile.email_verified:
                messages.success(request, "¡Ese correo ya está verificado! Podés iniciar sesión ahora.")
                request.session.pop('user_needs_verification', None)
                request.session.pop('verify_email', None)
                return redirect('login')

            # Generar y enviar un nuevo código
            profile.set_new_code(minutes=WINDOW_MIN)
            profile.verification_tries = 0  # limpio intentos al reenviar
            profile.save(update_fields=["email_verification_code", "verification_expires_at", "verification_tries"])

            enviar_codigo(email, profile.email_verification_code, minutos=WINDOW_MIN)
            mark_reenviado(email)  # cuenta este envío dentro de la ventana

            messages.success(request, f"¡Nuevo código enviado! Te enviamos un código de verificación a {email}. Revisá tu correo y seguí las instrucciones.")

    except Exception as e:
        logger.exception("[reenviar_codigo_obligatorio] Error: %s", e)
        messages.error(request, "No pudimos reenviar el código. Verificá que el correo sea correcto e intentá más tarde.")

    return redirect('core:verificar_email_obligatorio')

def _code_is_valid(stored: str | None, given: str | None) -> bool:
    return hmac.compare_digest((stored or ""), (given or ""))

@login_required
@email_verified_required
def agregar_publicacion(request):
    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                publicacion = form.save()
                
                # Crear artículos desde el formset
                formset = PublicacionArticuloFormSet(
                    data=request.POST,
                    files=request.FILES,
                    instance=publicacion
                )
                
                if formset.is_valid():
                    formset.save()
                    
                    # Enviar notificaciones
                    try:
                        favoritos = Favoritos.objects.filter(id_comedor=publicacion.id_comedor)
                        for favorito in favoritos:
                            if favorito.id_usuario.user.email:
                                # Aquí se enviaría el email
                                print(f"Notificando a {favorito.id_usuario.user.email} sobre nueva publicación")
                    except Exception as e:
                        print(f"Error enviando notificaciones: {e}")
                    
                    messages.success(request, "¡Publicación creada exitosamente!")
                    return redirect("core:listar_publicaciones", id_comedor=publicacion.id_comedor_id)
                else:
                    messages.error(request, "Error en los artículos de la publicación.")
                    return render(request, "core/agregar_publicacion.html", {"form": form, "formset": formset})
                    
            except Exception as e:
                messages.error(request, f"Error creando publicación: {str(e)}")
                return render(request, "core/agregar_publicacion.html", {"form": form, "formset": PublicacionArticuloFormSet()})
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
            return render(request, "core/agregar_publicacion.html", {"form": form, "formset": PublicacionArticuloFormSet()})
    else:
        form = PublicacionForm()
        formset = PublicacionArticuloFormSet()
    
    return render(request, "core/agregar_publicacion.html", {"form": form, "formset": formset})

def listar_publicaciones(request, id_comedor):
    publicaciones = (
        Publicacion.objects
        .filter(id_comedor=id_comedor)
        .select_related("id_comedor", "id_tipo_publicacion")
        .order_by("-fecha_inicio")
    )

    return render(request, "core/listar_publicaciones.html", {"publicaciones": publicaciones})

def agregar_favorito(request):
    if request.method == 'POST':
        form = FavoritoForm(request.POST)
        if form.is_valid():
            favorito, created = Favoritos.objects.get_or_create(
                id_usuario=form.cleaned_data['id_usuario'],
                id_comedor=form.cleaned_data['id_comedor']
            )
            messages.success(request, "Comedor agregado a favoritos.")
            return redirect('core:listar_comedores')
        else:
            messages.error(request, "Por favor, revisá los datos y corregí los errores.")
    else:
        form = FavoritoForm()
    return render(request, 'core/agregar_favorito.html', {'form': form})

def eliminar_favorito(request, favorito_id):
    favorito = Favoritos.objects.filter(id=favorito_id).first()
    if request.method == 'POST':
        if favorito:
            favorito.delete()
            messages.success(request, "Comedor eliminado de favoritos.")
        else:
            messages.error(request, "No se encontró el favorito.")
        return redirect('core:listar_comedores')
    return render(request, 'core/confirmar_eliminar_favorito.html', {'favorito': favorito})

# DEPRECADO: Las donaciones ahora se hacen desde el modal en las publicaciones (api_enviar_donacion)
# @login_required
# @email_verified_required
# def crear_donacion(request):
#     if request.method == 'POST':
#         form = DonacionForm(request.POST)
#         if form.is_valid():
#             try:
#                 donacion = form.save()
#                 
#                 # Enviar notificación al comedor
#                 try:
#                     if donacion.id_comedor.email_contacto:
#                         print(f"Notificando a {donacion.id_comedor.email_contacto} sobre nueva donación")
#                         # Aquí se enviaría el email al comedor
#                 except Exception as e:
#                     print(f"Error enviando notificación: {e}")
#                 
#                 messages.success(request, "¡Donación creada exitosamente!")
#                 return redirect('core:listar_donaciones')
#             except Exception as e:
#                 messages.error(request, f"Error creando donación: {str(e)}")
#                 return render(request, 'core/crear_donacion.html', {'form': form})
#         else:
#             messages.error(request, "Por favor, revisá los datos y corregí los errores.")
#             return render(request, 'core/crear_donacion.html', {'form': form})
#     else:
#         form = DonacionForm()
#     return render(request, 'core/crear_donacion.html', {'form': form})

def eliminar_donacion(request, donacion_id):
    donacion = Donacion.objects.filter(id=donacion_id).first()
    if request.method == 'POST':
        if donacion:
            donacion.delete()
            messages.success(request, "Donación eliminada.")
        else:
            messages.error(request, "No se encontró la donación.")
        return redirect('core:listar_donaciones')
    return render(request, 'core/confirmar_eliminar_donacion.html', {'donacion': donacion})

def editar_donacion(request, donacion_id):
    donacion = Donacion.objects.filter(id=donacion_id).first()
    if not donacion:
        messages.error(request, "No se encontró la donación.")
        return redirect('core:listar_donaciones')
    if request.method == 'POST':
        form = DonacionForm(request.POST, instance=donacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Donación editada correctamente.")
            return redirect('core:listar_donaciones')
        else:
            messages.error(request, "Por favor, revisá los datos y corregí los errores.")
    else:
        form = DonacionForm(instance=donacion)
    return render(request, 'core/editar_donacion.html', {'form': form, 'donacion': donacion})

@login_required
def listar_favoritos(request):
    favoritos = Favoritos.objects.filter(id_usuario=request.user.userprofile)
    return render(request, 'core/listar_favoritos.html', {'favoritos': favoritos})

@login_required
def agregar_favorito(request):
    if request.method == 'POST':
        # Obtener datos del POST directamente
        comedor_id = request.POST.get('id_comedor')
        usuario_id = request.POST.get('id_usuario')
        
        try:
            from core.models import Comedor, UserProfile
            
            comedor = Comedor.objects.get(id=comedor_id)
            usuario = UserProfile.objects.get(id=usuario_id)
            
            favorito, created = Favoritos.objects.get_or_create(
                id_usuario=usuario,
                id_comedor=comedor
            )
            
            if created:
                messages.success(request, f"Comedor '{comedor.nombre}' agregado a favoritos.")
            else:
                messages.info(request, "Este comedor ya estaba en tus favoritos.")
            
            return redirect('core:listar_favoritos')
            
        except (Comedor.DoesNotExist, UserProfile.DoesNotExist, ValueError) as e:
            messages.error(request, "Error al procesar la solicitud.")
            return redirect('core:listar_comedores')
    else:
        form = FavoritoForm()
    return render(request, 'core/agregar_favorito.html', {'form': form})

def listar_todas_donaciones(request):
    donaciones = Donacion.objects.all()
    return render(request, 'core/listar_donaciones.html', {'donaciones': donaciones})

def listar_donaciones_usuario(request, id_usuario):
    donaciones = Donacion.objects.filter(id_usuario_id=id_usuario)
    return render(request, 'core/listar_donaciones.html', {'donaciones': donaciones})

@require_GET
def listar_articulos_disponibles_por_publicacion(request, id_publicacion):
    """
    API: Devuelve los nombres de artículos de la publicación indicada.
    GET /api/publicaciones/<id_publicacion>/articulos/
    """
    try:
        pub = Publicacion.objects.get(pk=id_publicacion)
        articulos = list(
            PublicacionArticulo.objects
            .filter(id_publicacion=pub)
            .values_list("nombre_articulo", flat=True)
        )
        return JsonResponse({"articulos": articulos})
        
    except Publicacion.DoesNotExist:
        return JsonResponse({"error": "La publicación no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_POST
@login_required
def api_enviar_donacion(request):
    """
    API: Crea una donación desde el modal.
    POST /api/donaciones/enviar/
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        
        publicacion_id = data.get('publicacion_id')
        articulos = data.get('articulos', [])
        contacto = data.get('contacto', '')
        mensaje = data.get('mensaje', '')
        
        if not publicacion_id:
            return JsonResponse({"error": "ID de publicación requerido."}, status=400)
            
        if not articulos:
            return JsonResponse({"error": "Debe seleccionar al menos un artículo."}, status=400)
            
        if not contacto.strip():
            return JsonResponse({"error": "Datos de contacto requeridos."}, status=400)
        
        # Obtener la publicación
        publicacion = Publicacion.objects.get(pk=publicacion_id)
        
        # Crear la donación
        donacion = Donacion.objects.create(
            id_usuario=request.user.userprofile,
            id_comedor=publicacion.id_comedor,
            id_publicacion=publicacion
        )
        
        # Crear los items de la donación
        for articulo in articulos:
            DonacionItem.objects.create(
                id_donacion=donacion,
                nombre_articulo=articulo,
                cantidad=1  # Por defecto 1, se podría pedir cantidad
            )
        
        # Aquí se podría guardar los datos de contacto en un modelo separado
        # o enviar un email al comedor con la información
        
        return JsonResponse({
            "success": True, 
            "message": "Donación enviada exitosamente",
            "donacion_id": donacion.id
        })
        
    except Publicacion.DoesNotExist:
        return JsonResponse({"error": "La publicación no existe."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def _assert_publicacion_vigente(pub: Publicacion):
    """Opcional: exigir publicación vigente al momento de donar."""
    now = timezone.now()
    if not (pub.fecha_inicio <= now and (pub.fecha_fin is None or pub.fecha_fin >= now)):
        raise ValidationError("La publicación no está vigente.")

@require_POST
@transaction.atomic
def api_crear_donacion(request, comedor_id: int, publicacion_id: int):
    """
    API: Crea una donación para UNA publicación específica.
    POST /comedores/<comedor_id>/publicaciones/<publicacion_id>/donar/
    Body JSON: { "id_usuario": 123, "articulos": ["Leche", "Azúcar"] }

    Respuestas:
      201: { "ok": true, "donacion_id": 7 }
      400: { "ok": false, "error": "mensaje" }
    """
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    id_usuario = data.get("id_usuario")
    articulos: List[str] = data.get("articulos") or []

    # Validaciones básicas de entrada
    if not isinstance(id_usuario, int):
        return JsonResponse({"ok": False, "error": "id_usuario es requerido (int)."}, status=400)
    if not isinstance(articulos, list) or not all(isinstance(x, str) for x in articulos):
        return JsonResponse({"ok": False, "error": "articulos debe ser una lista de strings."}, status=400)
    articulos = [a.strip() for a in articulos if (a or "").strip()]
    if not articulos:
        return JsonResponse({"ok": False, "error": "Debe seleccionar al menos un artículo."}, status=400)

    # Entidades base
    usuario = get_object_or_404(UserProfile.objects.select_related("user"), pk=id_usuario)
    comedor = get_object_or_404(Comedor, pk=comedor_id)
    pub = get_object_or_404(Publicacion.objects.select_related("comedor"), pk=publicacion_id)

    # Publicación debe pertenecer al comedor indicado
    if pub.comedor_id != comedor.id:
        return JsonResponse({"ok": False, "error": "La publicación no corresponde al comedor."}, status=400)

    # (Opcional) exigir vigencia
    try:
        _assert_publicacion_vigente(pub)
    except ValidationError as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

    # Catálogo permitido (case-insensitive) SOLO de esa publicación
    permitidos = {
        n.strip().lower(): n
        for n in PublicacionArticulo.objects
                   .filter(publicacion=pub)
                   .values_list("nombre_articulo", flat=True)
    }

    # Normalizar y quedarnos con los válidos; ignorar duplicados
    elegidos_norm = {a.lower() for a in articulos}
    validos = [permitidos[a] for a in elegidos_norm if a in permitidos]

    if not validos:
        return JsonResponse({"ok": False, "error": "Los artículos no pertenecen a la publicación indicada."}, status=400)

    # Crear donación + detalle
    don = Donacion.objects.create(
        id_usuario=usuario,
        id_comedor=comedor,
        id_publicacion=pub,
    )
    DonacionItem.objects.bulk_create([
        DonacionItem(id_donacion=don, nombre_articulo=nombre, cantidad=1)  # cantidad fija = 1; ajustá si sumás cantidades
        for nombre in validos
    ])

    return JsonResponse({"ok": True, "donacion_id": don.id}, status=201)

def buscar(request):
    query = request.GET.get('q', '')
    results = SearchQuerySet().filter(content=query) if query else []
    return render(request, 'core/buscar.html', {'results': results, 'query': query})

from django.contrib.admin.views.decorators import staff_member_required
from haystack.management.commands import update_index
from django.http import HttpResponse

@staff_member_required
def rebuild_index_view(request):
    update_index.Command().handle(interactive=False, verbosity=1)
    return HttpResponse("Índice de búsqueda reconstruido.")

def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow:",
        "Sitemap: https://comedorescomunitarios.onrender.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")