from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Venta, DetalleVenta

# Register your models here

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']

@admin.action(description="Exportar ventas seleccionadas a CSV")
def exportar_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response['Content-Disposition'] = 'attachment; filename=ventas.csv'
    writer = csv.writer(response)
    writer.writerow(["ID", "Cliente", "Fecha", "Total (€)", "Pagado", "Método de Pago"])

    for venta in queryset:
        writer.writerow([
            venta.id,
            venta.cliente.username if venta.cliente else (venta.cliente_nombre or "Anónimo"),
            venta.fecha.strftime("%Y-%m-%d %H:%M"),
            f"{venta.total:.2f}",
            "Sí" if venta.pagado else "No",
            venta.get_metodo_pago_display(),
        ])

    return response

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'tienda', 'total', 'fecha', 'pagado', 'metodo_pago')
    list_filter = ('pagado', 'metodo_pago', 'fecha')
    search_fields = ('cliente__username', 'cliente_dni')
    date_hierarchy = 'fecha'
    inlines = [DetalleVentaInline]
    actions = [exportar_csv]

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
