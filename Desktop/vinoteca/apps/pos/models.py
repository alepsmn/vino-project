from django.db import models
from django.conf import settings
from apps.core.models import Tienda

# Create your models here.

class Terminal(models.Model):
    nombre = models.CharField(max_length=50)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name='terminales')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tienda} — {self.nombre}"

class VentaPOS(models.Model):
    terminal = models.ForeignKey(Terminal, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sincronizada = models.BooleanField(default=False)

    def __str__(self):
        return f"POS {self.terminal.nombre} — {self.fecha:%Y-%m-%d %H:%M}"