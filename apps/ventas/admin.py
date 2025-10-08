from django.contrib import admin
from .models import Venta, DetalleVenta

# Register your models here.

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]
    list_display = ('id', 'fecha', 'total', 'pagado')
    list_filter = ('pagado', 'fecha')
    date_hierarchy = 'fecha'

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'vino', 'cantidad', 'precio_unitario', 'subtotal')