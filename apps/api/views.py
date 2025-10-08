from rest_framework import viewsets, filters
from apps.inventario.models import Vino, Productor, Stock
from .serializers import VinoSerializer, ProductorSerializer, StockSerializer

# Create your views here.

class VinoViewSet(viewsets.ModelViewSet):
    queryset = Vino.objects.all()
    serializer_class = VinoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'tipo', 'productor__nombre', 'denominacion_origen', 'uvas']

class ProductorViewSet(viewsets.ModelViewSet):
    queryset = Productor.objects.all()
    serializer_class = ProductorSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('vino').all()
    serializer_class = StockSerializer