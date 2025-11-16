from django.db import transaction
from decimal import Decimal
from rest_framework import serializers
from apps.ventas.models import Venta, DetalleVenta
from apps.inventario.models import Producto, Stock, MovimientoStock

class DetalleVentaInSerializer(serializers.Serializer):
    producto = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaInSerializer(many=True, write_only=True)

    class Meta:
        model = Venta
        fields = ("id", "descuento", "metodo_pago", "detalles")

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        empleado = getattr(user, "empleado", None)
        tienda = getattr(empleado, "tienda", None)

        if not tienda:
            raise serializers.ValidationError("El empleado no tiene una tienda asignada.")

        almacen = getattr(tienda, "almacen", None)
        if not almacen:
            raise serializers.ValidationError("La tienda no tiene un almacén asociado.")

        detalles_in = validated_data.pop("detalles", [])
        descuento = Decimal(validated_data.get("descuento") or 0)

        venta = Venta.objects.create(
            tienda=tienda,
            empleado=empleado,
            descuento=descuento,
            metodo_pago=validated_data.get("metodo_pago", "POS"),
            total=Decimal("0.00"),
            pagado=False,
        )

        total_bruto = Decimal("0.00")

        for item in detalles_in:
            producto = Producto.objects.select_for_update().get(pk=item["producto"])
            stock = Stock.objects.filter(producto=producto, almacen=almacen).first()

            if not stock:
                raise serializers.ValidationError(f"Sin stock disponible para {producto.nombre}")
            if stock.cantidad < item["cantidad"]:
                raise serializers.ValidationError(f"Stock insuficiente para {producto.nombre}")

            cantidad = item["cantidad"]
            precio_unitario = producto.precio_venta
            subtotal = (precio_unitario * cantidad).quantize(Decimal("0.01"))

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )

            stock.cantidad -= cantidad
            stock.save(update_fields=["cantidad"])

            MovimientoStock.objects.create(
                producto=producto,
                almacen=almacen,
                cantidad=-cantidad,
                tipo="venta",
                venta=venta,
                usuario=user,
            )

            total_bruto += subtotal

        total = (total_bruto * (Decimal("1") - descuento / Decimal("100"))).quantize(Decimal("0.01"))
        venta.total = total
        venta.pagado = True
        venta.save(update_fields=["total", "pagado"])

        return venta
