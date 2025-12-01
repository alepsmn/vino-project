from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto

# Create your views here.

def catalogo(request):
    productos = Producto.objects.filter(activo=True)

    tipo = request.GET.get("tipo")
    q = request.GET.get("q")
    pais = request.GET.get("pais")
    productor = request.GET.get("productor")

    if tipo:
        productos = productos.filter(tipo=tipo)
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q)
            | Q(productor__nombre__icontains=q)
            | Q(denominacion_origen__icontains=q)
        )
    if pais:
        productos = productos.filter(pais__icontains=pais)
    if productor:
        productos = productos.filter(productor__nombre__icontains=productor)

    contexto = {
        "productos": productos.order_by("nombre"),
        "tipo": tipo or "todos",
        "q": q or "",
    }
    return render(request, "inventario/catalogo.html", contexto)

def detalle_producto(request, id):
    producto = get_object_or_404(Producto.objects.select_related('productor'), pk=id)
    return render(request, 'inventario/detalle_producto.html', {'producto': producto})

# hay q actualizar estos filtros
def filtrar_tipo(request, tipo):
    productos = Producto.objects.filter(tipo=tipo)
    return render(request, 'inventario/lista_vinos.html', {'productos': productos, 'tipo': tipo})

def filtrar_tipo(request, tipo):
    productos = Producto.objects.filter(tipo=tipo)
    return render(request, 'inventario/lista_vinos.html', {'productos': productos, 'tipo': tipo})

def filtrar_region(request, region):
    productos = Producto.objects.filter(denominacion_origen=region)
    return render(request, "inventario/lista_vinos.html", {"vinos": productos, "region": region})


