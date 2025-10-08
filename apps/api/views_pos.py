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
        if empleado:
            venta = serializer.save(empleado=empleado, tienda=empleado.tienda)
        else:
            venta = serializer.save()

        # Actualizar stock por cada detalle de venta
        for detalle in venta.detalles.all():
            try:
                stock = Stock.objects.get(vino=detalle.vino, tienda=venta.tienda)
                stock.cantidad = max(0, stock.cantidad - detalle.cantidad)
                stock.save(update_fields=["cantidad"])
            except Stock.DoesNotExist:
                # Si no existe el registro de stock, se crea con cantidad negativa (pendiente)
                Stock.objects.create(
                    vino=detalle.vino,
                    tienda=venta.tienda,
                    cantidad=max(0, -detalle.cantidad)
                )
