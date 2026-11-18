"""Warehouse URL routes."""

from django.urls import path

from .views import MovimientoListCreateView, StockListView

urlpatterns = [
    path("movimientos/", MovimientoListCreateView.as_view(), name="movimiento-list-create"),
    path("stock/", StockListView.as_view(), name="stock-list"),
]
