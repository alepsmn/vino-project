# apps/api/serializers.py

from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from apps.inventario.models import (
    Productor,
    Categoria,
    Atributo,
    ValorAtributo,
    Producto,
    ProductoAtributo,
    Stock,
    MovimientoStock,
)
from apps.ventas.models import Venta, DetalleVenta


# =========================
# PRODUCTOR
# =========================

class ProductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productor
        fields = ["id", "nombre", "pais", "region"]


# =========================
# CATEGORÍA
# =========================

class CategoriaSerializer(serializers.ModelSerializer):
    hijos = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "padre", "hijos"]

    def get_hijos(self, obj):
        # hijos directos, no recursivo infinito
        children = obj.hijos.all().order_by("nombre")
        return CategoriaSerializer(children, many=True).data


# =========================
# ATRIBUTOS
# =========================

class ValorAtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValorAtributo
        fields = ["id", "valor", "orden"]


class AtributoSerializer(serializers.ModelSerializer):
    valores = serializers.SerializerMethodField()

    class Meta:
        model = Atributo
        fields = ["id", "nombre", "slug", "tipo_dato", "categoria", "valores"]

    def get_valores(self, obj):
        # Solo tiene sentido para tipo=opcion, pero no pasa nada si se devuelve vacío
        if obj.tipo_dato != "opcion":
            return []
        return ValorAtributoSerializer(obj.valores.all(), many=True).data


# =========================
# PRODUCTO + ATRIBUTOS
# =========================

class ProductoAtributoSerializer(serializers.ModelSerializer):
    atributo = serializers.SerializerMethodField()
    valor = serializers.SerializerMethodField()

    class Meta:
        model = ProductoAtributo
        fields = ["atributo", "valor"]

    def get_atributo(self, obj):
        a = obj.atributo
        return {
            "id": a.id,
            "slug": a.slug,
            "nombre": a.nombre,
            "tipo_dato": a.tipo_dato,
        }

    def get_valor(self, obj):
        tipo = obj.atributo.tipo_dato

        if tipo == "texto":
            return obj.valor_texto
        if tipo == "entero":
            return obj.valor_entero
        if tipo == "decimal":
            return obj.valor_decimal
        if tipo == "booleano":
            return obj.valor_booleano
        if tipo == "opcion":
            return obj.valor_opcion.valor if obj.valor_opcion else None

        return None


class CategoriaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug"]


class ProductoMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ("id", "nombre", "slug")

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSimpleSerializer(read_only=True)
    productor = ProductorSerializer(read_only=True)
    atributos = ProductoAtributoSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "slug",
            "descripcion",
            "categoria",
            "productor",
            "pais",
            "precio_compra",
            "margen",
            "precio_venta",
            "activo",
            "codigo_barras",
            "imagen",
            "created_at",
            "updated_at",
            "atributos",
        ]

# =========================
# STOCK
# =========================

class StockSerializer(serializers.ModelSerializer):
    producto = ProductoMinSerializer(read_only=True)
    almacen = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Stock
        fields = ["id", "producto", "almacen", "cantidad", "actualizado"]

class StockMinimalSerializer(serializers.ModelSerializer):
    producto = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ["producto", "cantidad"]

    def get_producto(self, obj):
        p = obj.producto
        return {
            "id": p.id,
            "nombre": p.nombre,
            "precio_venta": format(p.precio_venta, ".2f"),
        }
    
class MovimientoStockSerializer(serializers.ModelSerializer):
    producto = ProductoMinSerializer(read_only=True)
    almacen = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MovimientoStock
        fields = [
            "id",
            "producto",
            "almacen",
            "cantidad",
            "tipo",
            "fecha",
            "venta",
            "usuario",
        ]

class MovimientoStockInSerializer(serializers.Serializer):
    producto = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=["ajuste", "entrada", "salida"])

    def to_representation(self, instance):
        # DRF nunca debe usar este serializer para salidas.
        return MovimientoStockSerializer(instance).data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        empleado = user.empleado
        tienda = empleado.tienda
        almacen = tienda.almacen

        producto = Producto.objects.get(pk=validated_data["producto"])
        cantidad = validated_data["cantidad"]
        tipo = validated_data["tipo"]

        if not Stock.objects.filter(producto=producto, almacen=almacen).exists():
            raise serializers.ValidationError(
                "Producto no pertenece al almacén del empleado."
            )

        stock = (
            Stock.objects
            .select_for_update()
            .filter(producto=producto, almacen=almacen)
            .first()
        )

        if not stock:
            raise serializers.ValidationError("No hay stock para este producto.")

        if tipo == "salida":
            if stock.cantidad < cantidad:
                raise serializers.ValidationError("No puede ser negativo: stock insuficiente.")
            stock.cantidad -= cantidad

        elif tipo == "entrada":
            stock.cantidad += cantidad

        elif tipo == "ajuste":
            stock.cantidad = cantidad

        stock.save(update_fields=["cantidad"])

        mov = MovimientoStock.objects.create(
            producto=producto,
            almacen=almacen,
            cantidad=cantidad if tipo != "salida" else -cantidad,
            tipo=tipo,
            usuario=user,
        )

        return mov

