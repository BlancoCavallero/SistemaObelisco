"""Supplier endpoints."""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CanalContacto, Proveedor
from .serializers import ProveedorSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.filter(activo=True)
    serializer_class = ProveedorSerializer
    pagination_class = None


class CanalesView(APIView):
    """The closed list of contact channels, so the front never duplicates it."""

    def get(self, _request):
        return Response(
            [{"valor": valor, "etiqueta": etiqueta} for valor, etiqueta in CanalContacto.choices]
        )
