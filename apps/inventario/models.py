from django.db import models
from apps.core.models import Almacen
from django.conf import settings
from decimal import Decimal

# Create your models here.

class Productor(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    region = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Productores"

    def __str__(self):
        return f"{self.nombre} ({self.pais})"
    
class Producto(models.Model):
    TIPO_CHOICES = [
        ('vino', 'Vino'),
        ('destilado', 'Destilado'),
    ]
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    productor = models.ForeignKey('Productor', on_delete=models.SET_NULL, null=True, blank=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    margen = models.DecimalField(max_digits=5, decimal_places=2, default=1.20)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(default=True)
    codigo_barras = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['nombre']

    def calcular_precio_venta(self, save=True):
        if self.precio_compra and self.margen:
            self.precio_venta = Decimal(self.precio_compra) * Decimal(self.margen)
            if save:
                self.save(update_fields=["precio_venta"])
        return self.precio_venta

    def __str__(self):
        return self.nombre
    
class Vino(Producto):
    SUBTIPO_CHOICES = [
        ('tinto', 'Tinto'),
        ('blanco', 'Blanco'),
        ('rosado', 'Rosado'),
        ('espumoso', 'Espumoso'),
    ]
    subtipo = models.CharField(max_length=20, choices=SUBTIPO_CHOICES)
    denominacion_origen = models.CharField(max_length=100, blank=True, null=True)
    uvas = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Vinos"

class Destilado(Producto):
    SUBTIPO_CHOICES = [
        ('whisky', 'Whisky'),
        ('ron', 'Ron'),
        ('vodka', 'Vodka'),
    ]
    subtipo = models.CharField(max_length=20, choices=SUBTIPO_CHOICES)
    volumen_cl = models.PositiveIntegerField(help_text="Volumen en centilitros")
    grado_alcohol = models.DecimalField(max_digits=5, decimal_places=2, help_text="Grado alcohólico %")
    
    class Meta:
        verbose_name_plural = "Destilados"
    
class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('producto', 'almacen')

    def __str__(self):
        if self.almacen:
            return f"{self.producto.nombre} ({self.almacen.nombre}) — {self.cantidad}"
        return f"{self.producto.nombre} — {self.cantidad}"


class TransferenciaStock(models.Model):
    origen = models.ForeignKey(Almacen, related_name='transferencias_salida', on_delete=models.CASCADE)
    destino = models.ForeignKey(Almacen, related_name='transferencias_entrada', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} — {self.cantidad} de {self.origen} a {self.destino}"
    
class MovimientoStock(models.Model):
    TIPO_CHOICES = (
        ('venta', 'Venta'),
        ('transferencia', 'Transferencia'),
        ('ajuste', 'Ajuste'),
    )
    producto = models.ForeignKey("inventario.Producto", on_delete=models.PROTECT, null=True, blank=True)
    almacen = models.ForeignKey("core.Almacen", on_delete=models.PROTECT)
    cantidad = models.IntegerField()  # negativa en venta
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    venta = models.ForeignKey("ventas.Venta", null=True, blank=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

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

