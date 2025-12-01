from django.contrib import admin
from .models import (
    Categoria, Atributo, ValorAtributo,
    Producto, ProductoAtributo,
    Stock, TransferenciaStock, MovimientoStock,
    Productor, MenuLateral, EntradaMenu
)

# Register your models here.

admin.site.register(Categoria)
admin.site.register(Atributo)
admin.site.register(ValorAtributo)
admin.site.register(Productor)
admin.site.register(Producto)
admin.site.register(ProductoAtributo)
admin.site.register(Stock)
admin.site.register(TransferenciaStock)
admin.site.register(MovimientoStock)
admin.site.register(MenuLateral)
admin.site.register(EntradaMenu)