"""El precio es un calculo con vigencia, no un campo que se edita.

Regla (D-06): precio = costo de lista del proveedor vigente x (1 + margen de la categoria
vigente). Se congela en la linea de la venta; el producto nunca guarda un precio.
"""

import datetime as dt
from decimal import Decimal

import pytest

from catalogo.models import PrecioLista
from core.models import Parametro

HOY = dt.date(2026, 3, 1)


@pytest.fixture
def con_costo(producto):
    PrecioLista.objects.create(
        producto=producto, valor=Decimal("10000"), vigente_desde=dt.date(2026, 1, 1)
    )
    return producto


def test_sin_costo_no_hay_precio(producto):
    assert producto.precio_venta(HOY) is None


def test_margen_por_defecto_es_diez_por_ciento(con_costo):
    assert con_costo.precio_venta(HOY) == Decimal("11000")


def test_margen_por_categoria_pisa_al_default(con_costo):
    Parametro.objects.create(
        clave="margen",
        valor={"default": 0.10, "Muebles": 0.50},
        vigente_desde=dt.date(2026, 1, 1),
    )
    assert con_costo.precio_venta(HOY) == Decimal("15000")


def test_sin_parametro_cargado_usa_el_diez_por_ciento(con_costo):
    assert Parametro.valor_vigente("margen", HOY) is None
    assert con_costo.precio_venta(HOY) == Decimal("11000")


def test_usa_el_costo_vigente_a_la_fecha(con_costo):
    PrecioLista.objects.create(
        producto=con_costo, valor=Decimal("20000"), vigente_desde=dt.date(2026, 6, 1)
    )

    assert con_costo.precio_venta(dt.date(2026, 3, 1)) == Decimal("11000")
    assert con_costo.precio_venta(dt.date(2026, 7, 1)) == Decimal("22000")


def test_el_margen_tambien_tiene_vigencia(con_costo):
    Parametro.objects.create(
        clave="margen", valor={"default": 0.10}, vigente_desde=dt.date(2026, 1, 1)
    )
    Parametro.objects.create(
        clave="margen", valor={"default": 0.20}, vigente_desde=dt.date(2026, 6, 1)
    )

    assert con_costo.precio_venta(dt.date(2026, 3, 1)) == Decimal("11000")
    assert con_costo.precio_venta(dt.date(2026, 7, 1)) == Decimal("12000")


def test_el_precio_se_redondea_a_la_centena(con_costo):
    PrecioLista.objects.filter(producto=con_costo).delete()
    PrecioLista.objects.create(
        producto=con_costo, valor=Decimal("1234"), vigente_desde=dt.date(2026, 1, 1)
    )

    # 1234 * 1.10 = 1357.4 -> 1400
    assert con_costo.precio_venta(HOY) == Decimal("1400")


def test_el_producto_no_guarda_precio(con_costo):
    from django.core.exceptions import FieldDoesNotExist

    for campo in ("precio", "precio_venta", "costo"):
        with pytest.raises(FieldDoesNotExist):
            con_costo._meta.get_field(campo)


def test_cambiar_el_margen_no_reescribe_el_pasado(con_costo):
    Parametro.objects.create(
        clave="margen", valor={"default": 0.10}, vigente_desde=dt.date(2026, 1, 1)
    )
    antes = con_costo.precio_venta(dt.date(2026, 3, 1))

    Parametro.objects.create(
        clave="margen", valor={"default": 0.30}, vigente_desde=dt.date(2026, 5, 1)
    )

    assert con_costo.precio_venta(dt.date(2026, 3, 1)) == antes
