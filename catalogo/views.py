"""Catalog endpoints: search first, create second."""

from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import COLORES, Categoria, Producto, TipoProducto
from .serializers import (
    CategoriaSerializer,
    ProductoSerializer,
    TipoProductoSerializer,
)


class ProductoBuscarView(generics.ListAPIView):
    """Find candidates before creating anything."""

    serializer_class = ProductoSerializer

    def get_queryset(self):
        queryset = Producto.objects.select_related("tipo__categoria").filter(activo=True)
        params = self.request.query_params

        exactos = (
            ("tipo", "tipo_id"),
            ("color", "color"),
            ("alto_cm", "alto_cm"),
            ("ancho_cm", "ancho_cm"),
            ("largo_cm", "largo_cm"),
        )
        for param, field in exactos:
            value = params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})

        if params.get("categoria"):
            queryset = queryset.filter(tipo__categoria__nombre__iexact=params["categoria"])

        term = params.get("q")
        if term:
            queryset = queryset.filter(
                Q(tipo__nombre__icontains=term)
                | Q(color__icontains=term)
                | Q(modelo__icontains=term)
            )

        return queryset.order_by("tipo__nombre", "color", "alto_cm")


class ProductoListCreateView(generics.ListCreateAPIView):
    """Create a product, or refuse and point at the existing one."""

    queryset = Producto.objects.select_related("tipo__categoria")
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        existente = serializer.buscar_duplicado()
        if existente is not None:
            return Response(
                {
                    "detail": "Ese producto ya existe. Suma cantidad en lugar de crear otro.",
                    "producto_existente": ProductoSerializer(existente).data,
                },
                status=status.HTTP_409_CONFLICT,
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoriaViewSet(viewsets.ModelViewSet):
    """Categories grow as the business adds lines: they are data, not code."""

    serializer_class = CategoriaSerializer
    pagination_class = None

    def get_queryset(self):
        return Categoria.objects.filter(activo=True)


class TipoProductoViewSet(viewsets.ModelViewSet):
    serializer_class = TipoProductoSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = TipoProducto.objects.select_related("categoria").all()
        categoria = self.request.query_params.get("categoria")
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        return queryset


class ColoresView(APIView):
    """The closed color list. Free text here would create three greys."""

    def get(self, _request):
        return Response([{"valor": valor, "etiqueta": etiqueta} for valor, etiqueta in COLORES])


class ProductoDetalleView(generics.RetrieveAPIView):
    """One product, for the staff sheet.

    Fetching the whole list to show one article works with ten products and stops
    working with five hundred, so the detail has its own route.
    """

    serializer_class = ProductoSerializer
    queryset = Producto.objects.select_related("tipo__categoria")
