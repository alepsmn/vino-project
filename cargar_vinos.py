import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vino_project.settings')
django.setup()

from apps.inventario.models import Productor, Vino, Destilado, Producto, Stock
from apps.core.models import Almacen

# --- LIMPIEZA PREVIA ---
print("Eliminando datos antiguos...")
Stock.objects.all().delete()
Vino.objects.all().delete()
Destilado.objects.all().delete()
Producto.objects.all().delete()
Productor.objects.all().delete()
Almacen.objects.all().delete()
print("Base limpia. Cargando nuevos datos...")

# --- FUNCIONES AUXILIARES ---
def limpiar_valor(valor):
    if isinstance(valor, str):
        valor = valor.replace('€', '').replace('%', '').replace(',', '.').strip()
    try:
        return float(valor)
    except (ValueError, TypeError):
        return None


def cargar_catalogo_csv(ruta, tipo):
    df = pd.read_csv(ruta)
    print(f"\n>>> Procesando {ruta}")

    # --- Limpieza de filas vacías ---
    df = df.dropna(how='all')
    df['Nombre'] = df['Nombre'].astype(str).str.strip()
    df['PRECIO COMPRA'] = df['PRECIO COMPRA'].astype(str).str.strip()
    df = df[(df['Nombre'] != '') & (df['PRECIO COMPRA'] != '')]

    print(f"Filas válidas detectadas: {len(df)}")

    for _, fila in df.iterrows():
        nombre = fila['Nombre']
        raw_precio = str(fila['PRECIO COMPRA']).replace('€', '').replace(',', '.').strip()

        try:
            precio_compra_valido = float(raw_precio)
        except ValueError:
            print(f"Fila '{nombre}' ignorada: precio no numérico ({raw_precio})")
            continue

        if not nombre or precio_compra_valido <= 0:
            print(f"Fila ignorada: nombre vacío o precio inválido → {fila.to_dict()}")
            continue

        margen_valido = limpiar_valor(fila.get('PORCENTAJE')) or 1.20
        productor_nombre = str(fila.get('Productor')).strip() if pd.notna(fila.get('Productor')) else "Desconocido"
        pais = str(fila.get('País')).strip() if 'País' in df.columns and pd.notna(fila.get('País')) else 'España'
        do = str(fila.get('DO')).strip() if 'DO' in df.columns and pd.notna(fila.get('DO')) else None
        uvas = str(fila.get('Uvas')).strip() if 'Uvas' in df.columns and pd.notna(fila.get('Uvas')) else None

        productor, _ = Productor.objects.get_or_create(nombre=productor_nombre, defaults={'pais': pais})

        if tipo == 'vino':
            subtipo = str(fila.get('Tipo')).lower().strip() if pd.notna(fila.get('Tipo')) else 'tinto'
            Vino.objects.create(
                nombre=nombre,
                tipo='vino',
                subtipo=subtipo,
                productor=productor,
                denominacion_origen=do,
                uvas=uvas,
                precio_compra=precio_compra_valido,
                margen=margen_valido,
            )

        elif tipo == 'destilado':
            subtipo = str(fila.get('Tipo')).lower().strip() if pd.notna(fila.get('Tipo')) else 'whisky'
            volumen = limpiar_valor(fila.get('Volumen')) or 70
            grado = limpiar_valor(fila.get('Grado')) or 40.0
            Destilado.objects.create(
                nombre=nombre,
                tipo='destilado',
                subtipo=subtipo,
                productor=productor,
                volumen_cl=volumen,
                grado_alcohol=grado,
                precio_compra=precio_compra_valido,
                margen=margen_valido,
            )


# --- CARGAS ---
cargar_catalogo_csv("data/Catalogo_Herencia_Altes_Sentits.csv", "vino")
cargar_catalogo_csv("data/Catalogo_The_Macallan_Sentits.csv", "destilado")
cargar_catalogo_csv("data/Listado_Carla_OCULT.xlsx - Sheet1.csv", "vino")

# --- STOCK ---
almacen, _ = Almacen.objects.get_or_create(nombre="Central", defaults={'ubicacion': 'Madrid'})
for producto in Producto.objects.all():
    Stock.objects.get_or_create(producto=producto, almacen=almacen, defaults={'cantidad': 15})

print("Stock generado correctamente.")

# --- CALCULAR PRECIOS ---
for p in Producto.objects.all():
    p.calcular_precio_venta(save=True)
print("Precios de venta recalculados y guardados.")
print(f"Productos totales: {Producto.objects.count()} / Stock: {Stock.objects.count()}")
