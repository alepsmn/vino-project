from rest_framework.viewsets import ModelViewSet
from apps.ventas.models import Venta
from apps.api.serializers import VentaSerializer

class VentaViewSet(ModelViewSet):
    serializer_class = VentaSerializer
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Venta.objects.none()

        empleado = getattr(user, "empleado", None)
        if not empleado or not empleado.tienda:
            return Venta.objects.none()

        tienda = empleado.tienda

        return (
            Venta.objects
            .filter(tienda=tienda)
            .select_related("tienda", "empleado")
            .prefetch_related("detalles__producto")
        )
