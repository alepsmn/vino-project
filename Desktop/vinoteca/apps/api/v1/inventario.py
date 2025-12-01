from rest_framework.viewsets import ModelViewSet
from apps.inventario.models import Categoria, Productor
from apps.api.serializers import CategoriaSerializer, ProductorSerializer

class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductorViewSet(ModelViewSet):
    queryset = Productor.objects.all()
    serializer_class = ProductorSerializer
