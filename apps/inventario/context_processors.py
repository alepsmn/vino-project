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
    # Toma el primer menú activo, si hay más de uno no rompe
    menu = (
        MenuLateral.objects.filter(activo=True)
        .prefetch_related("entradas__subentradas")
        .first()
    )

    if not menu:
        # si no hay ninguno activo, no muestra nada
        return {"menu_estructurado": []}

    raiz = [
        {"obj": e, "sub": obtener_subentradas(e)}
        for e in menu.entradas.filter(padre__isnull=True, activo=True).order_by("orden")
    ]
    return {"menu_estructurado": raiz}
