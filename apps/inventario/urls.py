from django.urls import path
from. import views

app_name = "inventario"

urlpatterns = [
    path('', views.lista_vinos, name='lista_vinos'),
    path('<int:id>/', views.detalle_vino, name='detalle_vino'),
]