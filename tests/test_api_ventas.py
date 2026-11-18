"""La venta por API: el precio lo pone el servidor, nunca el cliente."""

import datetime as dt
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from catalogo.models import PrecioLista
from inventario.models import Movimiento
from ventas.models import Cliente, Venta


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def con_stock_y_precio(producto, usuario):
    PrecioLista.objects.create(
        producto=producto, valor=Decimal("10000"), vigente_desde=dt.date(2026, 1, 1)
    )
    Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=10, tipo="entrada_compra"
    )
    return producto


def test_venta_anonima_en_efectivo(cliente, con_stock_y_precio):
    respuesta = cliente.post(
        "/api/ventas/",
        {
            "medio_pago": "efectivo",
            "lineas": [{"producto": con_stock_y_precio.pk, "cantidad": 2}],
        },
        format="json",
    )

    assert respuesta.status_code == 201
    # 10000 de costo + 10% de margen = 11000 el unitario, por 2 unidades.
    assert respuesta.data["total"] == "22000.00"
    assert respuesta.data["detalle"][0]["precio_unitario"] == "11000.00"
    assert respuesta.data["cliente"] is None
    assert Movimiento.objects.get(tipo="venta").cantidad == -2


def test_efectivo_con_parametro_descuenta_sobre_el_precio_de_venta(cliente, con_stock_y_precio):
    from core.models import Parametro

    Parametro.objects.create(
        clave="descuento_efectivo", valor={"porcentaje": 0.05}, vigente_desde=dt.date(2026, 1, 1)
    )

    respuesta = cliente.post(
        "/api/ventas/",
        {"medio_pago": "efectivo", "lineas": [{"producto": con_stock_y_precio.pk, "cantidad": 2}]},
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["total"] == "20900.00"


def test_el_cliente_no_puede_imponer_el_precio(cliente, con_stock_y_precio):
    respuesta = cliente.post(
        "/api/ventas/",
        {
            "medio_pago": "transferencia",
            "lineas": [
                {"producto": con_stock_y_precio.pk, "cantidad": 1, "precio_unitario": "1.00"}
            ],
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["total"] == "11000.00"


def test_producto_sin_precio_de_lista_devuelve_400(cliente, producto, usuario):
    Movimiento.objects.create(producto=producto, usuario=usuario, cantidad=5, tipo="entrada_compra")

    respuesta = cliente.post(
        "/api/ventas/",
        {"medio_pago": "efectivo", "lineas": [{"producto": producto.pk, "cantidad": 1}]},
        format="json",
    )

    assert respuesta.status_code == 400
    assert "precio" in str(respuesta.data).lower()
    assert not Venta.objects.exists()


def test_stock_insuficiente_devuelve_400_y_no_confirma(cliente, con_stock_y_precio):
    respuesta = cliente.post(
        "/api/ventas/",
        {"medio_pago": "efectivo", "lineas": [{"producto": con_stock_y_precio.pk, "cantidad": 99}]},
        format="json",
    )

    assert respuesta.status_code == 400
    assert not Movimiento.objects.filter(tipo="venta").exists()


def test_venta_vacia_devuelve_400(cliente):
    respuesta = cliente.post(
        "/api/ventas/", {"medio_pago": "efectivo", "lineas": []}, format="json"
    )
    assert respuesta.status_code == 400


def test_cuenta_corriente_exige_cliente_habilitado(cliente, con_stock_y_precio):
    inhabilitado = Cliente.objects.create(nombre="Ana", ciudad="Tres Lomas")

    respuesta = cliente.post(
        "/api/ventas/",
        {
            "medio_pago": "cuenta_corriente",
            "cliente": inhabilitado.pk,
            "lineas": [{"producto": con_stock_y_precio.pk, "cantidad": 1}],
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert "habilitad" in str(respuesta.data).lower()


def test_cuenta_corriente_con_cliente_habilitado(cliente, con_stock_y_precio):
    habilitado = Cliente.objects.create(
        nombre="Ana", ciudad="Quenuma", habilitado_cuenta_corriente=True
    )

    respuesta = cliente.post(
        "/api/ventas/",
        {
            "medio_pago": "cuenta_corriente",
            "cliente": habilitado.pk,
            "lineas": [{"producto": con_stock_y_precio.pk, "cantidad": 1}],
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["cliente"] == habilitado.pk


def test_la_venta_requiere_sesion(con_stock_y_precio):
    respuesta = APIClient().post(
        "/api/ventas/",
        {"medio_pago": "efectivo", "lineas": [{"producto": con_stock_y_precio.pk, "cantidad": 1}]},
        format="json",
    )
    assert respuesta.status_code in (401, 403)


def test_el_staff_ve_el_precio_del_producto(cliente, con_stock_y_precio):
    respuesta = cliente.get("/api/productos/buscar/")
    assert respuesta.data[0]["precio_venta"] == "11000.00"


def test_crear_y_listar_clientes(cliente):
    alta = cliente.post(
        "/api/clientes/",
        {"nombre": "Ana", "ciudad": "Quenuma", "habilitado_cuenta_corriente": True},
        format="json",
    )
    assert alta.status_code == 201

    listado = cliente.get("/api/clientes/")
    assert [c["nombre"] for c in listado.data] == ["Ana"]
