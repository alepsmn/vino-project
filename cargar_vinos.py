import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vino_project.settings')
django.setup()

from apps.core.models import Tienda
from django.db import transaction
from apps.inventario.models import Vino, Productor, Stock

# Helpers
def dec(val):
    """
    Convierte strings tipo '5,90 €' o '1,20%' a Decimal('5.90') o Decimal('1.20').
    Acepta float/Decimal/str.
    """
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip()
    s = s.replace('€', '').replace('%', '').replace(' ', '')
    s = s.replace(',', '.')  # coma decimal -> punto
    if s == '' or s == '-':
        return Decimal('0')
    return Decimal(s)

def norm_tipo(t):
    t = str(t or '').strip().lower()
    if 'tinto' in t: return 'tinto'
    if 'blanco' in t: return 'blanco'
    if 'rosado' in t: return 'rosado'
    if 'espumoso' in t: return 'espumoso'  # incluye “espumoso rosado”
    return 'tinto'  # default conservador

def safe(u):
    return (u or '').strip().strip(',').replace('  ', ' ')

# Datos (adaptados a tus filas)
rows = [
    {"nombre":"L'Ocell","tipo":"Tinto","productor":"Hidalgo Albert","pais":"España","do":"Montsant","uvas":"Garnacha, Carinyena, Cabernet Sauvignon","precio_compra":"5,90 €","margen":"1,20%","precio_venta":"7,08 €"},
    {"nombre":"Valtravieso Santa María","tipo":"Tinto","productor":"Valtravieso","pais":"España","do":"Ribera del Duero","uvas":"Tempranillo, Merlot,  Cabernet Sauvignon","precio_compra":"6,25 €","margen":"1,20%","precio_venta":"7,52 €"},
    {"nombre":"Zismero Garnacha","tipo":"Tinto","productor":"Alto Moncayo","pais":"España","do":"Campo de Borja","uvas":"Garnacha","precio_compra":"6,65 €","margen":"1,20%","precio_venta":"7,97 €"},
    {"nombre":"Manuel Hidalgo Fina","tipo":"Tinto","productor":"Hidalgo Albert","pais":"España","do":"Priorat","uvas":"Garnacha, Cabernet","precio_compra":"7,90 €","margen":"1,21%","precio_venta":"9,57 €"},
    {"nombre":"B.R.O.T.","tipo":"Tinto","productor":"Col·lectiu Biodinamich","pais":"España","do":"Penedès","uvas":"Tempranillo, Pinot Noir","precio_compra":"9,42 €","margen":"1,16%","precio_venta":"10,97 €"},
    {"nombre":"Almanova","tipo":"Tinto","productor":"Alma Mas Donas","pais":"España","do":"Ribiera Sacra","uvas":"Mencía","precio_compra":"8,59 €","margen":"1,19%","precio_venta":"10,25 €"},
    {"nombre":"Gruñón","tipo":"Tinto","productor":"Alto Moncayo","pais":"España","do":"Campo de Borja","uvas":"Garnacha & Syrah","precio_compra":"11,25 €","margen":"1,42%","precio_venta":"15,97 €"},
    {"nombre":"Metrius","tipo":"Tinto","productor":"-","pais":"España","do":"Galicia","uvas":"Syrah, Merlot","precio_compra":"13,45 €","margen":"1,19%","precio_venta":"15,98 €"},
    {"nombre":"Proventus","tipo":"Tinto","productor":"Tr3smano","pais":"España","do":"Ribera del Duero","uvas":"Tempranillo","precio_compra":"11,32 €","margen":"1,37%","precio_venta":"15,48 €"},
    {"nombre":"Edouard Delaunay Bourgogne","tipo":"Tinto","productor":"Edourad Delaunay","pais":"Francia","do":"Bourgone","uvas":"Pinot Noir","precio_compra":"12,70 €","margen":"1,21%","precio_venta":"15,37 €"},
    {"nombre":"Remírez de Ganuza Reserva","tipo":"Tinto","productor":"Remirez de Ganuza","pais":"España","do":"Rioja","uvas":"Tempranillo","precio_compra":"42,00 €","margen":"1,24%","precio_venta":"52,22 €"},
    {"nombre":"Viñas del Vero Pinot Noir 2024","tipo":"Rosado","productor":"Viñas del Vero","pais":"España","do":"Somontano","uvas":"Pinot Noir","precio_compra":"5,56 €","margen":"1,20%","precio_venta":"6,68 €"},
    {"nombre":"Herència Altés L'Esponetania","tipo":"Rosado","productor":"Herència Altés","pais":"España","do":"Terra Alta","uvas":"Garnacha, Carinyena, Garnacha Peluda","precio_compra":"6,15 €","margen":"1,22%","precio_venta":"7,49 €"},
    {"nombre":"Gran Caus Rosat","tipo":"Rosado","productor":"Can Rafols dels Caus","pais":"España","do":"Penedès","uvas":"Merlot","precio_compra":"11,75 €","margen":"1,20%","precio_venta":"14,10 €"},
    {"nombre":"Senda de los Olivos Verdejo","tipo":"Blanco","productor":"Senda de los Olivos","pais":"España","do":"Rueda","uvas":"Verdejo","precio_compra":"4,16 €","margen":"1,38%","precio_venta":"5,74 €"},
    {"nombre":"Vilarnau Capricis","tipo":"Blanco","productor":"Vilarnau","pais":"España","do":"Penedès","uvas":"Xarel·lo","precio_compra":"5,62 €","margen":"1,18%","precio_venta":"6,64 €"},
    {"nombre":"Ònix Clàssic","tipo":"Blanco","productor":"Vitinicola del Priorat","pais":"España","do":"Priorat","uvas":"Garnacha Blanca, Macabeu, PX","precio_compra":"6,97 €","margen":"1,18%","precio_venta":"8,23 €"},
    {"nombre":"B.R.O.T. Blanc","tipo":"Blanco","productor":"Col·lectiu Biodinamich","pais":"España","do":"PEnedès","uvas":"Macabeu, Riesling, Xarel·lo","precio_compra":"9,42 €","margen":"1,16%","precio_venta":"10,97 €"},
    {"nombre":"Benufet Herència Altés","tipo":"Blanco","productor":"Herència Altés","pais":"España","do":"Terra Alta","uvas":"Garnacha Blanca","precio_compra":"9,45 €","margen":"1,18%","precio_venta":"11,18 €"},
    {"nombre":"Almalarga","tipo":"Blanco","productor":"Alma Mas Donas","pais":"España","do":"Ribiera Sacra","uvas":"Godello","precio_compra":"10,70 €","margen":"1,18%","precio_venta":"12,64 €"},
    {"nombre":"Lagar de Proventus Albariño","tipo":"Blanco","productor":"Tr3smano","pais":"Portugal","do":"Douro","uvas":"Albariño","precio_compra":"11,90 €","margen":"1,17%","precio_venta":"13,96 €"},
    {"nombre":"Taleia Castell d'Encus","tipo":"Blanco","productor":"Castell d'encus","pais":"España","do":"Costers del Segre","uvas":"Sauvignon Blanc","precio_compra":"18,52 €","margen":"1,18%","precio_venta":"21,86 €"},
    {"nombre":"Pere Mata Reserva Família","tipo":"Espumoso","productor":"Mata i Coloma","pais":"España","do":"Cava","uvas":"Macabeo, Xarel·lo, Parellada","precio_compra":"9,95 €","margen":"1,16%","precio_venta":"11,54 €"},
    {"nombre":"AT Roca Rosat Reserva 2021","tipo":"Espumoso","productor":"AT Roca","pais":"España","do":"Classic Penedès","uvas":"Macabeo, Xarel·lo, Parellada","precio_compra":"10,08 €","margen":"1,20%","precio_venta":"12,14 €"},
    {"nombre":"Alta Alella Laietà Gran Reserva Brut Nature 2019","tipo":"Espumoso rosado","productor":"Alta Alella","pais":"España","do":"Cava","uvas":"Monastrell","precio_compra":"16,25 €","margen":"1,18%","precio_venta":"19,18 €"},
    {"nombre":"El Corral Cremat","tipo":"Espumoso","productor":"Albet i Noya","pais":"España","do":"Classic Penedès","uvas":"Xarel·lo","precio_compra":"42,50 €","margen":"1,20%","precio_venta":"51,12 €"},
    {"nombre":"Brimoncourt Brut Régence","tipo":"Espumoso","productor":"Brimoncourt","pais":"Francia","do":"Champagne","uvas":"Chardonnay, Pinot Noir, Pinot Meunier","precio_compra":"26,23 €","margen":"1,23%","precio_venta":"32,21 €"},
    {"nombre":"Amat Montané Sireni 2021","tipo":"Espumoso","productor":"Amat & Montané","pais":"España","do":"Ancestral","uvas":"Xarel·lo, Muscatt","precio_compra":"7,65 €","margen":"1,36%","precio_venta":"10,39 €"},
]

