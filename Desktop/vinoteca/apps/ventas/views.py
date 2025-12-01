from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.contrib import messages  # al inicio del archivo
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from apps.ventas.models import Venta
from apps.core.models import Almacen
from apps.usuarios.forms import PerfilClienteForm
from apps.usuarios.models import PerfilCliente

from .models import Venta, DetalleVenta
from .cart import Cart
import stripe

# Create your views here.

def ver_carrito(request):
    cart = Cart(request)
    return render(request, 'ventas/carrito.html', {'cart': cart})

def agregar_carrito(request, producto_id):
    cart = Cart(request)
    cantidad = int(request.POST.get('cantidad', 1))
    cart.add(producto_id, cantidad)
    messages.success(request, f"Se añadieron {cantidad} unidad(es) al carrito.")
    # Redirige a la página anterior en lugar del carrito
    referer = request.META.get('HTTP_REFERER')
    try:
        return redirect(referer) if referer else redirect('inventario:catalogo')
    except:
        return redirect('inventario:catalogo')

def restar_carrito(request, producto_id):
    cart = Cart(request)
    cantidad = int(request.POST.get('cantidad', 1))
    cart.subtract(producto_id, cantidad)
    return redirect('ventas:ver_carrito')

def eliminar_carrito(request, producto_id):
    cart = Cart(request)
    cart.remove(producto_id)
    return redirect('ventas:ver_carrito')

@login_required
def checkout(request):
    perfil = getattr(request.user, "perfilcliente", None)
    if not perfil or not perfil.es_mayor_edad:
        messages.error(request, "Debes ser mayor de 18 años para comprar alcohol.")
        return redirect("usuarios:perfil_datos")

    campos_requeridos = [perfil.dni, perfil.direccion, perfil.ciudad, perfil.codigo_postal]
    if not all(campos_requeridos):
        messages.error(request, "Debes completar tus datos personales y dirección antes de continuar con la compra.")
        return redirect("usuarios:perfil_datos")
    
    cart = Cart(request)
    if not any(cart):
        return redirect('ventas:ver_carrito')

    almacen_central = Almacen.objects.get(nombre='Central')

    # Verificar stock
    with transaction.atomic():
        for item in cart:
            producto = item["producto"]  # ← TU CART LO ENTREGA ASÍ

            stock = (
                producto.stock_set
                        .select_for_update()
                        .filter(almacen=almacen_central)
                        .first()
            )
            if not stock or stock.cantidad < item["cantidad"]:
                messages.error(request, f"Stock insuficiente para {producto.nombre}.")
                return redirect("ventas:tramitar_pedido")

    # Crear venta pendiente
    venta = Venta.objects.create(cliente=request.user, total=cart.total(), pagado=False)
    for item in cart:
        DetalleVenta.objects.create(
            venta=venta,
            producto=item['producto'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio'],
            subtotal=item['subtotal']
        )

    # No limpiar carrito todavía
    request.session["venta_id"] = venta.id
    return redirect('ventas:pago', venta_id=venta.id)

@login_required
def tramitar_pedido(request):
    perfil = getattr(request.user, "perfilcliente", None)
    if perfil is None:
        perfil = PerfilCliente.objects.create(user=request.user)

    # Verificación de datos críticos antes del checkout
    campos_obligatorios = [
        perfil.dni,
        perfil.fecha_nacimiento,
        perfil.direccion,
        perfil.ciudad,
        perfil.codigo_postal,
    ]

    if not all(campos_obligatorios):
        messages.error(request, "Debes completar tu perfil antes de tramitar el pedido.")
        return redirect("usuarios:perfil_datos")

    # Ahora SÍ solo pedimos dirección de envío (editable)
    if request.method == "POST":
        direccion_envio = request.POST.get("direccion_envio", "").strip()
        if direccion_envio:
            perfil.direccion = direccion_envio
            perfil.save(update_fields=["direccion"])

        return redirect("ventas:checkout")

    cart = Cart(request)

    return render(request, "ventas/tramitar_pedido.html", {
        "perfil": perfil,
        "cart": cart,
    })

def pago_view(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id, cliente=request.user)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    intent = stripe.PaymentIntent.create(
        amount=int(venta.total * 100),
        currency="eur",
        metadata={"venta_id": venta.id}
    )

    return render(request, "ventas/pago.html", {
        "venta": venta,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        "client_secret": intent.client_secret
    })

@require_GET
@login_required
def confirmacion_view(request):
    payment_intent = request.GET.get("payment_intent")

    ultima = (
        Venta.objects.filter(cliente=request.user)
        .order_by("-fecha")
        .first()
    )

    if not ultima:
        messages.error(request, "No se encontró ninguna venta pendiente.")
        return redirect("ventas:ver_carrito")

    if ultima.pagado:
        # Ya se procesó; idempotencia básica
        return render(request, "ventas/confirmacion.html", {"venta": ultima})

    almacen_central = Almacen.objects.get(nombre="Central")

    try:
        # Mismo punto de verdad que la API POS
        ultima.descontar_stock(almacen_central, usuario=request.user)
        ultima.pagado = True
        ultima.save(update_fields=["pagado"])
    except Exception as e:
        messages.error(request, f"Error al actualizar stock: {e}")
        return redirect("ventas:ver_carrito")

    from apps.ventas.cart import Cart
    Cart(request).clear()

    return render(request, "ventas/confirmacion.html", {"venta": ultima})