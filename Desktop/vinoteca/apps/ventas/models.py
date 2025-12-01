from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth.models import User
from apps.core.models import Tienda, Empleado
from apps.inventario.models import Producto, Stock, MovimientoStock  # añade Stock y MovimientoStock si no estaban

# Create your models here.

class Venta(models.Model):
    METODOS_PAGO = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
        ("otro", "Otro"),
    ]

    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    tienda = models.ForeignKey(Tienda, on_delete=models.SET_NULL, null=True, blank=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Descuento global en porcentaje sobre el total",
    )
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default="tarjeta")

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.id} — {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    @transaction.atomic
    def descontar_stock(self, almacen, usuario=None):
        """
        Punto ÚNICO de descuento de stock para esta venta.
        """
        for detalle in self.detalles.all().select_related("producto"):
            stock = (
                detalle.producto.stock_set
                .select_for_update()
                .filter(almacen=almacen)
                .first()
            )

            if not stock:
                raise ValueError(f"No hay stock para {detalle.producto.nombre}")

            if stock.cantidad < detalle.cantidad:
                raise ValueError(f"Stock insuficiente para {detalle.producto.nombre}")

            # actualizar stock
            stock.cantidad -= detalle.cantidad
            stock.save(update_fields=["cantidad"])

            # registrar movimiento
            MovimientoStock.objects.create(
                producto=detalle.producto,
                almacen=almacen,
                cantidad=-detalle.cantidad,
                tipo="venta",
                venta=self,
                usuario=usuario,
            )

class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        related_name="detalles",
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
