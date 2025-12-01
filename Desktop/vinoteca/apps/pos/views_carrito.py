# apps/pos/views_carrito.py

from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import redirect, render
from django.contrib import messages

from apps.pos.utils.carrito_pos import CarritoPOS
from apps.pos.api_client import POSAPIClient
from apps.pos.decorators import empleado_required


@empleado_required
def agregar_carrito(request, producto_id):
    """
    Añade un producto al carrito POS garantizando:
    - lectura real desde la API stock/
    - validación de stock antes de agregar
    - cantidad POST segura
    """
    token = request.session.get("api_token")
    api = POSAPIClient(token)

    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except:
        cantidad = 1

    # Obtener stock exacto via API
    r = api.session.get(f"{api.base_url}/stock/")
    data = r.json()
    items = data.get("results", data)

    producto = None
    for s in items:
        p = s.get("producto")
        if not p:
            continue
        if p["id"] == int(producto_id):
            p["stock_cantidad"] = s.get("cantidad", 0)
            producto = p
            break

    if not producto:
        messages.error(request, "Producto no encontrado en inventario.")
        return redirect("pos:panel_pos")

    if producto["stock_cantidad"] < cantidad:
        messages.error(request, "Stock insuficiente.")
        return redirect("pos:panel_pos")

    carrito = CarritoPOS(request)
    carrito.agregar(producto, cantidad)

    messages.success(
        request,
        f"{producto['nombre']} x{cantidad} añadido al carrito."
    )
    return redirect("pos:panel_pos")


@empleado_required
def eliminar_carrito(request, producto_id):
    carrito = CarritoPOS(request)
    carrito.eliminar(producto_id)
    messages.info(request, "Producto eliminado del carrito.")
    return redirect("pos:panel_pos")


@empleado_required
def limpiar_carrito(request):
    carrito = CarritoPOS(request)
    carrito.limpiar()
    messages.info(request, "Carrito vaciado.")
    return redirect("pos:panel_pos")


@empleado_required
def ver_carrito(request):
    carrito = CarritoPOS(request)
    return render(
        request,
        "pos/carrito.html",
        {
            "carrito": carrito.items(),
            "total": carrito.total(),
        },
    )


@empleado_required
def finalizar_venta(request):
    """
    Envia la venta a la API unificada:
    {
        detalles: [...],
        metodo_pago: str,
        descuento: float
    }
    El total final se calcula dentro de la API (no aquí).
    """
    token = request.session.get("api_token")
    if not token:
        messages.error(request, "Token inválido. Inicia sesión nuevamente.")
        return redirect("pos:login_pos")

    api = POSAPIClient(token)
    carrito = CarritoPOS(request)

    if not carrito.carrito:
        messages.warning(request, "El carrito está vacío.")
        return redirect("pos:panel_pos")

    detalles = []
    for pid, item in carrito.carrito.items():
        detalles.append({
            "producto": int(pid),
            "cantidad": item["cantidad"],
        })

    metodo = request.POST.get("metodo_pago", "tarjeta")

    try:
        descuento = Decimal(request.POST.get("descuento", "0")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except:
        descuento = Decimal("0.00")

    payload = {
        "detalles": detalles,
        "metodo_pago": metodo,
        "descuento": float(descuento),
    }

    r = api.session.post(f"{api.base_url}/ventas/", json=payload)

    if r.status_code in (200, 201):
        data = r.json()
        venta_id = data.get("id")
        messages.success(
            request,
            f"Venta #{venta_id} registrada correctamente."
        )
        carrito.limpiar()
        return redirect("pos:panel_pos")

    try:
        error = r.json()
    except:
        error = r.text

    messages.error(request, f"Error al registrar venta: {error}")
    return redirect("pos:panel_pos")
