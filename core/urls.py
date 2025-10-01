# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('privada/', views.privada, name='privada'),
    

    # Comedores
    path('comedores/crear/', views.crear_comedor, name='crear_comedor'),
    path('comedores/', views.listar_comedores, name='listar_comedores'),
    path('comedores/<int:pk>/', views.detalle_comedor, name='detalle_comedor'),

    # Publicaciones
    path('publicaciones/crear/', views.agregar_publicacion, name='agregar_publicacion'),

    # Favoritos
    path('favoritos/', views.listar_favoritos, name='listar_favoritos'),
    path('favoritos/agregar/', views.agregar_favorito, name='agregar_favorito'),
    path('favoritos/<int:favorito_id>/eliminar/', views.eliminar_favorito, name='eliminar_favorito'),

    # Donaciones (solo API endpoints - las donaciones se hacen desde el modal en publicaciones)
    path('donaciones/', views.listar_todas_donaciones, name='listar_donaciones'),
    path('donaciones/mis-donaciones/', views.listar_donaciones_usuario, name='mis_donaciones'),
    path('donaciones/<int:donacion_id>/eliminar/', views.eliminar_donacion, name='eliminar_donacion'),
    path('donaciones/<int:donacion_id>/editar/', views.editar_donacion, name='editar_donacion'),

    # API endpoints para AJAX
    path('api/publicaciones/<int:id_publicacion>/articulos/', views.listar_articulos_disponibles_por_publicacion, name='api_articulos_publicacion'),
    path('api/donaciones/enviar/', views.api_enviar_donacion, name='api_enviar_donacion'),
    path('api/comedores/<int:comedor_id>/publicaciones/<int:publicacion_id>/donar/', views.api_crear_donacion, name='api_crear_donacion'),

    # Activacion por token
    path('activate/<str:token>/', views.activate_account, name='activate_account'),

    # Registro
    path('registro/', views.registro, name='registro'),
    path('signup/', views.registro, name='signup'),

    # Verificacion de email
    path('verificar-email/', views.verificar_email, name='verificar_email'),
    path('verificar-email/reenviar/', views.reenviar_codigo, name='reenviar_codigo'),
    
    # Verificacion obligatoria (para usuarios no verificados que intentan hacer login)
    path('verificar-email-obligatorio/', views.verificar_email_obligatorio, name='verificar_email_obligatorio'),
    path('verificar-email-obligatorio/reenviar/', views.reenviar_codigo_obligatorio, name='reenviar_codigo_obligatorio'),
]
