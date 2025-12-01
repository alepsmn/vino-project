from django.shortcuts import render
from apps.inventario.models import Producto, Productor

def index(request):
    productos_destacados = Producto.objects.all()[:6]
    productores = Productor.objects.all()[:6]
    return render(request, "home/index.html", {
        "productos_destacados": productos_destacados,
        "productores": productores,
    })

def nosotros(request):
    return render(request, "home/nosotros.html")

def ubicacion(request):
    return render(request, "home/ubicacion.html")

def contacto(request):
    return render(request, "home/contacto.html")
