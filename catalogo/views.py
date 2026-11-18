"""Catalog endpoints: search first, create second."""

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Producto
from .serializers import ProductoSerializer


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
