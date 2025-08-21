from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado de registro que incluye el campo de email
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        }),
        help_text='Ingresa un correo electrónico válido'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            if field_name != 'email':  # El email ya tiene las clases
                field.widget.attrs.update({
                    'class': 'form-control'
                })
                if field_name == 'username':
                    field.widget.attrs['placeholder'] = 'Elige un nombre de usuario único'
                elif field_name == 'password1':
                    field.widget.attrs['placeholder'] = 'Crea una contraseña segura'
                elif field_name == 'password2':
                    field.widget.attrs['placeholder'] = 'Confirma tu contraseña'
    
    def clean_email(self):
        """
        Validar que el email sea único
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        """
        Guardar el usuario con el email
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
