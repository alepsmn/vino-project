# apps/inventario/context_processors.py
from .models import MenuLateral

def obtener_subentradas(entrada):
    return [
        {
            "obj": sub,
            "sub": obtener_subentradas(sub)
        }
        for sub in entrada.subentradas.filter(activo=True).order_by("orden")
    ]

def menu_lateral_context(request):
    try:
        menu = MenuLateral.objects.prefetch_related("entradas__subentradas").get(activo=True)
        raiz = [
            {"obj": e, "sub": obtener_subentradas(e)}
            for e in menu.entradas.filter(padre__isnull=True, activo=True).order_by("orden")
        ]
    except MenuLateral.DoesNotExist:
        raiz = []
    return {"menu_estructurado": raiz}
