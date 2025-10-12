from django.db import models
from apps.core.models import Almacen

# Create your models here.

class Productor(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    region = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Productores"

    def __str__(self):
        return f"{self.nombre} ({self.pais})"
    
class Vino(models.Model):
    TIPO_CHOICES = [
        ('tinto', 'Tinto'),
        ('blanco', 'Blanco'),
        ('rosado', 'Rosado'),
        ('espumoso', 'Espumoso'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE, related_name='vinos')
    denominacion_origen = models.CharField(max_length=100, blank=True, null=True)
    uvas = models.CharField(max_length=200, blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=8, decimal_places=2)
    margen = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje sobre el precio de compra")
    precio_venta = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    codigo_barras = models.CharField(max_length=64, unique=True, null=True,
        blank=True,
        help_text="Código de barras o identificador único del vino"
    )


    class Meta:
        verbose_name_plural = "Vinos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    
class Stock(models.Model):
    vino = models.ForeignKey(Vino, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, null=True, blank=True,)  # ← permite nulos durante la migración inicial
    cantidad = models.PositiveIntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vino', 'almacen')

    def __str__(self):
        return f"{self.vino.nombre} ({self.tienda.nombre}) — {self.cantidad}"
    
class TransferenciaStock(models.Model):
    origen = models.ForeignKey(Almacen, related_name='transferencias_salida', on_delete=models.CASCADE)
    destino = models.ForeignKey(Almacen, related_name='transferencias_entrada', on_delete=models.CASCADE)
    vino = models.ForeignKey(Vino, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vino.nombre} — {self.cantidad} de {self.origen} a {self.destino}"

'''
Menu lateral web
'''    
class MenuLateral(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Menú lateral"
        verbose_name_plural = "Menús laterales"

    def __str__(self):
        return self.nombre

class EntradaMenu(models.Model):
    menu = models.ForeignKey(MenuLateral, on_delete=models.CASCADE, related_name="entradas")
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=50,
        choices=[
            ("tipo", "Tipo"),
            ("region", "Denominación / Zona"),
            ("pais", "País de origen"),
            ("variedad", "Variedad"),
            ("elaborador", "Elaborador"),
            ("custom", "Enlace personalizado"),
        ],
        default="custom",
    )
    enlace_personalizado = models.CharField(
        max_length=200, blank=True, null=True, help_text="Usar si tipo='Enlace Personalizado'"
    )
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    # Nueva clave recursiva
    padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subentradas"
    )

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.nombre}"

