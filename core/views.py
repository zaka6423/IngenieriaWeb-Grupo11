from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse

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
