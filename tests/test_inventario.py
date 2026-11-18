"""The movement ledger is the single source of truth and is append-only."""

import pytest
from django.core.exceptions import ValidationError

from inventario.models import Movimiento, TipoMovimiento


def _movimiento(producto, usuario, cantidad, tipo=TipoMovimiento.ENTRADA_COMPRA):
    return Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=cantidad, tipo=tipo
    )


def test_movimiento_no_se_puede_editar(producto, usuario):
    mov = _movimiento(producto, usuario, 5)
    mov.cantidad = 9
    with pytest.raises(ValidationError):
        mov.save()


def test_movimiento_no_se_puede_borrar(producto, usuario):
    mov = _movimiento(producto, usuario, 5)
    with pytest.raises(ValidationError):
        mov.delete()
    assert Movimiento.objects.filter(pk=mov.pk).exists()


def test_movimiento_no_admite_cantidad_cero(producto, usuario):
    with pytest.raises(ValidationError):
        _movimiento(producto, usuario, 0)


def test_stock_es_la_suma_de_movimientos(producto, usuario):
    _movimiento(producto, usuario, 10)
    _movimiento(producto, usuario, 3, tipo=TipoMovimiento.ENTRADA_INVENTARIO_INICIAL)
    _movimiento(producto, usuario, -4, tipo=TipoMovimiento.VENTA)

    stock = dict(Movimiento.objects.stock_por_producto().values_list("producto", "total"))
    assert stock[producto.pk] == 9


def test_posicion_no_es_obligatoria(producto, usuario):
    mov = _movimiento(producto, usuario, 1)
    assert mov.posicion is None
