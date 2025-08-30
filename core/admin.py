from django.contrib import admin
from .models import Comedor

# Register your models here.
@admin.register(Comedor)
class ComedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'barrio', 'tipo', 'capacidad']
    list_filter = ['barrio', 'tipo']
    search_fields = ['nombre', 'barrio']
