"""Catalog URL routes."""

from django.urls import path

from .catalogo_publico import CatalogoPublicoView
from .views import ProductoBuscarView, ProductoListCreateView

urlpatterns = [
    path("catalogo/", CatalogoPublicoView.as_view(), name="catalogo-publico"),
    path("productos/", ProductoListCreateView.as_view(), name="producto-list-create"),
    path("productos/buscar/", ProductoBuscarView.as_view(), name="producto-buscar"),
]
