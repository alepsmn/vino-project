from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.inventario.models import MovimientoStock
from apps.api.serializers import (
    MovimientoStockSerializer,
    MovimientoStockInSerializer
)

class MovimientoStockViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        empleado = self.request.user.empleado
        almacen = empleado.tienda.almacen
        return (
            MovimientoStock.objects
            .filter(almacen=almacen)
            .select_related("producto", "almacen", "venta", "usuario")
            .order_by("-fecha")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MovimientoStockInSerializer
        return MovimientoStockSerializer

class MovimientoStockCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MovimientoStockInSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            mov = serializer.save()
            return Response(
                MovimientoStockSerializer(mov).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
