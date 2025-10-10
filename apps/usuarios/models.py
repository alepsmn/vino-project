from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class PerfilCliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, default="España")

    @property
    def es_mayor_edad(self):
        if not self.fecha_nacimiento:
            return False
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return edad >= 18

    def __str__(self):
        return self.user.username