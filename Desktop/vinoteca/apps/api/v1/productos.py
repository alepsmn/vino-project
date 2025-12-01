from rest_framework.viewsets import ModelViewSet
from apps.inventario.models import Producto
from apps.api.serializers import ProductoSerializer  # tu serializer actual

class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
