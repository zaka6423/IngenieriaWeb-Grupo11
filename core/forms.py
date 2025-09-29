from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Comedor, Favoritos, Donacion, Publicacion, PublicacionArticulo
from django.forms import inlineformset_factory


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
    email = forms.EmailField(required=True, help_text='Requerido. Ingresa una dirección de email válida.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Requerido.')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'username':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Nombre de usuario'
                })
            elif field_name == 'first_name':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Tu nombre'
                })
            elif field_name == 'last_name':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Tu apellido'
                })
            elif field_name == 'email':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com'
                })
            elif field_name in ['password1', 'password2']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Contraseña'
                })
        from django.utils.safestring import mark_safe
        self.fields['password1'].help_text = mark_safe('''
            <ul class="password-help-list">
                <li>Tu contraseña no puede ser muy similar a tu otra información personal.</li>
                <li>Tu contraseña debe contener al menos 8 caracteres.</li>
                <li>Tu contraseña no puede ser una contraseña comúnmente utilizada.</li>
                <li>Tu contraseña no puede ser completamente numérica.</li>
            </ul>
        ''')

        self.fields['password2'].help_text = 'Ingresa la misma contraseña que antes, para verificación.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = False
        if commit:
            user.save()
        return user

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'id_comedor', 'id_tipo_publicacion', 'descripcion', 'fecha_fin']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned = super().clean()
        titulo = (cleaned.get('titulo') or '').strip()
        comedor = cleaned.get('id_comedor')
        fecha_fin = cleaned.get('fecha_fin')

        if titulo and comedor:
            # Busco publicaciones con mismo título en ese comedor
            qs = Publicacion.objects.filter(
                id_comedor=comedor,
                titulo__iexact=titulo
            )
            # Excluir la instancia actual en caso de edición
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error('titulo',
                    f"El comedor '{comedor.nombre}' ya tiene una publicación con este título.")

        if fecha_fin and fecha_fin <= timezone.now():
            self.add_error('fecha_fin', "La fecha de fin debe ser posterior a la fecha de inicio.")

        return cleaned

class PublicacionArticuloForm(PublicacionForm):
    class Meta:
        model = PublicacionArticulo
        fields = ['nombre_articulo']
        widgets = {
            'nombre_articulo': forms.TextInput(attrs={'placeholder': 'Ej: Leche en polvo 1kg'}),
        }

# Inline formset (hijos) para artículos
PublicacionArticuloFormSet = inlineformset_factory(
    parent_model=Publicacion,
    model=PublicacionArticulo,
    form=PublicacionArticuloForm,
    fields=['nombre_articulo'],
    extra=3,          # cantidad de filas vacías iniciales
    can_delete=True,  # permitir borrar en edición
)

# Validación de duplicados en el formset (case-insensitive)
class PublicacionArticuloFormSetValidated(PublicacionArticuloFormSet.__class__):
    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue
            nombre = (form.cleaned_data.get('nombre_articulo') or '').strip().lower()
            if not nombre:
                # si dejaste la fila vacía, la ignoramos
                continue
            if nombre in seen:
                form.add_error('nombre_articulo', 'Este artículo está repetido.')
            seen.add(nombre)

# Helper para instanciar con validación
def get_articulos_formset(*, data=None, instance=None):
    base = inlineformset_factory(
        Publicacion, PublicacionArticulo,
        form=PublicacionArticuloForm,
        fields=['nombre_articulo'],
        extra=3, can_delete=True
    )
    # inyectamos el clean custom
    base.clean = PublicacionArticuloFormSetValidated.clean
    return base(data=data, instance=instance)

class FavoritoForm(forms.ModelForm):
    class Meta:
        model = Favoritos
        fields = ['id_usuario', 'id_comedor']

class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donacion
        fields = ['titulo', 'id_usuario', 'id_tipodonacion', 'descripcion']