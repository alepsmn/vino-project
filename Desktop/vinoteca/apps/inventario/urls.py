# apps/inventario/urls.py
from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("catalogo/", views.catalogo, name="catalogo"),
    path("<int:id>/", views.detalle_producto, name="detalle_producto"),
]