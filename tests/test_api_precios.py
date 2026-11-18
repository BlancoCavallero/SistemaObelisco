"""Cargar costos de la lista de fabrica, y hacer visible lo que falta.

Un producto sin costo no se puede vender: la pantalla de precios existe para que eso
se vea antes de que un vendedor se choque con un rechazo en el mostrador.
"""

import datetime as dt
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from catalogo.models import PrecioLista


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def otro_producto(tipo):
    from catalogo.models import Producto

    return Producto.objects.create(tipo=tipo, color="negro", alto_cm=80, ancho_cm=80, largo_cm=150)


def test_cargar_un_costo_queda_vigente(cliente, producto):
    respuesta = cliente.post(
        "/api/precios/",
        {"vigente_desde": "2026-01-01", "valores": [{"producto": producto.pk, "valor": "10000"}]},
        format="json",
    )

    assert respuesta.status_code == 201
    assert producto.precio_venta(dt.date(2026, 3, 1)) == Decimal("11000")


def test_carga_masiva_de_varios_productos(cliente, producto, otro_producto):
    respuesta = cliente.post(
        "/api/precios/",
        {
            "vigente_desde": "2026-01-01",
            "valores": [
                {"producto": producto.pk, "valor": "10000"},
                {"producto": otro_producto.pk, "valor": "20000"},
            ],
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert PrecioLista.objects.count() == 2


def test_no_se_pisa_un_costo_de_la_misma_fecha(cliente, producto):
    PrecioLista.objects.create(
        producto=producto, valor=Decimal("10000"), vigente_desde=dt.date(2026, 1, 1)
    )

    respuesta = cliente.post(
        "/api/precios/",
        {"vigente_desde": "2026-01-01", "valores": [{"producto": producto.pk, "valor": "99999"}]},
        format="json",
    )

    assert respuesta.status_code == 400
    assert PrecioLista.objects.get(producto=producto).valor == Decimal("10000")


def test_una_carga_parcial_falla_completa(cliente, producto, otro_producto):
    """O entran todos los valores, o no entra ninguno: media lista es peor que ninguna."""
    PrecioLista.objects.create(
        producto=otro_producto, valor=Decimal("5000"), vigente_desde=dt.date(2026, 1, 1)
    )

    respuesta = cliente.post(
        "/api/precios/",
        {
            "vigente_desde": "2026-01-01",
            "valores": [
                {"producto": producto.pk, "valor": "10000"},
                {"producto": otro_producto.pk, "valor": "20000"},
            ],
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert not PrecioLista.objects.filter(producto=producto).exists()


def test_valor_negativo_devuelve_400(cliente, producto):
    respuesta = cliente.post(
        "/api/precios/",
        {"vigente_desde": "2026-01-01", "valores": [{"producto": producto.pk, "valor": "-5"}]},
        format="json",
    )
    assert respuesta.status_code == 400


def test_lista_de_productos_sin_costo(cliente, producto, otro_producto):
    PrecioLista.objects.create(
        producto=producto, valor=Decimal("10000"), vigente_desde=dt.date(2026, 1, 1)
    )

    respuesta = cliente.get("/api/precios/faltantes/")

    assert respuesta.status_code == 200
    assert [p["id"] for p in respuesta.data] == [otro_producto.pk]


def test_la_carga_de_precios_requiere_sesion(producto):
    respuesta = APIClient().post(
        "/api/precios/",
        {"vigente_desde": "2026-01-01", "valores": [{"producto": producto.pk, "valor": "1"}]},
        format="json",
    )
    assert respuesta.status_code in (401, 403)


def test_ver_el_historial_de_costos_de_un_producto(cliente, producto):
    for fecha, valor in [("2026-01-01", "10000"), ("2026-06-01", "20000")]:
        PrecioLista.objects.create(
            producto=producto, valor=Decimal(valor), vigente_desde=dt.date.fromisoformat(fecha)
        )

    respuesta = cliente.get(f"/api/productos/{producto.pk}/precios/")

    assert respuesta.status_code == 200
    assert [p["valor"] for p in respuesta.data] == ["20000.00", "10000.00"]
