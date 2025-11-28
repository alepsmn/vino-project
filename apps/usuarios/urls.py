from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("perfil/", views.perfil_datos, name="perfil_datos"),
    path("perfil/pedidos/", views.perfil_pedidos, name="perfil_pedidos"),
    path("perfil/favoritos/", views.perfil_favoritos, name="perfil_favoritos"),
    path("perfil/colecciones/", views.perfil_colecciones, name="perfil_colecciones"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro, name="registro"),
]
