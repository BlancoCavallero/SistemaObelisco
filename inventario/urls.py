"""Warehouse URL routes."""

from django.urls import path

from .views import (
    ArmarView,
    HistorialMovimientosView,
    MovimientoListCreateView,
    StockListView,
    TransferirView,
)

urlpatterns = [
    path("movimientos/", MovimientoListCreateView.as_view(), name="movimiento-list-create"),
    path("movimientos/armar/", ArmarView.as_view(), name="movimiento-armar"),
    path("movimientos/transferir/", TransferirView.as_view(), name="movimiento-transferir"),
    path(
        "productos/<int:pk>/movimientos/",
        HistorialMovimientosView.as_view(),
        name="producto-movimientos",
    ),
    path("stock/", StockListView.as_view(), name="stock-list"),
]
