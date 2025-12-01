# tests/api/test_ventas.py

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient

from apps.inventario.models import Producto, Stock, Categoria
from apps.core.models import Almacen, Tienda, Empleado
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestVentaPOS:

    def setup_method(self):
        self.client = APIClient()

        # Usuario empleado
        self.user = User.objects.create_user(username="emp", password="1234")
        self.almacen = Almacen.objects.create(nombre="Central")
        self.tienda = Tienda.objects.create(nombre="T1", codigo="T1C", almacen=self.almacen)
        self.empleado = Empleado.objects.create(user=self.user, tienda=self.tienda)

        # Login API
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

    def test_crear_venta_correcta(self):
        url = reverse("ventas-list")
        payload = {
            "detalles": [
                {"producto": self.prod.id, "cantidad": 3}
            ],
            "descuento": 10,
            "metodo_pago": "efectivo",
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 201

        data = r.json()

        # Validaciones núcleo
        assert data["total"] == "40.50"   # 3 × 15 = 45 → -10% = 40.5
        assert data["pagado"] is True

        # Stock descontado
        stock = Stock.objects.get(producto=self.prod, almacen=self.almacen)
        assert stock.cantidad == 47

    def test_stock_insuficiente(self):
        url = reverse("ventas-list")
        payload = {
            "detalles": [
                {"producto": self.prod.id, "cantidad": 999}
            ],
            "descuento": 0,
        }

        r = self.client.post(url, payload, format="json")
        assert r.status_code == 400
        assert "Stock insuficiente" in str(r.content)

    def test_venta_idempotencia(self):
        """
        Dos intentos idénticos deben producir:
        - Solo una venta real
        - Stock descontado una sola vez
        - Segundo intento debe fallar (select_for_update protege)
        """
        url = reverse("ventas-list")
        payload = {
            "detalles": [
                {"producto": self.prod.id, "cantidad": 5}
            ],
        }

        r1 = self.client.post(url, payload, format="json")
        assert r1.status_code == 201

        stock = Stock.objects.get(producto=self.prod, almacen=self.almacen)
        assert stock.cantidad == 45

        # Segundo intento
        r2 = self.client.post(url, payload, format="json")
        assert r2.status_code == 400

        # Stock no ha vuelto a descontar
        stock2 = Stock.objects.get(producto=self.prod, almacen=self.almacen)
        assert stock2.cantidad == 45
