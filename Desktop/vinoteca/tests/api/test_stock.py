# tests/api/test_stock.py

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient

from apps.inventario.models import Producto, Stock, Categoria
from apps.core.models import Almacen, Tienda, Empleado
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestStockAPI:

    def setup_method(self):
        self.client = APIClient()

        # Usuario empleado
        self.user = User.objects.create_user(username="emp", password="1234")
        self.almacen = Almacen.objects.create(nombre="Central")
        self.tienda = Tienda.objects.create(nombre="T1", codigo="T1C", almacen=self.almacen)
        self.empleado = Empleado.objects.create(user=self.user, tienda=self.tienda)

        self.client.force_authenticate(self.user)

        # Producto
        cat = Categoria.objects.create(nombre="Vinos", slug="vinos")
        self.prod = Producto.objects.create(
            nombre="Vino A",
            slug="vino-a",
            categoria=cat,
            precio_compra=Decimal("10.00"),
            margen=Decimal("1.50"),
            precio_venta=Decimal("15.00"),
        )

        # Stock inicial
        Stock.objects.create(producto=self.prod, almacen=self.almacen, cantidad=50)

    # --------------------------------------------------------
    # 1. stock normal paginado
    # --------------------------------------------------------
    def test_stock_list(self):
        url = reverse("stock-list")
        r = self.client.get(url)
        assert r.status_code == 200
        data = r.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["cantidad"] == 50
        assert data["results"][0]["producto"]["id"] == self.prod.id

    # --------------------------------------------------------
    # 2. stock minimal para POS sin paginar
    # --------------------------------------------------------
    def test_stock_min(self):
        url = reverse("stock_min")
        r = self.client.get(url)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["cantidad"] == 50
        assert data[0]["producto"]["id"] == self.prod.id
        assert data[0]["producto"]["precio_venta"] == "15.00"

    # --------------------------------------------------------
    # 3. movimiento de entrada
    # --------------------------------------------------------
    def test_movimiento_entrada(self):
        url = reverse("movimientostock-list")

        payload = {
            "producto": self.prod.id,
            "cantidad": 10,
            "tipo": "entrada",
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 201

        stock = Stock.objects.get(producto=self.prod, almacen=self.almacen)
        assert stock.cantidad == 60

    # --------------------------------------------------------
    # 4. movimiento de salida válido
    # --------------------------------------------------------
    def test_movimiento_salida(self):
        url = reverse("movimientostock-list")

        payload = {
            "producto": self.prod.id,
            "cantidad": 20,
            "tipo": "salida",
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 201

        stock = Stock.objects.get(producto=self.prod, almacen=self.almacen)
        assert stock.cantidad == 30

    # --------------------------------------------------------
    # 5. movimiento salida NO válido (stock insuficiente)
    # --------------------------------------------------------
    def test_movimiento_salida_insuficiente(self):
        url = reverse("movimientostock-list")

        payload = {
            "producto": self.prod.id,
            "cantidad": 999,
            "tipo": "salida",
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 400
        assert "no puede ser negativo" in str(r.content).lower()

    # --------------------------------------------------------
    # 6. movimiento ajuste
    # --------------------------------------------------------
    def test_movimiento_ajuste(self):
        url = reverse("movimientostock-list")

        payload = {
            "producto": self.prod.id,
            "cantidad": 80,  # se ajusta directamente a 80
            "tipo": "ajuste",
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 201

        stock = Stock.objects.get(producto=self.prod, almacen=self.almacen)
        assert stock.cantidad == 80
