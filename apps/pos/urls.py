from django.urls import path
from . import views, views_carrito

app_name = "pos"

urlpatterns = [
    path("login/", views.login_pos, name="login_pos"),
    path("logout/", views.logout_pos, name="logout_pos"),
    path("", views.panel_pos, name="panel_pos"),
    path("resumen/", views.resumen_pos, name="resumen_pos"),
    path("buscar/", views.buscar_codigo, name="buscar_codigo"),

    # Carrito POS
    path("carrito/", views_carrito.ver_carrito, name="ver_carrito"),
    path('carrito/agregar/<int:producto_id>/', views_carrito.agregar_carrito, name='agregar_carrito'),
    path("carrito/eliminar/<int:vino_id>/", views_carrito.eliminar_carrito, name="eliminar_carrito"),
    path("carrito/limpiar/", views_carrito.limpiar_carrito, name="limpiar_carrito"),
    path("carrito/finalizar/", views_carrito.finalizar_venta, name="finalizar_venta"),

    # Inventario
    path("inventario/", views.inventario_pos, name="inventario_pos"),
]
