from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PerfilClienteForm, RegistroForm
from apps.ventas.models import Venta
from apps.ventas.cart import merge_carts
from apps.usuarios.models import PerfilCliente
from apps.usuarios.forms import RegistroForm
from django.contrib import messages

# Create your views here.

def registro(request):
    next_url = request.POST.get("next") or request.GET.get("next") or "/"

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()

            # fusionar carrito ANTES del login
            merge_carts(request.session, user.id)

            login(request, user)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect(next_url)
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {
        "form": form,
        "next": next_url,
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            # fusionar carrito ANTES del login
            merge_carts(request.session, user.id)

            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def perfil_datos(request):
    perfil = getattr(request.user, "perfilcliente", None)
    if perfil is None:
        perfil = PerfilCliente.objects.create(user=request.user)

    if request.method == "POST":
        form = PerfilClienteForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("usuarios:perfil_datos")
    else:
        form = PerfilClienteForm(instance=perfil)

    return render(request, "usuarios/perfil_datos.html", {
        "form": form,
        "active_tab": "datos",
    })


@login_required
def perfil_pedidos(request):
    ventas = Venta.objects.filter(cliente=request.user).order_by("-fecha")
    return render(request, "usuarios/perfil_pedidos.html", {
        "ventas": ventas,
        "active_tab": "pedidos",
    })


@login_required
def perfil_favoritos(request):
    return render(request, "usuarios/perfil_favoritos.html", {
        "active_tab": "favoritos",
    })


@login_required
def perfil_colecciones(request):
    return render(request, "usuarios/perfil_colecciones.html", {
        "active_tab": "colecciones",
    })
