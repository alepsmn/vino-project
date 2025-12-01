from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging
log = logging.getLogger("app")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Si DRF ya generó respuesta, normalizar formato
    if response is None:
        log.error(
            "error_interno",
            extra={
                "exception": str(exc),
                "view": context.get("view").__class__.__name__ if context.get("view") else None,
                "user_id": context["request"].user.id if context.get("request") else None,
            }
        )

        return Response({
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "details": "Error interno del servidor.",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

