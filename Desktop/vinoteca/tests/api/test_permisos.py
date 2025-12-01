import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from apps.inventario.models import Stock
from apps.core.models import Empleado, Tienda, Almacen

pytestmark = pytest.mark.django_db


class TestPermisosAPI:

    def setup_method(self):
        self.client = APIClient()

        # Tienda A
        self.almacen_a = Almacen.objects.create(nombre="A1")
        self.tienda_a = Tienda.objects.create(nombre="T1", almacen=self.almacen_a)

        # Tienda B
        self.almacen_b = Almacen.objects.create(nombre="B1")
        self.tienda_b = Tienda.objects.create(nombre="T2", almacen=self.almacen_b)

        # Usuario A
        self.user_a = User.objects.create_user(username="empleadoA", password="123")
        Empleado.objects.create(user=self.user_a, tienda=self.tienda_a)

        # Usuario B
        self.user_b = User.objects.create_user(username="empleadoB", password="123")
        Empleado.objects.create(user=self.user_b, tienda=self.tienda_b)

    def test_empleado_no_ve_stock_de_otra_tienda(self):
        """Empleado A no puede ver stock de tienda B."""
        self.client.force_authenticate(self.user_a)

        url = reverse("stock-list")

        from apps.inventario.models import Productor, Categoria, Producto

        productor = Productor.objects.create(nombre="P", pais="ES", region="R")
        categoria = Categoria.objects.create(nombre="C", slug="c")

        producto = Producto.objects.create(
            nombre="Prod",
            slug="prod",
            categoria=categoria,
            productor=productor,
            precio_compra=Decimal("5.00"),
            margen=Decimal("2.00"),
            precio_venta=Decimal("10.00"),
        )

        Stock.objects.create(
            producto=producto,
            almacen=self.almacen_b,
            cantidad=50
        )

        r = self.client.get(url)
        data = r.json()

        assert r.status_code == 200
        assert len(data["results"]) == 0  # No ve stock ajeno
