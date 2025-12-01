from decimal import Decimal
from apps.inventario.models import Producto


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.user = getattr(request, "user", None)

        # Clave de sesión por usuario
        if self.user and self.user.is_authenticated:
            self.user_key = f"cart_user_{self.user.id}"
        else:
            self.user_key = "cart"

        # Cargar o crear carrito vacío
        cart = self.session.get(self.user_key)
        if not cart:
            cart = {}
            self.session[self.user_key] = cart
        self.cart = cart

    def add(self, producto_id, cantidad=1):
        producto_id = str(producto_id)
        producto = Producto.objects.get(id=producto_id)
        if producto_id not in self.cart:
            # Todos los valores convertidos a tipos JSON serializables
            self.cart[producto_id] = {
                "nombre": str(producto.nombre),
                "precio": str(producto.precio_venta),  # string, no Decimal
                "cantidad": 0
            }
        self.cart[producto_id]["cantidad"] += int(cantidad)
        self.save()

    def subtract(self, vino_id, cantidad=1):
        vino_id = str(vino_id)
        if vino_id in self.cart:
            self.cart[vino_id]["cantidad"] -= int(cantidad)
            if self.cart[vino_id]["cantidad"] <= 0:
                del self.cart[vino_id]
            self.save()

    def remove(self, vino_id):
        vino_id = str(vino_id)
        if vino_id in self.cart:
            del self.cart[vino_id]
            self.save()

    def clear(self):
        self.session[self.user_key] = {}
        self.session.modified = True

    def save(self):
        safe_cart = {}
        # Convertir todo a tipos seguros para JSON
        for k, item in self.cart.items():
            safe_cart[str(k)] = {
                "nombre": str(item.get("nombre", "")),
                "precio": str(item.get("precio")),  # forzamos str
                "cantidad": int(item.get("cantidad", 0))
            }
        self.session[self.user_key] = safe_cart
        self.session.modified = True
        self.cart = safe_cart  # mantener sincronizado

    def __iter__(self):
        for producto_id, item in self.cart.items():
            try:
                precio_decimal = Decimal(item["precio"])
            except Exception:
                precio_decimal = Decimal(str(item["precio"]))
            producto = Producto.objects.filter(id=producto_id).first()
            if producto:
                yield {
                    "producto": producto,
                    "nombre": item["nombre"],
                    "precio": precio_decimal,
                    "cantidad": item["cantidad"],
                    "subtotal": precio_decimal * item["cantidad"],
                }

    def total(self):
        return sum(Decimal(i["precio"]) * i["cantidad"] for i in self.cart.values())

def merge_carts(session, user_id):
    anon_key = "cart"
    user_key = f"cart_user_{user_id}"

    anon = session.get(anon_key, {})
    user_cart = session.get(user_key, {})

    # fusionar cantidades
    for pid, item in anon.items():
        if pid in user_cart:
            user_cart[pid]["cantidad"] += item["cantidad"]
        else:
            user_cart[pid] = item

    session[user_key] = user_cart
    if anon_key in session:
        del session[anon_key]
    session.modified = True