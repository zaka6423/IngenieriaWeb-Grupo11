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
    """
    Formulario personalizado de registro que incluye el campo de email
    """
    email = forms.EmailField(required=True, help_text='Requerido. Ingresa una dirección de email válida.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Requerido.')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        """
        Validar que el email sea único
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email

    def save(self, commit=True):
        """
        Guardar el usuario con el email
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = False  # Usuario inactivo hasta verificar email
        if commit:
            user.save()
        return user
