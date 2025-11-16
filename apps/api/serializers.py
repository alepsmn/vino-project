from rest_framework import serializers
from apps.inventario.models import (
    Producto, Vino, Destilado, Productor, Stock
)

# Productor
class ProductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productor
        fields = '__all__'


# Producto base
class ProductoSerializer(serializers.ModelSerializer):
    productor = ProductorSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'tipo',
            'productor',
            'pais',
            'precio_compra',
            'margen',
            'precio_venta',
            'activo',
            'codigo_barras',
        ]

    def to_representation(self, instance):
        # recalcula en caso de que el campo esté vacío o desactualizado
        if not instance.precio_venta:
            instance.calcular_precio_venta(save=True)
        return super().to_representation(instance)

# Vino (hereda del producto)
class VinoSerializer(ProductoSerializer):
    class Meta(ProductoSerializer.Meta):
        model = Vino
        fields = ProductoSerializer.Meta.fields + [
            'subtipo',
            'denominacion_origen',
            'uvas',
        ]

# Destilado (hereda del producto)
class DestiladoSerializer(ProductoSerializer):
    class Meta(ProductoSerializer.Meta):
        model = Destilado
        fields = ProductoSerializer.Meta.fields + [
            'subtipo',
            'volumen_cl',
            'grado_alcohol',
        ]

# Stock
class StockSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    almacen = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'
