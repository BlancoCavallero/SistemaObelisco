"""Sales routes."""

from django.urls import path

from .views import ClienteViewSet, VentaListCreateView

urlpatterns = [
    path("ventas/", VentaListCreateView.as_view(), name="venta-list-create"),
    path("clientes/", ClienteViewSet.as_view({"get": "list", "post": "create"}), name="clientes"),
]
