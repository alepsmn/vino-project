from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PerfilClienteForm, RegistroForm
from apps.ventas.models import Venta
from django.contrib import messages

# Create your views here.

def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            return redirect("usuarios:login")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, "Credenciales incorrectas.")
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def perfil(request):
    perfil = getattr(request.user, "perfilcliente", None)
    if perfil is None:
        from apps.usuarios.models import PerfilCliente
        perfil = PerfilCliente.objects.create(user=request.user)

    if request.method == "POST":
        form = PerfilClienteForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("usuarios:perfil")
    else:
        form = PerfilClienteForm(instance=perfil)

    ventas = Venta.objects.filter(cliente=request.user).order_by("-fecha")
    return render(request, "usuarios/perfil.html", {"form": form, "ventas": ventas})