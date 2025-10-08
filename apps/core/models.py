from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    codigo = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} — {self.tienda.nombre}"