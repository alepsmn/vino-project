from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import VinoViewSet, ProductorViewSet, StockViewSet
from .views_pos import VentaViewSet

router = DefaultRouter()
router.register(r'vinos', VinoViewSet)
router.register(r'productores', ProductorViewSet)
router.register(r'stock', StockViewSet)
router.register(r'ventas', VentaViewSet)  # registra aquí las ventas

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token_auth'),
]
urlpatterns += router.urls