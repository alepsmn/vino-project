from .cart import Cart

def cart_count(request):
    try:
        cart = Cart(request)
        count = sum(item['cantidad'] for item in cart)
    except Exception:
        count = 0
    return {'cart_count': count}
