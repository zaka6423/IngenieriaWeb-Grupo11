from django import forms
from .models import Comedor

class ComedorForm(forms.ModelForm):
    class Meta:
        model = Comedor
        fields = ['nombre', 'descripcion', 'imagen', 'barrio', 'tipo', 'capacidad']

