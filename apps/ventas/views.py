from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.contrib import messages  # al inicio del archivo
from django.contrib.auth.decorators import login_required
from django.conf import settings
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

def agregar_carrito(request, vino_id):
    cart = Cart(request)
    cantidad = int(request.POST.get('cantidad', 1))
    cart.add(vino_id, cantidad)
    messages.success(request, f"Se añadieron {cantidad} unidad(es) al carrito.")
    # Redirige a la página anterior en lugar del carrito
    return redirect(request.META.get('HTTP_REFERER', 'inventario:lista_vinos'))

def restar_carrito(request, vino_id):
    cart = Cart(request)
    cantidad = int(request.POST.get('cantidad', 1))
    cart.subtract(vino_id, cantidad)
    return redirect('ventas:ver_carrito')

def eliminar_carrito(request, vino_id):
    cart = Cart(request)
    cart.remove(vino_id)
    return redirect('ventas:ver_carrito')

@login_required
def checkout(request):
    perfil = getattr(request.user, "perfilcliente", None)
    if not perfil or not perfil.es_mayor_edad:
        messages.error(request, "Debes ser mayor de 18 años para comprar alcohol.")
        return redirect("usuarios:perfil")

    campos_requeridos = [perfil.dni, perfil.direccion, perfil.ciudad, perfil.codigo_postal]
    if not all(campos_requeridos):
        messages.error(request, "Debes completar tus datos personales y dirección antes de continuar con la compra.")
        return redirect("usuarios:perfil")
    
    cart = Cart(request)
    if not any(cart):
        return redirect('ventas:ver_carrito')

    almacen_central = Almacen.objects.get(nombre='Central')

    # Verificar stock
    for item in cart:
        stock = item['vino'].stock_set.filter(almacen=almacen_central).first()
        if not stock or stock.cantidad < item['cantidad']:
            messages.error(request, f"Stock insuficiente para {item['vino'].nombre}.")
            return redirect('ventas:tramitar_pedido')

    # Crear venta pendiente
    venta = Venta.objects.create(cliente=request.user, total=cart.total(), pagado=False)
    for item in cart:
        DetalleVenta.objects.create(
            venta=venta,
            vino=item['vino'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio'],
            subtotal=item['subtotal']
        )

    # No limpiar carrito todavía
    request.session["venta_id"] = venta.id
    return redirect('ventas:pago', venta_id=venta.id)

@login_required
def tramitar_pedido(request):
    cart = Cart(request)
    if not any(cart):
        return redirect('ventas:ver_carrito')

    perfil = getattr(request.user, "perfilcliente", None)
    if perfil is None:
        perfil = PerfilCliente.objects.create(user=request.user)

    if request.method == "POST":
        form = PerfilClienteForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect("ventas:checkout")  # crea Venta y redirige al pago
    else:
        form = PerfilClienteForm(instance=perfil)

    return render(request, "ventas/tramitar_pedido.html", {
        "cart": cart,
        "form": form,
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
    # depuracion consola
    payment_intent = request.GET.get("payment_intent")

    # Última venta no pagada del usuario
    ultima = (
        Venta.objects.filter(cliente=request.user)
        .order_by("-fecha")
        .first()
    )

    if ultima and not ultima.pagado:
        ultima.pagado = True
        ultima.save(update_fields=["pagado"])

        almacen_central = Almacen.objects.get(nombre="Central")
        for detalle in ultima.detalles.all():
            stock = detalle.vino.stock_set.filter(almacen=almacen_central).first()
            if stock:
                stock.cantidad = max(0, stock.cantidad - detalle.cantidad)
                stock.save(update_fields=["cantidad"])

        # Aquí sí se limpia el carrito tras confirmar el pago
        from apps.ventas.cart import Cart
        cart = Cart(request)
        cart.clear()

    return render(request, "ventas/confirmacion.html", {"venta": ultima})