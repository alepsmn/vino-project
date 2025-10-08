from django.contrib import admin
from .models import Productor, Vino, Stock

# Register your models here.

@admin.register(Productor)
class ProductorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'region')
    search_fields = ('nombre', 'pais', 'region')


@admin.register(Vino)
class VinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'productor', 'precio_venta', 'activo', 'codigo_barras')
    list_filter = ('tipo', 'productor__pais', 'activo')
    search_fields = ('nombre', 'productor__nombre', 'denominacion_origen', 'uvas', 'codigo_barras')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('vino', 'tienda', 'cantidad', 'actualizado')
    list_filter = ('tienda',)
    search_fields = ('vino__nombre', 'tienda')