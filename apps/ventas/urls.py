from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:vino_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:vino_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('carrito/restar/<int:vino_id>/', views.restar_carrito, name='restar_carrito'),
]
