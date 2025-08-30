from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse
from .forms import ComedorForm
from .models import Comedor
from django.db.models import Q

def home(request):
    return render(request, 'core/home.html')

@login_required
def privada(request):
    return render(request, 'core/privada.html')

def registro(request):
    next_url = request.GET.get('next', '')
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Login automático
            auth_login(request, user)
            # Volver a 'next' si venía de una página protegida; si no, a privada
            return redirect(request.POST.get('next') or reverse('core:privada'))
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form, 'next': next_url})

# Vista para crear comedor
@login_required
def crear_comedor(request):
    if request.method == 'POST':
        form = ComedorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
    return render(request, 'core/detalle_comedor.html', {'comedor': comedor})
