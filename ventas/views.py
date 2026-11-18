"""Sales and customer account endpoints."""

from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cliente, CuentaMovimiento, Venta
from .serializers import ClienteSerializer, VentaSerializer
from .services import registrar_pago, saldo_de, vencido_de


class VentaListCreateView(generics.ListCreateAPIView):
    queryset = Venta.objects.select_related("cliente").prefetch_related("lineas__producto")
    serializer_class = VentaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer
    pagination_class = None

    @action(detail=True, methods=["get"])
    def cuenta(self, _request, pk=None):
        cliente = self.get_object()
        movimientos = cliente.cuenta_movimientos.all()
        return Response(
            {
                "cliente": ClienteSerializer(cliente).data,
                "saldo": f"{saldo_de(cliente):.2f}",
                "vencido": f"{vencido_de(cliente):.2f}",
                "movimientos": [
                    {
                        "id": movimiento.pk,
                        "tipo": movimiento.tipo,
                        "monto": f"{movimiento.monto:.2f}",
                        "vencimiento": movimiento.vencimiento,
                        "motivo": movimiento.motivo,
                        "fecha": movimiento.fecha,
                    }
                    for movimiento in movimientos
                ],
            }
        )

    @action(detail=True, methods=["post"], url_path="cuenta/pagos")
    def pago(self, request, pk=None):
        cliente = self.get_object()
        try:
            monto = Decimal(str(request.data.get("monto", "")))
        except (InvalidOperation, TypeError):
            return Response(
                {"detail": "El monto no es un numero valido."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            registrar_pago(cliente, monto, request.user, request.data.get("motivo", ""))
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"saldo": f"{saldo_de(cliente):.2f}"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def morosos(self, _request):
        hoy = timezone.localdate()
        vencidos = (
            CuentaMovimiento.objects.filter(tipo="cargo", vencimiento__lt=hoy)
            .values("cliente")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        filas = []
        for fila in vencidos:
            cliente = Cliente.objects.get(pk=fila["cliente"])
            vencido = vencido_de(cliente)
            if vencido > 0:
                filas.append(
                    {"cliente": ClienteSerializer(cliente).data, "vencido": f"{vencido:.2f}"}
                )
        return Response(filas)
