from django.shortcuts import render, redirect
from django.contrib import messages  # al inicio del archivo
from django.contrib.auth.decorators import login_required
from apps.core.models import Tienda
from .models import Venta, DetalleVenta
from .cart import Cart

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
    cart = Cart(request)

    if not any(cart):
        return render(request, 'ventas/checkout.html', {
            'cart': cart,
            'error': 'El carrito está vacío. Añade productos antes de comprar.'
        })

    if request.method == 'POST':
        tienda_online = Tienda.objects.get_or_create(nombre='Online', codigo='ONLINE')[0]

        # Validar stock antes de confirmar venta
        for item in cart:
            stock = item['vino'].stock_set.filter(tienda=tienda_online).first()
            if not stock or stock.cantidad < item['cantidad']:
                return render(request, 'ventas/checkout.html', {
                    'cart': cart,
                    'error': f"Stock insuficiente para {item['vino'].nombre}."
                })

        venta = Venta.objects.create(
            cliente=request.user,
            total=cart.total(),
            pagado=True,
            tienda=tienda_online
        )

        for item in cart:
            DetalleVenta.objects.create(
                venta=venta,
                vino=item['vino'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
                subtotal=item['subtotal']
            )
            stock = item['vino'].stock_set.filter(tienda=tienda_online).first()
            if stock:
                stock.cantidad = max(0, stock.cantidad - item['cantidad'])
                stock.save()

        cart.clear()
        return render(request, 'ventas/confirmacion.html', {'venta': venta})

    return render(request, 'ventas/checkout.html', {'cart': cart})
