from django.shortcuts import render, get_object_or_404
from .models import Vino

# Create your views here.

def lista_vinos(request):
    q = request.GET.get("q", "")
    vinos = Vino.objects.select_related('productor').filter(activo=True)
    if q:
        vinos = vinos.filter(nombre__icontains=q) | vinos.filter(productor__nombre__icontains=q)
    return render(request, 'inventario/lista_vinos.html', {'vinos': vinos})


def detalle_vino(request, id):
    vino = get_object_or_404(Vino.objects.select_related('productor'), pk=id)
    return render(request, 'inventario/detalle_vino.html', {'vino': vino})
