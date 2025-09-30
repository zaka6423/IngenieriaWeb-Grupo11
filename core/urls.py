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
    path('publicaciones/<int:id_comedor>/', views.listar_publicaciones, name="listar_publicaciones"),
    path('publicaciones/crear/', views.agregar_publicacion, name='agregar_publicacion'),

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
