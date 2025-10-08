from django.contrib import admin
from .models import PerfilCliente

# Register your models here.

@admin.register(PerfilCliente)
class PerfilClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'ciudad')