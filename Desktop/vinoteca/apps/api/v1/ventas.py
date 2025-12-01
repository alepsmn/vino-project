from rest_framework.viewsets import ModelViewSet
from apps.ventas.models import Venta
from apps.api.serializers import VentaSerializer

class VentaViewSet(ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
