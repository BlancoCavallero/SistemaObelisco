"""Sales and customer account endpoints."""

from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cliente, CuentaMovimiento, Venta
from .serializers import ClienteSerializer, VentaSerializer
from .services import marcar_entrega, registrar_pago, saldo_de, vencido_de


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


def _pendiente(venta):
    return {
        "id": venta.pk,
        "fecha": venta.fecha,
        "cliente": venta.cliente.nombre if venta.cliente_id else "",
        "ciudad": venta.cliente.ciudad if venta.cliente_id else "",
        "lineas": [
            {
                "producto": linea.producto_id,
                "nombre": linea.producto.nombre,
                "cantidad": linea.cantidad,
            }
            for linea in venta.lineas.all()
            if not linea.entregada
        ],
    }


class VentasPendientesView(APIView):
    """Ventas confirmadas con mercaderia que todavia no salio del deposito."""

    def get(self, _request):
        ventas = (
            Venta.objects.filter(confirmada=True, lineas__entregada=False)
            .distinct()
            .select_related("cliente")
            .prefetch_related("lineas__producto")
            .order_by("fecha", "id")
        )
        return Response({"ventas": [_pendiente(venta) for venta in ventas]})


class EntregarVentaView(APIView):
    """Marcar la entrega: cierra lineas y no toca el stock (D-07)."""

    def post(self, _request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        try:
            cerradas = marcar_entrega(venta)
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"venta": venta.pk, "lineas": cerradas})
