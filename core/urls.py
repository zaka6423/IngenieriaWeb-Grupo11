# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('privada/', views.privada, name='privada'),
    path('comedores/crear/', views.crear_comedor, name='crear_comedor'),
    path('comedores/', views.listar_comedores, name='listar_comedores'),
    path('comedores/<int:pk>/', views.detalle_comedor, name='detalle_comedor'),
    path('activate/<str:token>/', views.activate_account, name='activate_account'),
]
