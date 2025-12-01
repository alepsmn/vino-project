from rest_framework.permissions import BasePermission


class IsEmpleado(BasePermission):
    """
    Permite acceso solo a usuarios autenticados que tengan un empleado asociado.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and hasattr(user, "empleado")
            and getattr(user.empleado, "tienda", None) is not None
        )
