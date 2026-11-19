"""Supplier routes."""

from django.urls import path

from .views import CanalesView, ProveedorViewSet

urlpatterns = [
    path("proveedores/canales/", CanalesView.as_view(), name="proveedores-canales"),
    path(
        "proveedores/",
        ProveedorViewSet.as_view(
            {"get": "list", "post": "create", "patch": "partial_update", "put": "update"}
        ),
        name="proveedores",
    ),
    path(
        "proveedores/<int:pk>/",
        ProveedorViewSet.as_view({"patch": "partial_update", "put": "update", "get": "retrieve"}),
        name="proveedor-detalle",
    ),
]
