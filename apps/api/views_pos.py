from rest_framework import viewsets, permissions
from apps.ventas.models import Venta, DetalleVenta
from apps.inventario.models import Stock
from .serializers_ventas import VentaSerializer
from django.db import transaction

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all().select_related('tienda', 'empleado')
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        empleado = getattr(self.request.user, 'empleado', None)
        venta = serializer.save(
            empleado=empleado if empleado else None,
            tienda=getattr(empleado, "tienda", None),
        )

        # Almacén por defecto: Central
        from apps.core.models import Almacen
        almacen, _ = Almacen.objects.get_or_create(nombre="Central", defaults={"ubicacion": "Madrid"})

        # Actualizar stock por cada detalle
        for detalle in venta.detalles.all():
            try:
                stock = Stock.objects.get(vino=detalle.vino, almacen=almacen)
                stock.cantidad = max(0, stock.cantidad - detalle.cantidad)
                stock.save(update_fields=["cantidad"])
            except Stock.DoesNotExist:
                Stock.objects.create(
                    vino=detalle.vino,
                    almacen=almacen,
                    cantidad=max(0, -detalle.cantidad)
                )
