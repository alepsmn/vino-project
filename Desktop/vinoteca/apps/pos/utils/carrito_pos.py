# apps/pos/utils/carrito_pos.py

from decimal import Decimal


class CarritoPOS:
    """
    Carrito exclusivo del POS.
    Reglas:
    - No usa Producto modelo → usa diccionarios API.
    - No almacena Decimals sin convertir → siempre str.
    - No admite estados inválidos.
    - Idempotente: agregar / eliminar / limpiar no rompe sesión.
    """

    SESSION_KEY = "pos_carrito"

    def __init__(self, request):
        self.session = request.session
        raw = self.session.get(self.SESSION_KEY)

        if raw is None:
            raw = {}

        # Garantizar formato estricto
        self.carrito = self._sanear(raw)

    # -------------------------
    # PROTECCIÓN DE ESTADO
    # -------------------------
    def _sanear(self, raw):
        """
        Convierte cualquier formato ambiguo a formato estricto:
        {
            producto_id: {
                nombre: str,
                precio: str (representa decimal),
                cantidad: int,
            }
        }
        """
        fijo = {}

        for pid, item in raw.items():
            try:
                pid_str = str(int(pid))
            except:
                continue

            try:
                cantidad = int(item.get("cantidad", 0))
                if cantidad <= 0:
                    continue
            except:
                continue

            nombre = str(item.get("nombre", "")).strip()
            precio = item.get("precio")

            try:
                Decimal(str(precio))
            except:
                continue

            fijo[pid_str] = {
                "nombre": nombre,
                "precio": str(precio),
                "cantidad": cantidad,
            }

        return fijo

    def _guardar(self):
        self.session[self.SESSION_KEY] = self.carrito
        self.session.modified = True

    # -------------------------
    # OPERACIONES
    # -------------------------
    def agregar(self, producto_api, cantidad=1):
        """
        producto_api es un dict obtenido desde la API:
        {
            id, nombre, precio_venta, stock_cantidad, ...
        }
        """
        pid = str(producto_api["id"])
        cantidad = int(cantidad)

        if cantidad <= 0:
            return

        nombre = str(producto_api.get("nombre", ""))
        precio = producto_api.get("precio_venta")

        try:
            Decimal(str(precio))
        except:
            return

        if pid not in self.carrito:
            self.carrito[pid] = {
                "nombre": nombre,
                "precio": str(precio),
                "cantidad": 0,
            }

        self.carrito[pid]["cantidad"] += cantidad
        if self.carrito[pid]["cantidad"] <= 0:
            del self.carrito[pid]

        self._guardar()

    def eliminar(self, producto_id):
        pid = str(producto_id)
        if pid in self.carrito:
            del self.carrito[pid]
            self._guardar()

    def limpiar(self):
        self.carrito = {}
        self._guardar()

    # -------------------------
    # ITERACIÓN / CONSULTA
    # -------------------------
    def items(self):
        """
        Devuelve los ítems listos para la vista POS:
        [
            {
                "id": pid,
                "nombre": str,
                "precio": Decimal,
                "cantidad": int,
                "subtotal": Decimal,
            }
        ]
        """
        salida = []
        for pid, item in self.carrito.items():
            precio = Decimal(item["precio"])
            cantidad = item["cantidad"]
            salida.append(
                {
                    "id": int(pid),
                    "nombre": item["nombre"],
                    "precio": precio,
                    "cantidad": cantidad,
                    "subtotal": precio * cantidad,
                }
            )
        return salida

    def total(self):
        return sum(
            Decimal(item["precio"]) * item["cantidad"]
            for item in self.carrito.values()
        )
