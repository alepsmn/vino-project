from django.contrib import admin
from .models import Productor, Vino, Stock, MenuLateral, EntradaMenu

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
    list_display = ('vino', 'almacen', 'cantidad', 'actualizado')
    list_filter = ('almacen',)
    search_fields = ('vino__nombre',)
    readonly_fields = ('actualizado',)

class EntradaMenuInline(admin.TabularInline):
    model = EntradaMenu
    fk_name = "padre"
    extra = 0
    verbose_name = "Subentrada"
    verbose_name_plural = "Subentradas"

@admin.register(EntradaMenu)
class EntradaMenuAdmin(admin.ModelAdmin):
    list_display = ("nombre", "menu", "padre", "orden", "activo")
    list_filter = ("menu", "activo")
    search_fields = ("nombre",)
    inlines = [EntradaMenuInline]

@admin.register(MenuLateral)
class MenuLateralAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")