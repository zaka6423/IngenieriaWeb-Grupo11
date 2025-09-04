# models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Comedor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='images/', blank=True)
    barrio = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    capacidad = models.IntegerField()

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Guardar el modelo
        super().save(*args, **kwargs)
        
        # Log de guardado
        if self.imagen:
            print(f"Comedor saved: {self.nombre} (ID: {self.id}) - Image: {self.imagen.url}")

class UserProfile(models.Model):
    """
    Perfil de usuario extendido para manejar validación de email
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_code = models.CharField(max_length=10, blank=True, null=True)  # Nuevo campo

    def __str__(self):
        return f"Perfil de {self.user.username}"

class PendingRegistration(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password_hash = models.CharField(max_length=128)  # contraseña ya hasheada
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    tries = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.email} (pendiente)"

