from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from django.contrib.auth import login, authenticate, logout
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils.timezone import now
from apps.inventario.models import Vino
from apps.ventas.models import DetalleVenta
import requests

from .api_client import POSAPIClient

def empleado_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('/pos/login/')
        if not hasattr(user, 'empleado'):
            return redirect('/pos/login/')
        return view_func(request, *args, **kwargs)
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

    respuesta = api.get_vinos()
    # Si la API devuelve un dict con 'results', úsalo; si devuelve lista, úsala tal cual
    vinos = respuesta.get("results", respuesta) if isinstance(respuesta, dict) else respuesta

    contexto = {"vinos": vinos}
    return render(request, "pos/panel.html", contexto)

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
        vino = (
            Vino.objects.filter(codigo_barras=codigo).first()
            or Vino.objects.filter(nombre__icontains=codigo).first()
        )

        if not vino:
            messages.error(request, f"No se encontró ningún vino con '{codigo}'.")
            return redirect("pos:panel_pos")

        messages.success(request, f"{vino.nombre} encontrado. Listo para venta.")
        return redirect("pos:panel_pos")

    return redirect("pos:panel_pos")