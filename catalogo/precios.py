"""Loading factory list costs. Append-only and all-or-nothing."""

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PrecioLista, Producto
from .serializers import ProductoSerializer


class ValorSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    valor = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))


class CargaPreciosSerializer(serializers.Serializer):
    vigente_desde = serializers.DateField()
    valores = ValorSerializer(many=True, allow_empty=False)


class PrecioListaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioLista
        fields = ["id", "producto", "valor", "vigente_desde", "creado_en"]
        read_only_fields = ["creado_en"]


class CargaPreciosView(APIView):
    """Load costs for one factory list date.

    Partial application would be worse than no application: half a list means an
    unknown half of the catalogue is priced with the old cost. So the whole batch is
    validated and written inside one transaction.
    """

    def post(self, request):
        serializer = CargaPreciosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fecha = serializer.validated_data["vigente_desde"]
        valores = serializer.validated_data["valores"]

        ids = [valor["producto"].pk for valor in valores]
        ya_cargados = list(
            PrecioLista.objects.filter(vigente_desde=fecha, producto_id__in=ids).values_list(
                "producto__tipo__nombre", flat=True
            )
        )
        if ya_cargados:
            return Response(
                {
                    "detail": f"Ya hay un costo con fecha {fecha} para: "
                    + ", ".join(sorted(set(ya_cargados)))
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            creados = [
                PrecioLista(producto=valor["producto"], valor=valor["valor"], vigente_desde=fecha)
                for valor in valores
            ]
            PrecioLista.objects.bulk_create(creados)

        return Response({"creados": len(creados)}, status=status.HTTP_201_CREATED)


class FaltantesView(APIView):
    """Products with no cost at all: they cannot be sold until priced."""

    def get(self, _request):
        productos = Producto.objects.filter(activo=True, precios_lista__isnull=True)
        return Response(ProductoSerializer(productos, many=True).data)


class HistorialPreciosView(APIView):
    def get(self, _request, pk):
        producto = Producto.objects.get(pk=pk)
        precios = producto.precios_lista.order_by("-vigente_desde")
        return Response(PrecioListaSerializer(precios, many=True).data)
