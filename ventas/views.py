"""Sales endpoint: create-and-confirm, plus the customer directory."""

from rest_framework import generics, viewsets

from .models import Cliente, Venta
from .serializers import ClienteSerializer, VentaSerializer


class VentaListCreateView(generics.ListCreateAPIView):
    queryset = Venta.objects.select_related("cliente").prefetch_related("lineas__producto")
    serializer_class = VentaSerializer

    def perform_create(self, serializer):
        serializer.save()


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer
    pagination_class = None
