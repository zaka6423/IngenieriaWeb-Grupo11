# models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

import uuid
import secrets

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

    email_verification_code = models.CharField(max_length=10, blank=True, null=True)
    verification_expires_at = models.DateTimeField(blank=True, null=True)
    verification_tries = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def set_new_code(self, minutes=15):
        """Genera un nuevo código y reinicia intentos."""
        self.email_verification_code = f"{secrets.randbelow(10 ** 6):06d}"
        self.verification_expires_at = timezone.now() + timedelta(minutes=minutes)
        self.verification_tries = 0

    def code_is_valid(self, code: str) -> bool:
        """Verifica si el código es válido y no está vencido."""
        if not self.email_verification_code or not self.verification_expires_at:
            return False
        if timezone.now() > self.verification_expires_at:
            return False
        return secrets.compare_digest(code, self.email_verification_code)

