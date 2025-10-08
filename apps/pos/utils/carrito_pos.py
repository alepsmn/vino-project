from decimal import Decimal

class CarritoPOS:
    def __init__(self, request):
        self.session = request.session
        self.carrito = self.session.get("carrito_pos", {})

    def agregar(self, vino, cantidad=1):
        id_str = str(vino["id"])
        carrito = self.carrito.copy()

        precio_unitario = Decimal(str(vino["precio_venta"]))
        cantidad = int(cantidad)

        if id_str in carrito:
            carrito[id_str]["cantidad"] += cantidad
        else:
            carrito[id_str] = {
                "nombre": vino["nombre"],
                "precio_unitario": str(precio_unitario),
                "cantidad": cantidad,
            }

        subtotal = precio_unitario * carrito[id_str]["cantidad"]
        carrito[id_str]["subtotal"] = str(subtotal.quantize(Decimal("0.01")))

        self.carrito = carrito
        self.session["carrito_pos"] = carrito
        self.session.modified = True

    def eliminar(self, vino_id):
        id_str = str(vino_id)
        if id_str in self.carrito:
            del self.carrito[id_str]
            self.session["carrito_pos"] = self.carrito
            self.session.modified = True

    def limpiar(self):
        self.session["carrito_pos"] = {}
        self.session.modified = True
        self.carrito = {}

    def total(self):
        total = Decimal("0.00")
        for item in self.carrito.values():
            total += Decimal(item["subtotal"])
        return total.quantize(Decimal("0.01"))

    def items(self):
        return self.carrito.items()
