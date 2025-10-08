from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from django.contrib.auth import login, authenticate, logout
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils.timezone import now
from apps.ventas.models import DetalleVenta
from functools import wraps
from .utils.carrito_pos import CarritoPOS
import requests

from .api_client import POSAPIClient

def empleado_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('/pos/login/')

        # Superusuario: acceso total
        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Empleado: acceso normal
        if hasattr(user, 'empleado'):
            return view_func(request, *args, **kwargs)

        # Sin permisos: cerrar sesión y redirigir
        messages.error(request, "No tienes permisos para acceder al POS.")
        logout(request)
        return redirect('/usuarios/login/')

    return wrapper

def login_pos(request):
    # si el usuario ya está autenticado, lo redirigimos al panel
    if request.user.is_authenticated and request.session.get("api_token"):
        return redirect("pos:panel_pos")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # obtener token de la API
            resp = requests.post(
                "http://127.0.0.1:8000/api/v1/token/",
                data={"username": username, "password": password},
            )
            if resp.status_code == 200:
                token = resp.json().get("token")
                request.session["api_token"] = token
                return redirect("pos:panel_pos")
            else:
                messages.error(request, "No se pudo obtener el token API.")
                return redirect("pos:login_pos")
        else:
            return render(request, "pos/login.html", {"error": "Credenciales incorrectas"})

    return render(request, "pos/login.html")

@empleado_required
def logout_pos(request):
    logout(request)
    return redirect('/pos/login/')

@empleado_required
def panel_pos(request):
    token = request.session.get("api_token")
    api = POSAPIClient(token=token)
    respuesta = api.session.get(f"{api.base_url}/stock/")
    data = respuesta.json()
    stock_items = data.get("results", data)
    vinos = []
    for item in stock_items:
        vino = item.get("vino")
        if vino:
            vino["stock_cantidad"] = item.get("cantidad", 0)
            vinos.append(vino)

    carrito = CarritoPOS(request)
    contexto = {
        "vinos": vinos,
        "carrito": carrito.items(),
        "total": carrito.total()
    }
    return render(request, "pos/panel.html", contexto)

@empleado_required
def inventario_pos(request):
    token = request.session.get("api_token")
    api = POSAPIClient(token=token)

    # Si hay búsqueda
    query = request.GET.get("q", "").strip()
    url = f"{api.base_url}/stock/"
    if query:
        url += f"?search={query}"

    respuesta = api.session.get(url)
    data = respuesta.json()
    stock_items = data.get("results", data)

    vinos = []
    for item in stock_items:
        vino = item.get("vino")
        if vino:
            vino["stock_cantidad"] = item.get("cantidad", 0)
            vinos.append(vino)

    return render(request, "pos/inventario.html", {"vinos": vinos, "query": query})


@empleado_required
def registrar_venta_pos(request, vino_id):
    if request.method != "POST":
        return redirect("pos:panel_pos")

    cantidad = int(request.POST.get("cantidad", 1))
    token = request.session.get("api_token")

    if not token:
        messages.error(request, "No hay token API. Inicie sesión nuevamente.")
        return redirect("pos:login_pos")

    api = POSAPIClient(token=token)

    # Construcción del payload de venta
    try:
        vino_id = int(vino_id)
        vino = next(v for v in api.get_vinos().get("results", []) if v["id"] == vino_id)
        precio_unitario = float(vino["precio_venta"])
        subtotal = precio_unitario * cantidad
    except StopIteration:
        messages.error(request, "Vino no encontrado en la API.")
        return redirect("pos:panel_pos")

    detalles = [
        {
            "vino": vino_id,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal,
        }
    ]

    resultado = api.registrar_venta(detalles)

    if isinstance(resultado, dict) and resultado.get("id"):
        messages.success(request, f"Venta registrada correctamente: {vino['nombre']} x{cantidad}.")
    else:
        messages.error(request, f"Error al registrar venta: {resultado}")

    return redirect("pos:panel_pos")


@empleado_required
def resumen_pos(request):
    hoy = now().date()
    inicio = request.GET.get("inicio") or hoy
    fin = request.GET.get("fin") or hoy

    resumen = (
        DetalleVenta.objects.filter(venta__fecha__date__range=[inicio, fin])
        .values("vino__nombre")
        .annotate(
            cantidad_vendida=Sum("cantidad"),
            total_vendido=Sum(
                ExpressionWrapper(
                    F("precio_unitario") * F("cantidad"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            ),
        )
        .order_by("-cantidad_vendida")
    )
    total_periodo = sum([r["total_vendido"] for r in resumen]) if resumen else 0

    return render(
        request,
        "pos/resumen.html",
        {"resumen": resumen, "inicio": inicio, "fin": fin, "total_periodo": total_periodo},
    )

@empleado_required
def buscar_codigo(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        token = request.session.get("api_token")
        api = POSAPIClient(token=token)

        # búsqueda directa en API
        response = api.session.get(f"{api.base_url}/vinos/?search={codigo}")
        data = response.json()
        vinos = data.get("results", data)

        # cargar carrito existente para mostrarlo también
        carrito = CarritoPOS(request)

        contexto = {
            "vinos": vinos,
            "carrito": carrito.items(),
            "total": carrito.total()
        }
        return render(request, "pos/panel.html", contexto)

    return redirect("pos:panel_pos")

