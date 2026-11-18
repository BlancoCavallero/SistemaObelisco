"""Public catalog: what a customer sees. No authentication, and no prices.

Prices are deliberately absent: publishing them would freeze a value that today is
computed as factory list x margin and resolved at the counter. The catalog invites a
consultation; the price belongs to the staff surface.
"""

from django.db.models import Sum
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Producto


class CatalogoPublicoView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        productos = (
            Producto.objects.select_related("tipo__categoria")
            .filter(activo=True)
            .annotate(stock=Sum("movimientos__cantidad"))
            .filter(stock__gt=0)
            .order_by("tipo__categoria__nombre", "tipo__nombre", "color")
        )

        categoria = request.query_params.get("categoria")
        if categoria:
            productos = productos.filter(tipo__categoria__nombre__iexact=categoria)

        filas = [self._fila(producto) for producto in productos]

        indice = {}
        for producto in self._todos_disponibles():
            nombre = producto.tipo.categoria.nombre
            indice[nombre] = indice.get(nombre, 0) + 1

        return Response(
            {
                "categorias": [
                    {"nombre": nombre, "total": total} for nombre, total in indice.items()
                ],
                "productos": filas,
            }
        )

    def _todos_disponibles(self):
        return (
            Producto.objects.select_related("tipo__categoria")
            .filter(activo=True)
            .annotate(stock=Sum("movimientos__cantidad"))
            .filter(stock__gt=0)
        )

    def _fila(self, producto):
        imagen = producto.imagenes.first()
        return {
            "id": producto.pk,
            "id_visible": producto.id_visible,
            "nombre": producto.nombre,
            "categoria": producto.tipo.categoria.nombre,
            "tipo": producto.tipo.nombre,
            "color": producto.get_color_display(),
            "medidas": producto.medidas,
            "stock": producto.stock,
            "imagen": imagen.archivo.url if imagen and imagen.archivo else None,
        }
