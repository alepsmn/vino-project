from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.inventario.models import Productor
from apps.api.serializers import ProductorSerializer

class ProductorViewSet(ReadOnlyModelViewSet):
    queryset = Productor.objects.all()
    serializer_class = ProductorSerializer
