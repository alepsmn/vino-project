import os
import django
import csv
from decimal import Decimal

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vino_project.settings')
django.setup()

from apps.core.models import Almacen
from apps.inventario.models import Productor, Vino, Stock

# Ruta del CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
RUTA_CSV = os.path.join(DATA_DIR, "inventario.csv")

def limpiar_numero(valor):
    if not valor:
        return Decimal('0.00')
    v = valor.replace("€", "").replace(",", ".").replace("%", "").strip()
    try:
        return Decimal(v)
    except Exception:
        return Decimal('0.00')

def importar():
    print("=== Importando inventario desde CSV ===")

    # Comprobar existencia del archivo
    if not os.path.exists(RUTA_CSV):
        print(f"ERROR: No se encontró el archivo CSV en {RUTA_CSV}")
        print("Coloca el archivo 'inventario.csv' en la carpeta 'data' del proyecto.")
        return

    # Crear o recuperar almacén central
    almacen, _ = Almacen.objects.get_or_create(nombre="Central", defaults={"ubicacion": "Madrid"})

    with open(RUTA_CSV, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for i, row in enumerate(lector, 1):
            nombre = row.get("Nombre") or row.get("NOMBRE") or row.get("Vino") or ""
            tipo = row.get("Tipo") or row.get("TIPO") or "tinto"
            productor_nombre = row.get("Productor") or "Desconocido"
            pais = row.get("Pais") or "España"
            region = row.get("DO") or ""
            uvas = row.get("Uvas") or ""
            precio_compra = limpiar_numero(row.get("PRECIO COMPRA"))
            margen = limpiar_numero(row.get("PORCENTAJE"))
            precio_venta = limpiar_numero(row.get("PREU"))

            if not nombre:
                continue

            productor, _ = Productor.objects.get_or_create(
                nombre=productor_nombre.strip() or "Desconocido",
                defaults={"pais": pais.strip(), "region": region.strip()}
            )

            vino, _ = Vino.objects.get_or_create(
                nombre=nombre.strip(),
                defaults={
                    "tipo": tipo.strip().lower(),
                    "productor": productor,
                    "denominacion_origen": region.strip(),
                    "uvas": uvas.strip(),
                    "precio_compra": precio_compra,
                    "margen": margen,
                    "precio_venta": precio_venta,
                    "activo": True
                }
            )

            Stock.objects.get_or_create(
                vino=vino,
                almacen=almacen,
                defaults={"cantidad": 20}
            )

            if i % 10 == 0:
                print(f"→ {i} registros procesados...")

    print("=== Importación completada correctamente ===")

if __name__ == "__main__":
    importar()
