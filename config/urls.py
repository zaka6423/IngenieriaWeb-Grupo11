"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import registro, custom_login
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # URLs personalizadas de accounts (deben ir ANTES de include)
    path('accounts/signup/', registro, name='accounts_signup'),
    path('accounts/login/', custom_login, name='accounts_login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    # URLs de Django auth (después de las personalizadas)
    path('accounts/', include('django.contrib.auth.urls')),
    # URLs personalizadas principales
    path('login/', custom_login, name='login'),
    path('registro/', registro, name='registro'),
    path('signup/', registro, name='signup'),
    path('', include('core.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configuración para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # También servir desde STATICFILES_DIRS
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()


