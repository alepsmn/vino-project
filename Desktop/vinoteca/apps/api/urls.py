# apps/api/urls.py
from django.urls import path, include
from apps.api.v1 import urls as api_v1

urlpatterns = [
    path("api/v1/", include(api_v1)),
]
