from rest_framework import serializers
from apps.inventario.models import Vino, Productor, Stock

class ProductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productor
        fields = '__all__'

class VinoSerializer(serializers.ModelSerializer):
    productor = ProductorSerializer(read_only=True)

    class Meta:
        model = Vino
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    vino = VinoSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'