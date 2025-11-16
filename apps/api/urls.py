from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    ProductoViewSet,
    VinoViewSet,
    DestiladoViewSet,
    ProductorViewSet,
    StockViewSet,
)
from .views_pos import VentaViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'vinos', VinoViewSet)
router.register(r'destilados', DestiladoViewSet)
router.register(r'productores', ProductorViewSet)
router.register(r'stock', StockViewSet)
router.register(r'ventas', VentaViewSet)

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token_auth'),
]

urlpatterns += router.urls