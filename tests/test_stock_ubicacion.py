"""Cuanto hay en cada lugar.

El ledger no exige ubicacion (A15), asi que una parte del stock puede no tenerla. Ese
stock existe y hay que mostrarlo como "sin ubicar", no esconderlo: si se oculta, los
totales por local no cierran contra el total del producto.
"""

import pytest
from rest_framework.test import APIClient

from inventario.models import Almacen, Movimiento, Posicion, Sector


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def locales(db):
    uno = Almacen.objects.create(codigo="ALM-01", nombre="Local Tres Lomas")
    dos = Almacen.objects.create(codigo="ALM-02", nombre="Exhibicion")
    deposito = Posicion.objects.create(
        sector=Sector.objects.create(almacen=uno, codigo="SEC-01"), codigo="POS-01"
    )
    salon = Posicion.objects.create(
        sector=Sector.objects.create(almacen=dos, codigo="SEC-01"), codigo="POS-01"
    )
    return {"uno": uno, "dos": dos, "deposito": deposito, "salon": salon}


def _mov(producto, usuario, cantidad, posicion=None, estado="listo"):
    return Movimiento.objects.create(
        producto=producto,
        usuario=usuario,
        cantidad=cantidad,
        tipo="entrada_compra",
        posicion=posicion,
        estado=estado,
    )


def test_agrupa_por_ubicacion_y_estado(cliente, usuario, producto, locales):
    _mov(producto, usuario, 5, locales["deposito"], estado="en_caja")
    _mov(producto, usuario, 2, locales["salon"], estado="listo")

    respuesta = cliente.get("/api/stock/ubicaciones/")

    assert respuesta.status_code == 200
    etiquetas = {f["etiqueta"]: f["cantidad"] for f in respuesta.data["filas"]}
    assert etiquetas["ALM-01/SEC-01/POS-01"] == 5
    assert etiquetas["ALM-02/SEC-01/POS-01"] == 2


def test_el_stock_sin_ubicacion_se_muestra_aparte(cliente, usuario, producto, locales):
    _mov(producto, usuario, 3, locales["deposito"])
    _mov(producto, usuario, 4, None)

    respuesta = cliente.get("/api/stock/ubicaciones/")

    etiquetas = {f["etiqueta"]: f["cantidad"] for f in respuesta.data["filas"]}
    assert etiquetas["sin ubicar"] == 4


def test_las_filas_suman_el_total_del_producto(cliente, usuario, producto, locales):
    _mov(producto, usuario, 5, locales["deposito"])
    _mov(producto, usuario, 2, locales["salon"])
    _mov(producto, usuario, 4, None)

    respuesta = cliente.get("/api/stock/ubicaciones/")

    suma = sum(f["cantidad"] for f in respuesta.data["filas"] if f["producto"] == producto.pk)
    assert suma == 11


def test_filtra_por_almacen(cliente, usuario, producto, locales):
    _mov(producto, usuario, 5, locales["deposito"])
    _mov(producto, usuario, 2, locales["salon"])

    respuesta = cliente.get("/api/stock/ubicaciones/", {"almacen": locales["dos"].pk})

    assert [f["cantidad"] for f in respuesta.data["filas"]] == [2]


def test_resume_el_total_por_almacen(cliente, usuario, producto, locales):
    _mov(producto, usuario, 5, locales["deposito"])
    _mov(producto, usuario, 2, locales["salon"])
    _mov(producto, usuario, 4, None)

    respuesta = cliente.get("/api/stock/ubicaciones/")

    resumen = {a["codigo"]: a["total"] for a in respuesta.data["almacenes"]}
    assert resumen["ALM-01"] == 5
    assert resumen["ALM-02"] == 2
    assert resumen["sin ubicar"] == 4


def test_no_incluye_filas_en_cero(cliente, usuario, producto, locales):
    _mov(producto, usuario, 3, locales["deposito"])
    _mov(producto, usuario, -3, locales["deposito"])

    respuesta = cliente.get("/api/stock/ubicaciones/")

    assert respuesta.data["filas"] == []


def test_requiere_sesion():
    assert APIClient().get("/api/stock/ubicaciones/").status_code in (401, 403)
