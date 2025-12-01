from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.inventario.models import MovimientoStock
from apps.api.serializers import MovimientoStockSerializer

class MovimientoStockViewSet(ReadOnlyModelViewSet):
    queryset = MovimientoStock.objects.all()
    serializer_class = MovimientoStockSerializer
