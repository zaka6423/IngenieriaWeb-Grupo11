# models.py
from django.db import models

class Comedor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='comedores/')
    barrio = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    capacidad = models.IntegerField()

    def __str__(self):
        return self.nombre