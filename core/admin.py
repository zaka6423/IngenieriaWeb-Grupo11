from django.contrib import admin
from .models import Comedor, UserProfile, Publicacion, PublicacionArticulo

# Register your models here.
@admin.register(Comedor)
class ComedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'barrio', 'tipo', 'capacidad']
    list_filter = ['barrio', 'tipo']
    search_fields = ['nombre', 'barrio']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_verified', 'activation_token']
    list_filter = ['email_verified']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['activation_token']

class PublicacionArticuloInline(admin.TabularInline):
    model = PublicacionArticulo
    extra = 1

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'comedor', 'tipo_donacion']
    inlines = [PublicacionArticuloInline]

@admin.register(PublicacionArticulo)
class PublicacionArticuloAdmin(admin.ModelAdmin):
    list_display = ['publicacion', 'nombre_articulo']