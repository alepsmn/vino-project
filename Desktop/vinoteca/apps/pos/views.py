# apps/pos/views.py

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

from apps.pos.api_client import POSAPIClient
from apps.pos.utils.carrito_pos import CarritoPOS
from apps.pos.decorators import empleado_required
from apps.ventas.models import DetalleVenta


def login_pos(request):
    if request.user.is_authenticated and request.session.get("api_token"):
        return redirect("pos:panel_pos")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if not user:
            return render(request, "pos/login.html", {"error": "Credenciales incorrectas"})

        login(request, user)

        api = POSAPIClient()
        token = api.login(username, password)
        if not token:
            messages.error(request, "No se pudo obtener token API.")
            logout(request)
            return redirect("pos:login_pos")

        request.session["api_token"] = token
        return redirect("pos:panel_pos")

    return render(request, "pos/login.html")


@empleado_required
def logout_pos(request):
    logout(request)
    return redirect("pos:login_pos")


@empleado_required
def panel_pos(request):
    token = request.session.get("api_token")
    api = POSAPIClient(token=token)

    productos = []
    url = f"{api.base_url}/stock/"

    while url:
        r = api.session.get(url)
        data = r.json()

        for item in data.get("results", []):
            p = item.get("producto")
            if not p:
                continue
            p["stock_cantidad"] = item.get("cantidad", 0)
            productos.append(p)

        url = data.get("next")

    carrito = CarritoPOS(request)
    return render(
        request,
        "pos/panel.html",
        {"productos": productos, "carrito": carrito.items(), "total": carrito.total()},
    )


@empleado_required
def inventario_pos(request):
    token = request.session.get("api_token")
    api = POSAPIClient(token=token)

    query = request.GET.get("q", "").strip()
    url = f"{api.base_url}/stock/"
    if query:
        url += f"?search={query}"

    productos = []

    while url:
        r = api.session.get(url)
        data = r.json()

        for item in data.get("results", []):
            p = item.get("producto")
            if p:
                p["stock_cantidad"] = item.get("cantidad", 0)
                productos.append(p)

        url = data.get("next")

    return render(
        request,
        "pos/inventario.html",
        {"productos": productos, "query": query},
    )


@empleado_required
def resumen_pos(request):
    hoy = now().date()
    inicio = request.GET.get("inicio") or hoy
    fin = request.GET.get("fin") or hoy

    resumen = (
        DetalleVenta.objects.filter(venta__fecha__date__range=[inicio, fin])
        .values("producto__nombre")
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

    total_periodo = (
        sum(r["total_vendido"] for r in resumen) if resumen else Decimal("0")
    )

    return render(
        request,
        "pos/resumen.html",
        {"resumen": resumen, "inicio": inicio, "fin": fin, "total_periodo": total_periodo},
    )


@empleado_required
def buscar_codigo(request):
    if request.method != "POST":
        return redirect("pos:panel_pos")

    codigo = request.POST.get("codigo", "").strip()
    token = request.session.get("api_token")
    api = POSAPIClient(token=token)

    r = api.session.get(f"{api.base_url}/productos/?search={codigo}")
    try:
        data = r.json()
    except:
        messages.error(request, "Error en API")
        return redirect("pos:panel_pos")

    productos = data.get("results") or []
    if not productos:
        messages.warning(request, "No se encontró producto")
        return redirect("pos:panel_pos")

    carrito = CarritoPOS(request)
    return render(
        request,
        "pos/panel.html",
        {"productos": productos, "carrito": carrito.items(), "total": carrito.total()},
    )
