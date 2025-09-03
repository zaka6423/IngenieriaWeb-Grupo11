from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import uuid

from .forms import ComedorForm, CustomUserCreationForm
from .models import Comedor, UserProfile

def home(request):
    try:
        comedores_count = Comedor.objects.count()
        total_capacity = Comedor.objects.aggregate(total=models.Sum('capacidad'))['total'] or 0
        barrios_count = Comedor.objects.values('barrio').distinct().count()
        tipos_count = Comedor.objects.values('tipo').distinct().count()
        comedores_recientes = Comedor.objects.all().order_by('-id')[:6]
    except Exception as e:
        # Loguear el error y mostrar valores por defecto
        print(f"Error en vista home: {e}")
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

            # Crear perfil de usuario
            profile = UserProfile.objects.create(
                user=user,
                activation_token=str(uuid.uuid4())
            )

            # Enviar email de activación
            activation_link = request.build_absolute_uri(
                reverse('core:activate_account', args=[profile.activation_token])
            )

            try:
                send_mail(
                    'Activa tu cuenta',
                    f'Haz clic en el siguiente enlace para activar tu cuenta: {activation_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Se ha enviado un email de activación. Revisa tu bandeja de entrada.')
            except Exception as e:
                messages.warning(request, 'Error al enviar el email de activación. Contacta al administrador.')

            return redirect('core:home')
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
