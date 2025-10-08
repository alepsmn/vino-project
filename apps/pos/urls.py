from django.urls import path
from . import views

app_name = "pos"

urlpatterns = [
    path("login/", views.login_pos, name="login_pos"),
    path("logout/", views.logout_pos, name="logout_pos"),
    path("", views.panel_pos, name="panel_pos"),
    path("venta/<int:vino_id>/", views.registrar_venta_pos, name="registrar_venta"),
    path("resumen/", views.resumen_pos, name="resumen_pos"),
    path("buscar/", views.buscar_codigo, name="buscar_codigo"),
]
