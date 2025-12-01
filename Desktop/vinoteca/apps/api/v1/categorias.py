from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.inventario.models import Categoria
from apps.api.serializers import CategoriaSerializer

class CategoriaViewSet(ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
