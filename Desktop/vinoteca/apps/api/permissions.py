from rest_framework.permissions import BasePermission


class IsEmpleado(BasePermission):
    """
    Permite acceso solo a usuarios autenticados que tengan un empleado asociado.
    """

    def has_permission(self, request, view):
        user = request.user

        ok = (
            user
            and user.is_authenticated
            and hasattr(user, "empleado")
            and getattr(user.empleado, "tienda", None) is not None
        )

        if not ok:
            log.warning(
                "acceso_denegado",
                extra={
                    "user_id": getattr(user, "id", None),
                    "view": view.__class__.__name__,
                    "reason": "Usuario sin empleado o sin tienda asignada"
                }
            )

        return ok
