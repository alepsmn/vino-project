from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Vino

# Create your views here.

def lista_vinos(request):
    vinos = Vino.objects.all()
    q = request.GET.get('q')
    if q:
        vinos = vinos.filter(
            Q(nombre__icontains=q) |
            Q(tipo__icontains=q) |
            Q(productor__nombre__icontains=q) |
            Q(denominacion_origen__icontains=q) |
            Q(uvas__icontains=q)
        )
    return render(request, 'inventario/lista_vinos.html', {'vinos': vinos})

def detalle_vino(request, id):
    vino = get_object_or_404(Vino.objects.select_related('productor'), pk=id)
    return render(request, 'inventario/detalle_vino.html', {'vino': vino})

def filtrar_tipo(request, tipo):
    vinos = Vino.objects.filter(tipo=tipo)
    return render(request, 'inventario/lista_vinos.html', {'vinos': vinos, 'tipo': tipo})

def filtrar_tipo_denominacion(request, tipo, denom):
    vinos = Vino.objects.filter(tipo=tipo, denominacion_origen=denom)
    return render(request, 'inventario/lista_vinos.html', {
        'vinos': vinos,
        'tipo': tipo,
        'denominacion': denom
    })

def filtrar_region(request, region):
    vinos = Vino.objects.filter(denominacion_origen=region)
    return render(request, "inventario/lista_vinos.html", {"vinos": vinos, "region": region})
