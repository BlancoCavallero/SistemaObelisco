"""Stock derived from the ledger. One place, so the rule is not duplicated."""

from django.db.models import Sum

from .models import Movimiento


def stock_de(producto, estado=None, posicion=None):
    """Signed sum of movements for a product, optionally narrowed to one dimension."""
    queryset = Movimiento.objects.filter(producto=producto)
    if estado is not None:
        queryset = queryset.filter(estado=estado)
    if posicion is not None:
        queryset = queryset.filter(posicion=posicion)
    return queryset.aggregate(total=Sum("cantidad"))["total"] or 0
