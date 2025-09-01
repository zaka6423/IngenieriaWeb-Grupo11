# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class Comedor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='images/', blank=True)
    barrio = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    capacidad = models.IntegerField()

    def __str__(self):
        return self.nombre

class UserProfile(models.Model):
    """
    Perfil de usuario extendido para manejar validación de email
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
