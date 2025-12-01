import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from apps.inventario.models import Stock, MovimientoStock
from apps.ventas.models import Venta

pytestmark = pytest.mark.django_db


class TestStockIntegridadMovimientos:

    def setup_method(self):
        self.client = APIClient()

        # Usuario + tienda + almacén
        self.user = User.objects.create_user(username="empleado", password="123")
        self.client.force_authenticate(self.user)

        from apps.core.models import Empleado, Tienda, Almacen
        self.almacen = Almacen.objects.create(nombre="A1")
        self.tienda = Tienda.objects.create(nombre="T1", almacen=self.almacen)
        Empleado.objects.create(user=self.user, tienda=self.tienda)

        # Producto + stock inicial
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
            precio_venta=Decimal("10.00"),
        )

        self.stock = Stock.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=50,
        )

        self.url = reverse("movimientostock-list")

    def test_cuadre_movimientos_vs_stock(self):
        """
        Invariante global:
        stock_final == stock_inicial + sum(movimientos.cantidad)
        """

        inicial = self.stock.cantidad

        # Entrada +30
        r1 = self.client.post(self.url, {
            "producto": self.producto.id,
            "cantidad": 30,
            "tipo": "entrada",
        }, format="json")
        assert r1.status_code == 201

        # Salida -10
        r2 = self.client.post(self.url, {
            "producto": self.producto.id,
            "cantidad": 10,
            "tipo": "salida",
        }, format="json")
        assert r2.status_code == 201

        # Salida inválida (no debe alterar nada)
        r3 = self.client.post(self.url, {
            "producto": self.producto.id,
            "cantidad": 9999,
            "tipo": "salida",
        }, format="json")
        assert r3.status_code == 400

        # Stock real
        self.stock.refresh_from_db()
        final = self.stock.cantidad

        # Suma movimientos válidos
        movimientos = MovimientoStock.objects.filter(producto=self.producto)
        suma = sum(m.cantidad for m in movimientos)

        # Comprobación del invariante
        assert final == inicial + suma, \
            f"Invariante roto: final={final}, inicial={inicial}, suma={suma}"