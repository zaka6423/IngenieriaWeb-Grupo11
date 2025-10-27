from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Comedor, Favoritos, Donacion, Publicacion, PublicacionArticulo, DonacionItem, TipoPublicacion
from django.forms import inlineformset_factory, BaseInlineFormSet


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
            'tipo': forms.Select(choices=[
                ('', 'Selecciona un tipo de comedor'),
                ('Comunitario', 'Comunitario'),
                ('Parroquial', 'Parroquial'),
                ('Municipal', 'Municipal'),
                ('ONG', 'ONG'),
                ('Cooperativa', 'Cooperativa'),
                ('Barrial', 'Barrial'),
                ('Religioso', 'Religioso'),
                ('Social', 'Social'),
                ('Otro', 'Otro'),
            ], attrs={
                'class': 'form-control',
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
        fields = ['id_comedor', 'titulo',  'id_tipo_publicacion', 'descripcion', 'fecha_fin']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'id_comedor': 'Comedor',
            'titulo': 'Título',
            'id_tipo_publicacion': 'Tipo de publicación',
            'descripcion': 'Descripción',
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
                self.add_error('titulo', f"El comedor '{comedor}' ya tiene una publicación con este título.")

        if fecha_fin and fecha_fin <= timezone.now():
            self.add_error('fecha_fin', "La fecha de fin debe ser posterior a la fecha de inicio.")

        return cleaned

class TipoPublicacionForm(forms.ModelForm):
    class Meta:
        model = TipoPublicacion
        fields = ['descripcion']
        labels = {'descripcion': 'Descripción'}

class PublicacionArticuloForm(forms.ModelForm):
    class Meta:
        model = PublicacionArticulo
        fields = ['nombre_articulo']
        widgets = {
            'nombre_articulo': forms.TextInput(attrs={'placeholder': 'Ej: Leche en polvo 1kg'}),
        }

class BasePublicacionArticuloFormSet(BaseInlineFormSet):
    """Valida duplicados case-insensitive dentro del formset."""
    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
                continue
            nombre = (form.cleaned_data.get('nombre_articulo') or '').strip().lower()
            if not nombre:
                continue
            if nombre in seen:
                form.add_error('nombre_articulo', 'Este artículo está repetido.')
            else:
                seen.add(nombre)

PublicacionArticuloFormSet = inlineformset_factory(
    parent_model=Publicacion,
    model=PublicacionArticulo,
    form=PublicacionArticuloForm,
    formset=BasePublicacionArticuloFormSet,
    fields=['nombre_articulo'],
    extra=3,
    can_delete=True,
)

class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donacion
        fields = ['id_usuario', 'id_comedor', 'id_publicacion']
        labels = {
            'id_usuario': 'Usuario',
            'id_comedor': 'Comedor',
            'id_publicacion': 'Publicación',
        }


class DonacionItemForm(forms.ModelForm):
    class Meta:
        model = DonacionItem
        fields = ['nombre_articulo', 'cantidad']  # id_donacion lo maneja el formset
        labels = {'nombre_articulo': 'Artículo', 'cantidad': 'Cantidad'}


DonacionItemFormSet = inlineformset_factory(
    parent_model=Donacion,
    model=DonacionItem,
    form=DonacionItemForm,
    fields=['nombre_articulo', 'cantidad'],
    extra=1,
    can_delete=True,
)

class FavoritoForm(forms.ModelForm):
    class Meta:
        model = Favoritos
        fields = ['id_usuario', 'id_comedor']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.fecha_alta:
            instance.fecha_alta = timezone.now()
        if commit:
            instance.save()
        return instance