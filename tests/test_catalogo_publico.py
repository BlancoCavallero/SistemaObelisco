"""Catalogo publico: se ve sin login, solo lo disponible, y nunca expone precios."""

import pytest
from rest_framework.test import APIClient

from catalogo.models import ImagenProducto
from inventario.models import Movimiento


@pytest.fixture
def cliente_publico():
    return APIClient()


def _entrada(producto, usuario, cantidad):
    Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=cantidad, tipo="entrada_compra"
    )


def test_catalogo_se_ve_sin_autenticacion(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 3)

    r = cliente_publico.get("/api/catalogo/")

    assert r.status_code == 200
    assert len(r.data["productos"]) == 1


def test_catalogo_solo_muestra_lo_que_tiene_stock(cliente_publico, usuario, producto, tipo):
    from catalogo.models import Producto

    sin_stock = Producto.objects.create(
        tipo=tipo, color="negro", alto_cm=80, ancho_cm=80, largo_cm=80
    )
    _entrada(producto, usuario, 2)

    r = cliente_publico.get("/api/catalogo/")

    ids = [p["id"] for p in r.data["productos"]]
    assert producto.pk in ids
    assert sin_stock.pk not in ids


def test_catalogo_no_muestra_productos_ocultos(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 5)
    producto.activo = False
    producto.save()

    r = cliente_publico.get("/api/catalogo/")

    assert r.data["productos"] == []


def test_catalogo_no_expone_precios(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 1)

    r = cliente_publico.get("/api/catalogo/")

    campos = set(r.data["productos"][0])
    assert not {"precio", "precio_venta", "costo", "margen"} & campos


def test_catalogo_expone_la_imagen_principal(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 1)
    ImagenProducto.objects.create(producto=producto, archivo="productos/probe.jpg", principal=True)

    r = cliente_publico.get("/api/catalogo/")

    assert r.data["productos"][0]["imagen"].endswith("productos/probe.jpg")


def test_catalogo_sin_imagen_devuelve_none(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 1)
    r = cliente_publico.get("/api/catalogo/")
    assert r.data["productos"][0]["imagen"] is None


def test_catalogo_expone_categorias_con_su_total(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 1)

    r = cliente_publico.get("/api/catalogo/")

    assert r.data["categorias"] == [{"nombre": "Muebles", "total": 1}]


def test_catalogo_filtra_por_categoria(cliente_publico, usuario, producto):
    _entrada(producto, usuario, 1)

    vacio = cliente_publico.get("/api/catalogo/", {"categoria": "Electrodomesticos"})
    lleno = cliente_publico.get("/api/catalogo/", {"categoria": "Muebles"})

    assert vacio.data["productos"] == []
    assert len(lleno.data["productos"]) == 1
