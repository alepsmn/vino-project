from rest_framework.viewsets import ModelViewSet
from apps.inventario.models import Stock
from apps.api.serializers import StockSerializer

class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
