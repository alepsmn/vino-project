from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import redirect, render
from django.contrib import messages
from apps.pos.api_client import POSAPIClient
from .utils.carrito_pos import CarritoPOS
from .views import empleado_required

@empleado_required
def agregar_carrito(request, producto_id):
    token = request.session.get("api_token")
    api = POSAPIClient(token)
    cantidad = int(request.POST.get("cantidad", 1))

    response = api.session.get(f"{api.base_url}/stock/")
    data = response.json()
    stock_items = data.get("results", data)

    producto = None
    for s in stock_items:
        if s["producto"]["id"] == int(producto_id):
            producto = s["producto"]
            producto["stock_cantidad"] = s.get("cantidad", 0)
            break

    if not producto:
        messages.error(request, "Producto no encontrado en el inventario.")
        return redirect("pos:panel_pos")

    if producto["stock_cantidad"] < cantidad:
        messages.error(request, "Cantidad superior al stock disponible.")
        return redirect("pos:panel_pos")

    carrito = CarritoPOS(request)
    carrito.agregar(producto, cantidad)
    messages.success(request, f"{producto['nombre']} x{cantidad} añadido al carrito.")
    return redirect("pos:panel_pos")

@empleado_required
def eliminar_carrito(request, vino_id):
    carrito = CarritoPOS(request)
    carrito.eliminar(vino_id)
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
    contexto = {
        "carrito": carrito.items(),
        "total": carrito.total(),
    }
    return render(request, "pos/carrito.html", contexto)

@empleado_required
def finalizar_venta(request):
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
    for producto_id, item in carrito.carrito.items():
        detalles.append({
            "producto": int(producto_id),
            "cantidad": item["cantidad"],
        })

    total = carrito.total()
    metodo = request.POST.get("metodo_pago", "tarjeta")

    # descuento leído del formulario (porcentaje)
    try:
        descuento = Decimal(request.POST.get("descuento", "0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except:
        descuento = Decimal("0.00")

    # aplicar descuento al total
    total_final = (total * (Decimal("100") - descuento) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    response = api.session.post(
        f"{api.base_url}/ventas/",
        json={
            "detalles": detalles,
            "total": float(total_final),
            "pagado": True,
            "metodo_pago": metodo,
            "descuento": float(descuento)
        }
    )

    if response.status_code in (200, 201):
        data = response.json()
        venta_id = data.get("id")
        messages.success(request, f"Venta #{venta_id} registrada correctamente. Total: {total_final} € (Descuento {descuento}%).")
        carrito.limpiar()
    else:
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text
        messages.error(request, f"Error al registrar la venta ({response.status_code}): {error_msg}")

    return redirect("pos:panel_pos")
