from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import uuid
import random

from .forms import ComedorForm, CustomUserCreationForm
from .models import Comedor, UserProfile

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

def registro(request):
    next_url = request.GET.get('next', '')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Generar código aleatorio de 6 dígitos
            verification_code = str(random.randint(100000, 999999))
            # Crear perfil de usuario con el código
            profile = UserProfile.objects.create(
                user=user,
                activation_token=str(uuid.uuid4()),
                email_verification_code=verification_code
            )
            # Enviar email con el código
            try:
                send_mail(
                    'Código de verificación de cuenta',
                    f'Tu código de verificación es: {verification_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Se ha enviado un código de verificación a tu email. Ingrésalo para activar tu cuenta.')
            except Exception as e:
                messages.warning(request, 'Error al enviar el email de verificación. Contacta al administrador.')
            return redirect('core:verificar_email')
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

def verificar_email(request):
    if request.method == "POST":
        code = request.POST.get('code')
        # Buscar el perfil del usuario más reciente sin verificar
        profile = UserProfile.objects.filter(email_verified=False).order_by('-id').first()
        if profile and profile.email_verification_code == code:
            profile.email_verified = True
            profile.user.is_active = True
            profile.user.save()
            profile.save()
            messages.success(request, '¡Email verificado correctamente! Ya puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'El código ingresado es incorrecto. Intenta nuevamente.')
    return render(request, 'registration/verificar_email.html')
