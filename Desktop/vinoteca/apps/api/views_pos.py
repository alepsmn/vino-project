from rest_framework import viewsets, permissions
from apps.ventas.models import Venta
from apps.inventario.models import Stock
from .serializers_ventas import VentaSerializer
from django.db import transaction

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all().select_related('tienda', 'empleado')
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]