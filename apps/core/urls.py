from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("nosotros/", views.nosotros, name="nosotros"),
    path("ubicacion/", views.ubicacion, name="ubicacion"),
    path("contacto/", views.contacto, name="contacto"),
]
