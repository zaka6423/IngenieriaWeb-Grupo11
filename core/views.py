from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import uuid

from .forms import ComedorForm, CustomUserCreationForm
from .models import Comedor, UserProfile

def home(request):
    comedores_count = Comedor.objects.count()
    total_capacity = Comedor.objects.aggregate(total=models.Sum('capacidad'))['total'] or 0
    barrios_count = Comedor.objects.values('barrio').distinct().count()
    tipos_count = Comedor.objects.values('tipo').distinct().count()
    comedores_recientes = Comedor.objects.all().order_by('-id')[:6]
    
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
    comedores_count = Comedor.objects.count()
    total_capacity = Comedor.objects.aggregate(total=models.Sum('capacidad'))['total'] or 0
    barrios_count = Comedor.objects.values('barrio').distinct().count()
    tipos_count = Comedor.objects.values('tipo').distinct().count()
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
            try:
                user = form.save()

                profile = UserProfile.objects.create(
                    user=user,
                    activation_token=str(uuid.uuid4())
                )

                activation_link = request.build_absolute_uri(
                    reverse('core:activate_account', args=[profile.activation_token])
                )

                try:
                    send_mail(
                        'Activa tu cuenta - Comedores Comunitarios',
                        f'''¡Hola {user.first_name}!

Gracias por registrarte en Comedores Comunitarios.

Para activar tu cuenta, haz clic en el siguiente enlace:
{activation_link}

Si no solicitaste esta cuenta, puedes ignorar este email.

¡Bienvenido a nuestra comunidad solidaria!

El equipo de Comedores Comunitarios''',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f'¡Registro exitoso! Se ha enviado un email de activación a {user.email}. Revisa tu bandeja de entrada y spam.')
                except Exception as e:
                    messages.warning(request, 'Usuario creado exitosamente, pero hubo un error al enviar el email de activación. Contacta al administrador.')

                return render(request, 'registration/registro_exitoso.html', {'user_email': user.email})
            except Exception as e:
                messages.error(request, 'Hubo un error al crear la cuenta. Por favor, intenta nuevamente.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
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

def custom_login(request):
    """
    Vista personalizada de login
    """
    if request.user.is_authenticated:
        return redirect('core:privada')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
                    next_url = request.GET.get('next', 'core:privada')
                    return redirect(next_url)
                else:
                    return render(request, 'registration/cuenta_inactiva.html')
            else:
                try:
                    from django.contrib.auth.models import User
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        if user.is_active:
                            auth_login(request, user)
                            messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
                            next_url = request.GET.get('next', 'core:privada')
                            return redirect(next_url)
                        else:
                            return render(request, 'registration/cuenta_inactiva.html')
                    else:
                        messages.error(request, 'Usuario o contraseña incorrectos.')
                except User.DoesNotExist:
                    messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def crear_comedor(request):
    if request.method == 'POST':
        form = ComedorForm(request.POST, request.FILES)
        if form.is_valid():
            comedor = form.save()
            
            return redirect('core:listar_comedores')
    else:
        form = ComedorForm()
    return render(request, 'core/crear_comedor.html', {'form': form})

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

def detalle_comedor(request, pk):
    comedor = get_object_or_404(Comedor, pk=pk)
    
    return render(request, 'core/detalle_comedor.html', {'comedor': comedor})

