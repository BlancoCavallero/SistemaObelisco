"""Sales routes."""

from django.urls import path

from .views import ClienteViewSet, EntregarVentaView, VentaListCreateView, VentasPendientesView

urlpatterns = [
    path("ventas/", VentaListCreateView.as_view(), name="venta-list-create"),
    path("ventas/pendientes/", VentasPendientesView.as_view(), name="ventas-pendientes"),
    path(
        "ventas/<int:pk>/entregar/",
        EntregarVentaView.as_view(),
        name="venta-entregar",
    ),
    path(
        "clientes/",
        ClienteViewSet.as_view({"get": "list", "post": "create"}),
        name="clientes",
    ),
    path("clientes/morosos/", ClienteViewSet.as_view({"get": "morosos"}), name="clientes-morosos"),
    path(
        "clientes/<int:pk>/cuenta/",
        ClienteViewSet.as_view({"get": "cuenta"}),
        name="cliente-cuenta",
    ),
    path(
        "clientes/<int:pk>/cuenta/pagos/",
        ClienteViewSet.as_view({"post": "pago"}),
        name="cliente-pago",
    ),
]
