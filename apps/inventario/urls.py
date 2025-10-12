from django.urls import path
from. import views

app_name = "inventario"

urlpatterns = [
    path('', views.lista_vinos, name='lista_vinos'),
    path('<int:id>/', views.detalle_vino, name='detalle_vino'),
    path('tipo/<str:tipo>/', views.filtrar_tipo, name='filtrar_tipo'),
    path('tipo/<str:tipo>/<str:denom>/', views.filtrar_tipo_denominacion, name='filtrar_tipo_denominacion'),
    path("region/<str:region>/", views.filtrar_region, name="filtrar_region"),
]