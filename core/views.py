from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models

from datetime import timedelta
import secrets

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone

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
                print(f"Image uploaded: {comedor.imagen.name} -> {comedor.imagen.url}")

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
        Paso 1: NO creamos el User todavía.
        Guardamos todo en sesión y enviamos el código al email ingresado.
        """
    next_url = request.GET.get('next', '')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            raw_password = form.cleaned_data["password1"]

            # Unicidad antes de enviar el código
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, "Ese nombre de usuario ya está en uso.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})
            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, "Ese email ya tiene una cuenta.")
                return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

            code = generar_codigo()
            expires_at = timezone.now() + timedelta(minutes=15)

            # Guardar en sesión (sin texto plano de contraseña)
            request.session[SESSION_KEY] = {
                "username": username,
                "email": email,
                "password_hash": make_password(raw_password),
                "code": code,
                "expires_at": expires_at.isoformat(),
                "resend_after": (timezone.now() + timedelta(seconds=60)).isoformat(),  # anti-spam
            }
            request.session.modified = True

            # Enviar email
            enviar_codigo(email, code, minutos=15)

            messages.success(request, "Te enviamos un código a tu email. Ingrésalo para activar tu cuenta.")
            return redirect('core:verificar_email')
        else:
            messages.error(request, "Revisá los datos del formulario.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})


def verificar_email(request):
    """
        Paso 2: valida el código de sesión; recién entonces crea el User y el UserProfile.
        """
    pending = request.session.get(SESSION_KEY)

    if request.method == "POST":
        code_in = (request.POST.get('code') or "").strip()

        if not pending:
            messages.error(request, "No hay un registro pendiente. Repetí el proceso.")
            return redirect('core:registro')

        # Expiración
        try:
            expires_at = timezone.datetime.fromisoformat(pending["expires_at"])
            if timezone.is_naive(expires_at):
                expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())
        except Exception:
            messages.error(request, "Registro pendiente inválido. Repetí el proceso.")
            request.session.pop(SESSION_KEY, None)
            return redirect('core:registro')

        if timezone.now() > expires_at:
            messages.error(request, "El código expiró. Pedí uno nuevo.")
            return redirect('core:reenviar_verificacion')

        # Comparación en tiempo constante
        if not secrets.compare_digest(code_in, pending["code"]):
            messages.error(request, "El código ingresado es incorrecto. Intenta nuevamente.")
            return render(request, 'registration/verificar_email.html')

        # OK: crear User y Profile
        with transaction.atomic():
            # doble chequeo de unicidad por concurrencia
            if User.objects.filter(username__iexact=pending["username"]).exists() \
                    or User.objects.filter(email__iexact=pending["email"]).exists():
                messages.error(request, "Ese usuario/email ya existe. Probá con otros datos.")
                request.session.pop(SESSION_KEY, None)
                return redirect('core:registro')

            user = User.objects.create(
                username=pending["username"],
                email=pending["email"],
                is_active=True,
            )
            # set password hash ya generado
            user.password = pending["password_hash"]
            user.save(update_fields=["password", "is_active", "email", "username"])

            UserProfile.objects.create(
                user=user,
                email_verified=True,
            )

        # limpiar sesión
        request.session.pop(SESSION_KEY, None)
        messages.success(request, "¡Email verificado correctamente! Ya podés iniciar sesión.")
        return redirect('login')

    # GET
    return render(request, 'registration/verificar_email.html')


def reenviar_verificacion(request):
    """
    Regenera y reenvía el código usando SOLAMENTE la sesión (sin DB extra).
    """
    pending = request.session.get(SESSION_KEY)
    if not pending:
        messages.error(request, "No hay verificación pendiente.")
        return redirect('core:registro')

    # Rate limit básico
    try:
        resend_after = timezone.datetime.fromisoformat(pending["resend_after"])
        if timezone.is_naive(resend_after):
            resend_after = timezone.make_aware(resend_after, timezone.get_current_timezone())
    except Exception:
        resend_after = timezone.now()

    if timezone.now() < resend_after:
        messages.info(request, "Esperá unos segundos antes de volver a solicitar el código.")
        return redirect('core:verificar_email')

    # Regenerar
    code = generar_codigo()
    pending["code"] = code
    pending["expires_at"] = expira_en(15)
    pending["resend_after"] = (timezone.now() + timedelta(seconds=60)).isoformat()
    request.session[SESSION_KEY] = pending
    request.session.modified = True

    enviar_codigo(pending["email"], code, minutos=15)
    messages.success(request, "Te reenviamos el código a tu email.")
    return redirect('core:verificar_email')