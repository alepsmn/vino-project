from rest_framework import viewsets, filters
from apps.inventario.models import Producto, Vino, Destilado, Productor, Stock
from .serializers import (
    ProductoSerializer, VinoSerializer,
    DestiladoSerializer, ProductorSerializer,
    StockSerializer
)

# Create your views here.
# Base de productos (todos)
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'tipo', 'productor__nombre', 'pais']


# Vinos específicos
class VinoViewSet(viewsets.ModelViewSet):
    queryset = Vino.objects.select_related('productor').all().order_by('nombre')
    serializer_class = VinoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'subtipo', 'productor__nombre', 'denominacion_origen', 'uvas']


# Destilados específicos
class DestiladoViewSet(viewsets.ModelViewSet):
    queryset = Destilado.objects.select_related('productor').all().order_by('nombre')
    serializer_class = DestiladoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'subtipo', 'productor__nombre']


# Productores
class ProductorViewSet(viewsets.ModelViewSet):
    queryset = Productor.objects.all().order_by('nombre')
    serializer_class = ProductorSerializer


# Stock (inventario)
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('producto', 'almacen').all().order_by('producto__nombre')
    serializer_class = StockSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['producto__nombre', 'almacen__nombre']
