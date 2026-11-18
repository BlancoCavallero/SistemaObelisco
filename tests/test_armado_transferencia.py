"""Armado y transferencia no cambian el total: cambian estado o ubicacion.

Por eso cada uno se registra como un par de movimientos (-1 origen, +1 destino) que
comparten una referencia. El invariante sigue siendo uno: el stock total es la suma de
las cantidades firmadas.
"""

import pytest
from django.db.models import Sum
from rest_framework.test import APIClient

from inventario.models import Almacen, Movimiento, Posicion, Sector


@pytest.fixture
def cliente(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


@pytest.fixture
def deposito(db):
    return Posicion.objects.create(
        sector=Sector.objects.create(
            almacen=Almacen.objects.create(codigo="ALM-01", nombre="Deposito"), codigo="SEC-01"
        ),
        codigo="POS-01",
    )


@pytest.fixture
def salon(db):
    return Posicion.objects.create(
        sector=Sector.objects.create(
            almacen=Almacen.objects.create(codigo="ALM-02", nombre="Salon"), codigo="SEC-01"
        ),
        codigo="POS-01",
    )


def _entrada(producto, usuario, cantidad, estado="en_caja", posicion=None):
    return Movimiento.objects.create(
        producto=producto,
        usuario=usuario,
        cantidad=cantidad,
        tipo="entrada_compra",
        estado=estado,
        posicion=posicion,
    )


def _total(producto, estado=None):
    qs = Movimiento.objects.filter(producto=producto)
    if estado:
        qs = qs.filter(estado=estado)
    return qs.aggregate(t=Sum("cantidad"))["t"] or 0


# --- armado ----------------------------------------------------------------


def test_armar_mueve_de_caja_a_listo_sin_cambiar_el_total(cliente, usuario, producto):
    _entrada(producto, usuario, 5)

    r = cliente.post(
        "/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 2}, format="json"
    )

    assert r.status_code == 201
    assert _total(producto) == 5
    assert _total(producto, "en_caja") == 3
    assert _total(producto, "listo") == 2


def test_armar_deja_un_par_de_movimientos_con_la_misma_referencia(cliente, usuario, producto):
    _entrada(producto, usuario, 5)
    cliente.post("/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 2}, format="json")

    pares = Movimiento.objects.filter(tipo="armado")
    assert pares.count() == 2
    assert len({m.referencia for m in pares}) == 1
    assert sorted(m.cantidad for m in pares) == [-2, 2]


def test_no_se_puede_armar_mas_de_lo_que_hay_en_caja(cliente, usuario, producto):
    _entrada(producto, usuario, 3)

    r = cliente.post(
        "/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 5}, format="json"
    )

    assert r.status_code == 400
    assert "en caja" in str(r.data).lower()
    assert Movimiento.objects.filter(tipo="armado").count() == 0
    assert _total(producto, "en_caja") == 3


def test_no_se_puede_armar_sin_stock(cliente, producto):
    r = cliente.post(
        "/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 1}, format="json"
    )
    assert r.status_code == 400
    assert Movimiento.objects.count() == 0


def test_armar_cantidad_cero_devuelve_400(cliente, usuario, producto):
    _entrada(producto, usuario, 5)
    r = cliente.post(
        "/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 0}, format="json"
    )
    assert r.status_code == 400


def test_armar_requiere_autenticacion(producto):
    r = APIClient().post(
        "/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 1}, format="json"
    )
    assert r.status_code in (401, 403)
    assert Movimiento.objects.count() == 0


# --- transferencia ---------------------------------------------------------


def test_transferir_mueve_entre_ubicaciones_sin_cambiar_el_total(
    cliente, usuario, producto, deposito, salon
):
    _entrada(producto, usuario, 4, estado="listo", posicion=deposito)

    r = cliente.post(
        "/api/movimientos/transferir/",
        {"producto": producto.pk, "cantidad": 3, "desde": deposito.pk, "hasta": salon.pk},
        format="json",
    )

    assert r.status_code == 201
    assert _total(producto) == 4
    en_deposito = Movimiento.objects.filter(posicion=deposito).aggregate(t=Sum("cantidad"))["t"]
    en_salon = Movimiento.objects.filter(posicion=salon).aggregate(t=Sum("cantidad"))["t"]
    assert (en_deposito, en_salon) == (1, 3)


def test_transferir_mas_de_lo_que_hay_en_origen_devuelve_400(
    cliente, usuario, producto, deposito, salon
):
    _entrada(producto, usuario, 2, estado="listo", posicion=deposito)

    r = cliente.post(
        "/api/movimientos/transferir/",
        {"producto": producto.pk, "cantidad": 5, "desde": deposito.pk, "hasta": salon.pk},
        format="json",
    )

    assert r.status_code == 400
    assert Movimiento.objects.filter(tipo="transferencia").count() == 0


def test_transferir_al_mismo_lugar_devuelve_400(cliente, usuario, producto, deposito):
    _entrada(producto, usuario, 5, estado="listo", posicion=deposito)

    r = cliente.post(
        "/api/movimientos/transferir/",
        {"producto": producto.pk, "cantidad": 1, "desde": deposito.pk, "hasta": deposito.pk},
        format="json",
    )

    assert r.status_code == 400


def test_transferir_desde_una_posicion_vacia_devuelve_400(cliente, producto, deposito, salon):
    r = cliente.post(
        "/api/movimientos/transferir/",
        {"producto": producto.pk, "cantidad": 1, "desde": deposito.pk, "hasta": salon.pk},
        format="json",
    )
    assert r.status_code == 400
    assert Movimiento.objects.count() == 0


# --- el invariante global --------------------------------------------------


def test_el_total_es_la_suma_aunque_haya_armados_y_transferencias(
    cliente, usuario, producto, deposito, salon
):
    _entrada(producto, usuario, 10)
    cliente.post("/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 4}, format="json")
    cliente.post(
        "/api/movimientos/transferir/",
        {"producto": producto.pk, "cantidad": 3, "desde": deposito.pk, "hasta": salon.pk},
        format="json",
    )

    assert _total(producto) == 10
    assert _total(producto, "en_caja") == 6
    assert _total(producto, "listo") == 4


def test_el_stock_expone_el_desglose_por_estado(cliente, usuario, producto):
    _entrada(producto, usuario, 7)
    cliente.post("/api/movimientos/armar/", {"producto": producto.pk, "cantidad": 3}, format="json")

    r = cliente.get("/api/stock/")

    fila = next(f for f in r.data if f["producto"] == producto.pk)
    assert fila["total"] == 7
    assert fila["en_caja"] == 4
    assert fila["listo"] == 3
