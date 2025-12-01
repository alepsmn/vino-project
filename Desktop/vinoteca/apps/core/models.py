from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Almacen(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Almacenes"

    def __str__(self):
        return self.nombre

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    codigo = models.CharField(max_length=20, unique=True)
    almacen = models.ForeignKey(Almacen, on_delete=models.SET_NULL, null=True, related_name="tiendas")

    def save(self, *args, **kwargs):
        if not self.codigo:
            base = (self.nombre or "tienda").lower().replace(" ", "")
            slug = base
            n = 1
            while Tienda.objects.filter(codigo=slug).exists():
                slug = f"{base}{n}"
                n += 1
            self.codigo = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} — {self.tienda.nombre}"