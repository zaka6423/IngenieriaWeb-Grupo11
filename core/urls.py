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
    path('publicaciones/', views.listar_publicaciones, name='listar_publicaciones'),
    path('publicaciones/crear/', views.agregar_publicacion, name='crear_publicacion'),
    path('publicaciones/mis-publicaciones/', views.mis_publicaciones, name='mis_publicaciones'),
    path('publicaciones/<int:pk>/', views.detalle_publicacion, name='detalle_publicacion'),
    path('publicaciones/<int:pk>/editar/', views.editar_publicacion, name='editar_publicacion'),
    path('publicaciones/<int:pk>/eliminar/', views.eliminar_publicacion, name='eliminar_publicacion'),

    # Favoritos
    path('favoritos/', views.listar_favoritos, name='listar_favoritos'),
    path('favoritos/agregar/', views.agregar_favorito, name='agregar_favorito'),
    path('favoritos/eliminar/<int:favorito_id>/', views.eliminar_favorito, name='eliminar_favorito'),

    # Donaciones
    path('donaciones/', views.listar_todas_donaciones, name='listar_donaciones'),
    path('donaciones/mis-donaciones/', views.listar_donaciones_usuario, name='mis_donaciones'),
    path('donaciones/crear/', views.crear_donacion, name='crear_donacion'),
    path('donaciones/editar/<int:donacion_id>/', views.editar_donacion, name='editar_donacion'),
    path('donaciones/eliminar/<int:donacion_id>/', views.eliminar_donacion, name='eliminar_donacion'),

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
