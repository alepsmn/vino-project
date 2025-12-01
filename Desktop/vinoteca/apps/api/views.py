# apps/api/views.py

from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated


from apps.inventario.models import Productor, Categoria, Producto, Stock, MovimientoStock
from apps.ventas.models import Venta
from apps.api.permissions import IsEmpleado

from .serializers import (
    ProductorSerializer,
    CategoriaSerializer,
    ProductoSerializer,
    StockSerializer,
    StockMinimalSerializer,
    MovimientoStockSerializer,
    MovimientoStockInSerializer,
    VentaSerializer,
)


class ProductorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Productor.objects.all()
    serializer_class = ProductorSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsEmpleado]
    serializer_class = StockSerializer

    def get_queryset(self):
        empleado = self.request.user.empleado
        almacen = empleado.tienda.almacen
        return Stock.objects.filter(almacen=almacen).select_related("producto", "almacen").order_by("id")

class StockMinimalView(generics.ListAPIView):
    permission_classes = [IsEmpleado]
    serializer_class = StockMinimalSerializer
    pagination_class = None

    def get_queryset(self):
        empleado = self.request.user.empleado
        almacen = empleado.tienda.almacen
        return Stock.objects.filter(almacen=almacen).select_related("producto")

class MovimientoStockViewSet(viewsets.ModelViewSet):
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

class VentaViewSet(viewsets.ModelViewSet):
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

'''MUTACIONES'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MovimientoStockCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MovimientoStockInSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            mov = serializer.save()
            return Response(MovimientoStockSerializer(mov).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)