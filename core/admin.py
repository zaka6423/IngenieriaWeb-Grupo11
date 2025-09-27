from django.contrib import admin
from .models import Comedor, UserProfile, Publicacion, PublicacionArticulo, Favoritos, Donacion, TipoDonacion

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

@admin.register(Favoritos)
class FavoritosAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'id_comedor', 'fecha_alta')
    search_fields = ('id_usuario__user__username', 'id_comedor__nombre')
    list_filter = ('id_comedor',)

@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'id_usuario', 'id_tipodonacion', 'descripcion')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('id_tipodonacion',)

@admin.register(TipoDonacion)
class TipoDonacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion')
    search_fields = ('descripcion',)