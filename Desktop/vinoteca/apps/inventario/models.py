from django.db import models
from apps.core.models import Almacen
from django.conf import settings
from decimal import Decimal, InvalidOperation
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# Create your models here.

# -------------------------
# PRODUCTOR
# -------------------------
class Productor(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    region = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Productores"

    def __str__(self):
        return f"{self.nombre} ({self.pais})"


# -------------------------
# CATEGORÍA
# -------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    padre = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="hijos",
    )

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


# -------------------------
# ATRIBUTO
# -------------------------
class Atributo(models.Model):
    TIPO = [
        ("texto", "Texto"),
        ("entero", "Entero"),
        ("decimal", "Decimal"),
        ("booleano", "Booleano"),
        ("opcion", "Opción"),
    ]

    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    tipo_dato = models.CharField(max_length=20, choices=TIPO)
    categoria = models.ForeignKey(
        Categoria,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Si es NULL, atributo global",
    )

    def __str__(self):
        return self.nombre


# -------------------------
# VALOR DE ATRIBUTO (para tipo=opción)
# -------------------------
class ValorAtributo(models.Model):
    atributo = models.ForeignKey(
        Atributo,
        on_delete=models.CASCADE,
        related_name="valores",
    )
    valor = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.atributo.nombre}: {self.valor}"


# -------------------------
# PRODUCTO
# -------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )
    productor = models.ForeignKey(
        Productor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )

    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    margen = models.DecimalField(max_digits=5, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # slug único
        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            n = 1
            while Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug

        # validar precio_compra y margen
        if self.precio_compra is None or self.margen is None:
            raise ValidationError("precio_compra y margen son obligatorios.")

        try:
            pc = Decimal(self.precio_compra)
            mg = Decimal(self.margen)
        except InvalidOperation:
            raise ValidationError("precio_compra o margen inválidos.")

        if pc <= 0:
            raise ValidationError("precio_compra debe ser > 0.")

        if mg <= 0:
            raise ValidationError("margen debe ser > 0.")

        # recálculo automático del precio_venta
        pv = pc * mg
        if pv <= 0:
            raise ValidationError("precio_venta resultante inválido.")

        self.precio_venta = pv.quantize(Decimal("0.01"))

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

# -------------------------
# PRODUCTO-ATRIBUTO
# -------------------------
class ProductoAtributo(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="atributos",
    )
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE)

    valor_texto = models.CharField(max_length=255, null=True, blank=True)
    valor_entero = models.IntegerField(null=True, blank=True)
    valor_decimal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    valor_booleano = models.BooleanField(null=True, blank=True)
    valor_opcion = models.ForeignKey(
        ValorAtributo,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ("producto", "atributo")

    def __str__(self):
        return f"{self.producto.nombre} — {self.atributo.nombre}"

    def clean(self):
        tipo = self.atributo.tipo_dato
        campos = {
            "texto": self.valor_texto,
            "entero": self.valor_entero,
            "decimal": self.valor_decimal,
            "booleano": self.valor_booleano,
            "opcion": self.valor_opcion,
        }

        # valor correcto obligatorio
        if campos[tipo] in (None, "", False):
            raise ValidationError(f"El atributo '{self.atributo.nombre}' requiere valor de tipo '{tipo}'")

        # otros campos deben estar vacíos
        for t, v in campos.items():
            if t != tipo and v not in (None, "", False):
                raise ValidationError(f"'{self.atributo.nombre}' no puede tener valor en tipo '{t}'")

    def save(self, *args, **kwargs):
        self.full_clean()  # ejecuta clean()
        super().save(*args, **kwargs)


# -------------------------
# STOCK
# -------------------------
class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("producto", "almacen")

    def __str__(self):
        return f"{self.producto.nombre} ({self.almacen.nombre}) — {self.cantidad}"


# -------------------------
# TRANSFERENCIA
# -------------------------
class TransferenciaStock(models.Model):
    origen = models.ForeignKey(Almacen, related_name="transferencias_salida", on_delete=models.CASCADE)
    destino = models.ForeignKey(Almacen, related_name="transferencias_entrada", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} — {self.cantidad} de {self.origen} a {self.destino}"


# -------------------------
# MOVIMIENTO DE STOCK
# -------------------------
class MovimientoStock(models.Model):
    TIPO_CHOICES = (
        ("venta", "Venta"),
        ("transferencia", "Transferencia"),
        ("ajuste", "Ajuste"),
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT)
    cantidad = models.IntegerField()  # negativo en venta
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    venta = models.ForeignKey("ventas.Venta", null=True, blank=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]


# -------------------------
# MENÚ LATERAL
# -------------------------
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
    enlace_personalizado = models.CharField(max_length=200, blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subentradas",
    )

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.nombre
