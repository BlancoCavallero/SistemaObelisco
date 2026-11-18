"""Catalog URL routes."""

from django.urls import path

from .catalogo_publico import CatalogoPublicoView
from .precios import CargaPreciosView, FaltantesView, HistorialPreciosView
from .views import (
    CategoriaViewSet,
    ColoresView,
    ProductoBuscarView,
    ProductoListCreateView,
    TipoProductoViewSet,
)

urlpatterns = [
    path("catalogo/", CatalogoPublicoView.as_view(), name="catalogo-publico"),
    path("colores/", ColoresView.as_view(), name="colores"),
    path("productos/", ProductoListCreateView.as_view(), name="producto-list-create"),
    path("productos/buscar/", ProductoBuscarView.as_view(), name="producto-buscar"),
    path("precios/", CargaPreciosView.as_view(), name="precios-carga"),
    path("precios/faltantes/", FaltantesView.as_view(), name="precios-faltantes"),
    path("productos/<int:pk>/precios/", HistorialPreciosView.as_view(), name="producto-precios"),
    path(
        "categorias/",
        CategoriaViewSet.as_view({"get": "list", "post": "create"}),
        name="categorias",
    ),
    path("tipos/", TipoProductoViewSet.as_view({"get": "list", "post": "create"}), name="tipos"),
]
