from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path("carrito/agregar/<int:producto_id>/", views.agregar_carrito, name="agregar_carrito"),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/restar/<int:producto_id>/', views.restar_carrito, name='restar_carrito'),

    path('confirmacion/', views.confirmacion_view, name='confirmacion'),
    path('tramitar/', views.tramitar_pedido, name='tramitar_pedido'),
    path('checkout/', views.checkout, name='checkout'),
    path('pago/<int:venta_id>/', views.pago_view, name='pago'),

]
 