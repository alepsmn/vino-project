from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .productores import ProductorViewSet
from .categorias import CategoriaViewSet
from .productos import ProductoViewSet
from .stock import StockViewSet, StockMinimalView
from .movimientos import MovimientoStockViewSet, MovimientoStockCreateView
from .ventas import VentaViewSet

router = DefaultRouter()
router.register("productores", ProductorViewSet)
router.register("categorias", CategoriaViewSet)
router.register("productos", ProductoViewSet)
router.register("stock", StockViewSet)
router.register("movimientos", MovimientoStockViewSet)
router.register("ventas", VentaViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("stock-minimal/", StockMinimalView.as_view(), name="stock-minimal"),
    path("movimientos/create/", MovimientoStockCreateView.as_view(), name="movimiento-create"),
]
