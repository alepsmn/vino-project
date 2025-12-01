# apps/pos/decorators.py

from functools import wraps
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


def empleado_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect("/pos/login/")

        # Superusuario: acceso total
        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Empleado: acceso normal
        if hasattr(user, "empleado"):
            return view_func(request, *args, **kwargs)

        # Sin permisos: cerrar sesión y redirigir
        messages.error(request, "No tienes permisos para acceder al POS.")
        logout(request)
        return redirect("/usuarios/login/")

    return wrapper