# =========================
# VENTAS (API POS)
# =========================

class DetalleVentaInSerializer(serializers.Serializer):
    producto = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)


class DetalleVentaOutSerializer(serializers.ModelSerializer):
    producto = ProductoMinSerializer(read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad", "precio_unitario", "subtotal"]


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaInSerializer(many=True, write_only=True)
    lineas = DetalleVentaOutSerializer(source="detalles", many=True, read_only=True)

    class Meta:
        model = Venta
        fields = (
            "id",
            "cliente",
            "tienda",
            "empleado",
            "fecha",
            "total",
            "pagado",
            "descuento",
            "metodo_pago",
            "detalles",   # entrada
            "lineas",     # salida
        )
        read_only_fields = ("cliente", "tienda", "empleado", "fecha", "total", "pagado")

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        empleado = getattr(user, "empleado", None)
        if not empleado or not empleado.tienda:
            raise serializers.ValidationError("Empleado sin tienda asignada.")

        tienda = empleado.tienda
        almacen = tienda.almacen

        detalles_in = validated_data.pop("detalles", [])
        if not detalles_in:
            raise serializers.ValidationError("Una venta requiere al menos un detalle.")

        # =============================
        # Firma POS → anti-duplicados
        # =============================
        firma_nueva = tuple(sorted((d["producto"], d["cantidad"]) for d in detalles_in))

        ultima = (
            Venta.objects
            .filter(empleado=empleado, tienda=tienda)
            .order_by("-fecha")
            .first()
        )

        if ultima:
            firma_ultima = tuple(
                sorted((d.producto_id, d.cantidad) for d in ultima.detalles.all())
            )
            if firma_ultima == firma_nueva:
                raise serializers.ValidationError("Venta duplicada (idempotencia POS).")

        # =============================
        # Validar productos y calcular total previo
        # =============================
        total_bruto = Decimal("0.00")
        productos_cache = {}

        for item in detalles_in:
            pid = item["producto"]
            cantidad = item["cantidad"]

            try:
                p = Producto.objects.get(pk=pid)
            except Producto.DoesNotExist:
                raise serializers.ValidationError(f"Producto {pid} no existe.")

            if cantidad <= 0:
                raise serializers.ValidationError("Cantidad inválida.")

            productos_cache[pid] = p
            total_bruto += (p.precio_venta * cantidad)

        # =============================
        # Validar stock ANTES de crear nada
        # =============================
        from apps.inventario.models import Stock

        for pid, p in productos_cache.items():
            item = next(d for d in detalles_in if d["producto"] == pid)
            cantidad = item["cantidad"]

            s = (
                Stock.objects
                .select_for_update()
                .filter(producto=p, almacen=almacen)
                .first()
            )

            if not s:
                raise serializers.ValidationError(f"No hay stock para {p.nombre}.")

            if s.cantidad < cantidad:
                raise serializers.ValidationError(f"Stock insuficiente para {p.nombre}.")

        # =============================
        # Crear venta
        # =============================
        descuento = Decimal(str(validated_data.get("descuento", 0)))
        metodo_pago = validated_data.get("metodo_pago") or "tarjeta"

        venta = Venta.objects.create(
            cliente=None,
            tienda=tienda,
            empleado=empleado,
            descuento=descuento,
            metodo_pago=metodo_pago,
            total=Decimal("0.00"),
            pagado=False,
        )

        # =============================
        # Crear líneas
        # =============================
        from apps.ventas.models import DetalleVenta

        for item in detalles_in:
            p = productos_cache[item["producto"]]
            cantidad = item["cantidad"]

            DetalleVenta.objects.create(
                venta=venta,
                producto=p,
                cantidad=cantidad,
                precio_unitario=p.precio_venta,
                subtotal=(p.precio_venta * cantidad).quantize(Decimal("0.01")),
            )

        # =============================
        # Aplicar stock
        # =============================
        venta.descontar_stock(
            almacen=almacen,
            usuario=user
        )

        # =============================
        # Finalizar total
        # =============================

        total = (
            total_bruto * (Decimal("1") - descuento / Decimal("100"))
        ).quantize(Decimal("0.01"))

        venta.total = total
        venta.pagado = True
        venta.save(update_fields=["total", "pagado"])

        return venta
