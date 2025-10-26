# models.py
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets

class Comedor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='images/', blank=True)
    barrio = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    capacidad = models.IntegerField()

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comedores",
        verbose_name="Dueño del comedor",
        null=True, blank=True
    )

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Guardar el modelo
        super().save(*args, **kwargs)

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

class TipoPublicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    descripcion = models.CharField(max_length=255, db_column='Descripcion')

    class Meta:
        db_table = 'TipoPublicacion'

class Publicacion(models.Model):
    id_comedor = models.ForeignKey('Comedor', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    id_tipo_publicacion = models.ForeignKey("TipoPublicacion", on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True)

    fecha_inicio = models.DateTimeField(default=timezone.now)  # se setea al crear
    fecha_fin = models.DateTimeField(null=True, blank=True)  # lo carga el usuario

    def __str__(self):
        return self.titulo

class PublicacionArticulo(models.Model):
    id_publicacion = models.ForeignKey('Publicacion', on_delete=models.CASCADE)
    nombre_articulo = models.CharField(max_length=255)

    class Meta:
        unique_together = ('id_publicacion', 'nombre_articulo')

    def __str__(self):
        return f"{self.nombre_articulo} ({self.id_publicacion.titulo})"

# models.py
class Favoritos(models.Model):
    id_usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='IdUsuario')
    id_comedor = models.ForeignKey(Comedor, on_delete=models.CASCADE, db_column='IdComedor')
    fecha_alta = models.DateTimeField(db_column='FechaAlta', auto_now_add=True)

    class Meta:
        db_table = 'Favoritos'
        unique_together = ('id_usuario', 'id_comedor')

class Donacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='IdDonacion')
    id_usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='IdUsuario')
    id_comedor = models.ForeignKey(Comedor, on_delete=models.CASCADE, db_column='IdComedor')
    id_publicacion = models.ForeignKey('Publicacion', on_delete=models.CASCADE, db_column='IdPublicacion')
    fecha_alta = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Donacion'

    def __str__(self):
        return f"Donación {self.id} de {self.usuario} en {self.comedor}"

class DonacionItem(models.Model):
    id_donacion = models.ForeignKey(Donacion, on_delete=models.CASCADE, related_name="items")
    nombre_articulo = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('id_donacion', 'nombre_articulo')

    def __str__(self):
        return f"{self.nombre_articulo} x{self.cantidad}"