@transaction.atomic
def cargar():
    for r in rows:
        productor_nombre = safe(r.get('productor') or '-')
        pais = safe(r.get('pais') or '')
        prod, _ = Productor.objects.get_or_create(
            nombre=productor_nombre,
            defaults={'pais': pais, 'region': None}
        )
        # Si ya existía sin país, actualiza país si viene ahora
        if not prod.pais and pais:
            prod.pais = pais
            prod.save(update_fields=['pais'])

        tipo_norm = norm_tipo(r.get('tipo'))
        vino, created = Vino.objects.get_or_create(
            nombre=safe(r.get('nombre')),
            productor=prod,
            defaults={
                'tipo': tipo_norm,
                'denominacion_origen': safe(r.get('do')),
                'uvas': safe(r.get('uvas')),
                'precio_compra': dec(r.get('precio_compra')),
                'margen': dec(r.get('margen')),
                'precio_venta': dec(r.get('precio_venta')),
                'descripcion': '',
                'activo': True,
            }
        )
        if not created:
            # Actualiza datos clave si ya existía
            vino.tipo = tipo_norm
            vino.denominacion_origen = safe(r.get('do'))
            vino.uvas = safe(r.get('uvas'))
            vino.precio_compra = dec(r.get('precio_compra'))
            vino.margen = dec(r.get('margen'))
            vino.precio_venta = dec(r.get('precio_venta'))
            vino.activo = True
            vino.save()

        # Stock inicial por tiendas (ajusta cantidades si quieres)
        for tienda_nombre, qty in [('Online', 20), ('Tienda Fisica', 20)]:
            tienda_obj, _ = Tienda.objects.get_or_create(
                nombre=tienda_nombre,
                defaults={
                    'direccion': 'N/A',
                    'codigo': tienda_nombre.lower().replace(' ', '_')  # genera código único
                }
            )
            Stock.objects.update_or_create(
                vino=vino,
                tienda=tienda_obj,
                defaults={'cantidad': qty}
            )

        print(f"[OK] {vino.nombre} — {prod.nombre} — {vino.precio_venta}€")

if __name__ == '__main__':
    cargar()
