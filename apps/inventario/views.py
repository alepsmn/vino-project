from django.shortcuts import render, get_object_or_404
from .models import Vino

# Create your views here.

def lista_vinos(request):
    vinos = Vino.objects.select_related('productor').filter(activo=True)
    return render(request, 'inventario/lista_vinos.html', {'vinos': vinos})

def detalle_vino(request, id):
    vino = get_object_or_404(Vino, pk=id)
    return render(request, 'inventario/detalle_vino.html', {'vino': vino})