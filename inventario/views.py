"""Warehouse endpoints: register movements and read derived stock."""

import uuid

from django.db import transaction
from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.models import Producto

from .models import Almacen, EstadoArticulo, Movimiento, Posicion, TipoMovimiento
from .serializers import (
    ArmarSerializer,
    MovimientoSerializer,
    TransferirSerializer,
)


def _stock(producto, estado=None, posicion=None):
    """Signed sum of the ledger, optionally narrowed to one dimension."""
    queryset = Movimiento.objects.filter(producto=producto)
    if estado is not None:
        queryset = queryset.filter(estado=estado)
    if posicion is not None:
        queryset = queryset.filter(posicion=posicion)
    return queryset.aggregate(total=Sum("cantidad"))["total"] or 0


class MovimientoListCreateView(generics.ListCreateAPIView):
    queryset = Movimiento.objects.select_related("producto")
    serializer_class = MovimientoSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ArmarView(APIView):
    """Move units from box to assembled. The total does not change."""

    def post(self, request):
        serializer = ArmarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=datos["producto"].pk)
            disponible = _stock(producto, estado=EstadoArticulo.EN_CAJA)
            if disponible < datos["cantidad"]:
                return Response(
                    {"detail": f"Solo hay {disponible} en caja de {producto.nombre}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            referencia = uuid.uuid4().hex
            Movimiento.objects.create(
                producto=producto,
                cantidad=-datos["cantidad"],
                tipo=TipoMovimiento.ARMADO,
                estado=EstadoArticulo.EN_CAJA,
                posicion=datos.get("posicion"),
                referencia=referencia,
                usuario=request.user,
            )
            Movimiento.objects.create(
                producto=producto,
                cantidad=datos["cantidad"],
                tipo=TipoMovimiento.ARMADO,
                estado=EstadoArticulo.LISTO,
                posicion=datos.get("posicion"),
                referencia=referencia,
                usuario=request.user,
            )

        return Response(
            {"referencia": referencia, "armado": datos["cantidad"]},
            status=status.HTTP_201_CREATED,
        )


class TransferirView(APIView):
    """Move units between positions. The total does not change."""

    def post(self, request):
        serializer = TransferirSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=datos["producto"].pk)
            disponible = _stock(producto, estado=datos["estado"], posicion=datos["desde"])
            if disponible < datos["cantidad"]:
                return Response(
                    {"detail": f"Solo hay {disponible} en la posicion de origen."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            referencia = uuid.uuid4().hex
            for posicion, signo in ((datos["desde"], -1), (datos["hasta"], 1)):
                Movimiento.objects.create(
                    producto=producto,
                    cantidad=signo * datos["cantidad"],
                    tipo=TipoMovimiento.TRANSFERENCIA,
                    estado=datos["estado"],
                    posicion=posicion,
                    referencia=referencia,
                    usuario=request.user,
                )

        return Response(
            {"referencia": referencia, "transferido": datos["cantidad"]},
            status=status.HTTP_201_CREATED,
        )


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
        productos = list(self.get_queryset())
        desglose = {}
        for fila in (
            Movimiento.objects.filter(producto__in=productos)
            .values("producto", "estado")
            .annotate(total=Sum("cantidad"))
        ):
            desglose.setdefault(fila["producto"], {})[fila["estado"]] = fila["total"]

        filas = [
            {
                "producto": producto.pk,
                "id_visible": producto.id_visible,
                "nombre": producto.nombre,
                "total": producto.total,
                "en_caja": desglose.get(producto.pk, {}).get(EstadoArticulo.EN_CAJA, 0),
                "listo": desglose.get(producto.pk, {}).get(EstadoArticulo.LISTO, 0),
            }
            for producto in productos
        ]
        return Response(filas)


class HistorialMovimientosView(APIView):
    """Every movement of one product, newest first, with its running balance.

    This is the answer to "why are there 3 and not 7". Without it, a stock adjustment
    is a magic number and the system loses trust the first time something is missing.
    """

    def get(self, _request, pk):
        from django.shortcuts import get_object_or_404

        from catalogo.models import Producto

        producto = get_object_or_404(Producto, pk=pk)
        movimientos = producto.movimientos.select_related("usuario").order_by("fecha", "id")

        acumulado = 0
        filas = []
        for movimiento in movimientos:
            acumulado += movimiento.cantidad
            filas.append(
                {
                    "id": movimiento.pk,
                    "fecha": movimiento.fecha,
                    "tipo": movimiento.tipo,
                    "cantidad": movimiento.cantidad,
                    "estado": movimiento.estado,
                    "motivo": movimiento.motivo,
                    "referencia": movimiento.referencia,
                    "usuario": movimiento.usuario.get_full_name() or movimiento.usuario.username,
                    "saldo_acumulado": acumulado,
                }
            )

        return Response(
            {
                "producto": {
                    "id": producto.pk,
                    "id_visible": producto.id_visible,
                    "nombre": producto.nombre,
                },
                "total": acumulado,
                "movimientos": list(reversed(filas)),
            }
        )


class StockPorUbicacionView(APIView):
    """How much is in each place, including the stock that has no location.

    The ledger never requires a position (A15), so part of the stock is unlocated. It
    has to be shown explicitly: hiding it makes the per-store totals disagree with the
    product total, and then nobody trusts either number.
    """

    def get(self, request):
        filas_brutas = (
            Movimiento.objects.values("producto", "posicion", "estado")
            .annotate(total=Sum("cantidad"))
            .order_by()
        )

        almacen_filtro = request.query_params.get("almacen")
        productos = {p.pk: p for p in Producto.objects.select_related("tipo__categoria")}
        posiciones = {
            p.pk: p
            for p in _posiciones_con_ruta()
        }

        filas = []
        for fila in filas_brutas:
            if fila["total"] == 0:
                continue
            posicion = posiciones.get(fila["posicion"])
            if almacen_filtro and (
                posicion is None or str(posicion.sector.almacen_id) != str(almacen_filtro)
            ):
                continue
            producto = productos.get(fila["producto"])
            if producto is None:
                continue
            filas.append(
                {
                    "producto": producto.pk,
                    "id_visible": producto.id_visible,
                    "nombre": producto.nombre,
                    "estado": fila["estado"],
                    "posicion": fila["posicion"],
                    "etiqueta": (
                        f"{posicion.sector.almacen.codigo}/{posicion.sector.codigo}/"
                        f"{posicion.codigo}"
                        if posicion
                        else "sin ubicar"
                    ),
                    "cantidad": fila["total"],
                }
            )

        totales = {}
        for fila in filas:
            clave = fila["etiqueta"].split("/")[0] if fila["posicion"] else "sin ubicar"
            totales[clave] = totales.get(clave, 0) + fila["cantidad"]

        almacenes = [
            {
                "id": almacen.pk,
                "codigo": almacen.codigo,
                "nombre": almacen.nombre,
                "total": totales.get(almacen.codigo, 0),
            }
            for almacen in Almacen.objects.all()
        ]
        if totales.get("sin ubicar"):
            almacenes.append(
                {
                    "id": None,
                    "codigo": "sin ubicar",
                    "nombre": "Mercaderia sin ubicacion asignada",
                    "total": totales["sin ubicar"],
                }
            )

        filas.sort(key=lambda f: (f["nombre"], f["etiqueta"], f["estado"]))
        return Response({"almacenes": almacenes, "filas": filas})


def _posiciones_con_ruta():
    return Posicion.objects.select_related("sector__almacen")
