from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.inventario.models import Producto
from apps.api.serializers import ProductoSerializer

class ProductoViewSet(ReadOnlyModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
