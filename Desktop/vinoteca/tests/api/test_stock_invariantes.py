import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from apps.inventario.models import Stock, MovimientoStock
from apps.ventas.models import Venta
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


class TestStockInvariantes:

    def setup_method(self):
        self.client = APIClient()

        # Crear usuario empleado con tienda y almacén
        self.user = User.objects.create_user(username="empleado", password="123")
        self.client.force_authenticate(self.user)

        from apps.core.models import Empleado, Tienda, Almacen
        self.almacen = Almacen.objects.create(nombre="A1")
        self.tienda = Tienda.objects.create(nombre="T1", almacen=self.almacen)
        Empleado.objects.create(user=self.user, tienda=self.tienda)

        # Crear producto + stock inicial
        from apps.inventario.models import Productor, Categoria, Producto
        self.productor = Productor.objects.create(nombre="P", pais="ES", region="R")
        self.categoria = Categoria.objects.create(nombre="C", slug="c")
        self.producto = Producto.objects.create(
            nombre="Prod",
            slug="prod",
            categoria=self.categoria,
            productor=self.productor,
            precio_compra=Decimal("5.00"),
            margen=Decimal("2.00"),
            precio_venta=Decimal("10.00"),  # 5 * 2 = 10
        )

        self.stock = Stock.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=50,
        )

    # ============================
    # 1) EL STOCK NUNCA NEGATIVO
    # ============================

    def test_invariante_stock_no_negativo(self):
        """
        Intento de salida mayor que el stock debe:
        - Devolver 400
        - No modificar el stock
        - No crear MovimientoStock inválido
        """

        url = reverse("movimientostock-list")

        payload = {
            "producto": self.producto.id,
            "cantidad": 999,
            "tipo": "salida",
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 400

        # Stock intacto
        self.stock.refresh_from_db()
        assert self.stock.cantidad == 50

        # No hay movimientos creados
        assert MovimientoStock.objects.count() == 0

    # ======================================================
    # 2) SECUENCIA DE OPERACIONES NO PUEDE ROMPER EL ESTADO
    # ======================================================

    def test_invariante_stock_secuencias(self):
        """
        Secuencia general:
        - entrada válida
        - salida válida
        - intento inválido
        Estado final debe seguir siendo consistente.
        """

        url = reverse("movimientostock-list")

        # Entrada
        r1 = self.client.post(url, {
            "producto": self.producto.id,
            "cantidad": 30,
            "tipo": "entrada",
        }, format="json")
        assert r1.status_code == 201

        # Salida válida
        r2 = self.client.post(url, {
            "producto": self.producto.id,
            "cantidad": 20,
            "tipo": "salida",
        }, format="json")
        assert r2.status_code == 201

        # Intento inválido
        r3 = self.client.post(url, {
            "producto": self.producto.id,
            "cantidad": 999,
            "tipo": "salida",
        }, format="json")
        assert r3.status_code == 400

        # Estado final válido
        self.stock.refresh_from_db()
        assert self.stock.cantidad == 60  # 50 + 30 - 20

        # Movimientos válidos cuadran el delta
        movimientos = MovimientoStock.objects.order_by("id")
        cantidades = [m.cantidad for m in movimientos]
        assert sum(cantidades) == 10  # 30 - 20
        assert movimientos.count() == 2   # solo los válidos
