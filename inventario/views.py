"""Warehouse endpoints: register movements and read derived stock."""

from django.db.models import Sum
from rest_framework import generics
from rest_framework.response import Response

from catalogo.models import Producto

from .models import Movimiento
from .serializers import MovimientoSerializer


class MovimientoListCreateView(generics.ListCreateAPIView):
    queryset = Movimiento.objects.select_related("producto")
    serializer_class = MovimientoSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class StockListView(generics.ListAPIView):
    """Current stock per product, derived from the ledger. Nothing is stored."""

    serializer_class = MovimientoSerializer

    def get_queryset(self):
        return (
            Producto.objects.filter(activo=True, movimientos__isnull=False)
            .annotate(total=Sum("movimientos__cantidad"))
            .order_by("id")
        )

    def list(self, request, *args, **kwargs):
        filas = [
            {
                "producto": producto.pk,
                "id_visible": producto.id_visible,
                "nombre": producto.nombre,
                "total": producto.total,
            }
            for producto in self.get_queryset()
        ]
        return Response(filas)
