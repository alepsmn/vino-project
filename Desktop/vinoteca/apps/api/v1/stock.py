from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView
from apps.inventario.models import Stock
from apps.api.serializers import StockSerializer, StockMinimalSerializer
from apps.api.permissions import IsEmpleado

class StockViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsEmpleado]
    serializer_class = StockSerializer

    def get_queryset(self):
        empleado = self.request.user.empleado
        almacen = empleado.tienda.almacen
        return (
            Stock.objects
            .filter(almacen=almacen)
            .select_related("producto", "almacen")
            .order_by("id")
        )

class StockMinimalView(ListAPIView):
    permission_classes = [IsEmpleado]
    serializer_class = StockMinimalSerializer
    pagination_class = None

    def get_queryset(self):
        empleado = self.request.user.empleado
        almacen = empleado.tienda.almacen
        return (
            Stock.objects
            .filter(almacen=almacen)
            .select_related("producto")
        )
