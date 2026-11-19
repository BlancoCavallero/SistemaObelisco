"""Warehouse URL routes."""

from django.urls import path

from .ubicaciones import AlmacenViewSet, PosicionViewSet, SectorViewSet
from .views import (
    ArmarView,
    ConteoView,
    HistorialMovimientosView,
    MovimientoListCreateView,
    StockListView,
    StockPorUbicacionView,
    TransferirView,
)

urlpatterns = [
    path("conteo/", ConteoView.as_view(), name="conteo"),
    path("movimientos/", MovimientoListCreateView.as_view(), name="movimiento-list-create"),
    path("movimientos/armar/", ArmarView.as_view(), name="movimiento-armar"),
    path("movimientos/transferir/", TransferirView.as_view(), name="movimiento-transferir"),
    path(
        "productos/<int:pk>/movimientos/",
        HistorialMovimientosView.as_view(),
        name="producto-movimientos",
    ),
    path("stock/", StockListView.as_view(), name="stock-list"),
    path(
        "stock/ubicaciones/",
        StockPorUbicacionView.as_view(),
        name="stock-ubicaciones",
    ),
    path("almacenes/", AlmacenViewSet.as_view({"get": "list", "post": "create"}), name="almacenes"),
    path("sectores/", SectorViewSet.as_view({"get": "list", "post": "create"}), name="sectores"),
    path(
        "posiciones/",
        PosicionViewSet.as_view({"get": "list", "post": "create"}),
        name="posiciones",
    ),
]
