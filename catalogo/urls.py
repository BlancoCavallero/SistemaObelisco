"""Catalog URL routes."""

from django.urls import path

from .views import ProductoBuscarView, ProductoListCreateView

urlpatterns = [
    path("productos/", ProductoListCreateView.as_view(), name="producto-list-create"),
    path("productos/buscar/", ProductoBuscarView.as_view(), name="producto-buscar"),
]
