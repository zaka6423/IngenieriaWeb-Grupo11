from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Comedor

class ComedorForm(forms.ModelForm):
    """
    Formulario para crear y editar comedores
    """
    class Meta:
        model = Comedor
        fields = ['nombre', 'descripcion', 'imagen', 'barrio', 'tipo', 'capacidad']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del comedor'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del comedor'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'barrio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Barrio donde se encuentra'
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de comedor'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Capacidad máxima de personas'
            })
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=False):
        return super().save(commit=False)
