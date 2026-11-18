"""La cuenta corriente expuesta: saldo, deuda vencida y pagos."""

import datetime as dt
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from inventario.models import Movimiento
from ventas.models import Cliente, CuentaMovimiento, MedioPago, Venta
from ventas.services import confirmar_venta


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def con_cuenta(db):
    return Cliente.objects.create(nombre="Ana", ciudad="Quenuma", habilitado_cuenta_corriente=True)


@pytest.fixture
def con_deuda(usuario, producto, con_cuenta):
    from ventas.models import LineaVenta

    Movimiento.objects.create(producto=producto, usuario=usuario, cantidad=5, tipo="entrada_compra")
    venta = Venta.objects.create(
        usuario=usuario, medio_pago=MedioPago.CUENTA_CORRIENTE, cliente=con_cuenta
    )
    LineaVenta.objects.create(
        venta=venta, producto=producto, cantidad=1, precio_unitario=Decimal("30000")
    )
    confirmar_venta(venta)
    return con_cuenta


def test_la_cuenta_expone_saldo_y_movimientos(cliente, con_deuda):
    respuesta = cliente.get(f"/api/clientes/{con_deuda.pk}/cuenta/")

    assert respuesta.status_code == 200
    assert respuesta.data["saldo"] == "30000.00"
    assert len(respuesta.data["movimientos"]) == 3
    assert respuesta.data["vencido"] == "0.00"


def test_registrar_un_pago_por_api(cliente, usuario, con_deuda):
    respuesta = cliente.post(
        f"/api/clientes/{con_deuda.pk}/cuenta/pagos/",
        {"monto": "10000"},
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["saldo"] == "20000.00"
    assert CuentaMovimiento.objects.filter(tipo="pago").count() == 1


def test_un_pago_invalido_devuelve_400(cliente, con_deuda):
    respuesta = cliente.post(
        f"/api/clientes/{con_deuda.pk}/cuenta/pagos/", {"monto": "0"}, format="json"
    )
    assert respuesta.status_code == 400


def test_el_vencido_se_informa(cliente, con_deuda):
    CuentaMovimiento.objects.filter(cliente=con_deuda, vencimiento=timezone.localdate()).update(
        vencimiento=timezone.localdate() - dt.timedelta(days=3)
    )

    respuesta = cliente.get(f"/api/clientes/{con_deuda.pk}/cuenta/")

    assert respuesta.data["vencido"] == "10000.00"


def test_la_lista_de_morosos(cliente, usuario, con_deuda, producto):
    otro = Cliente.objects.create(nombre="Beto", ciudad="Casbas", habilitado_cuenta_corriente=True)
    CuentaMovimiento.objects.create(
        cliente=otro,
        tipo="cargo",
        monto=Decimal("5000"),
        vencimiento=timezone.localdate() - dt.timedelta(days=30),
        usuario=usuario,
    )
    CuentaMovimiento.objects.filter(cliente=con_deuda).update(
        vencimiento=timezone.localdate() + dt.timedelta(days=30)
    )

    respuesta = cliente.get("/api/clientes/morosos/")

    assert respuesta.status_code == 200
    assert [f["cliente"]["nombre"] for f in respuesta.data] == ["Beto"]
    assert respuesta.data[0]["vencido"] == "5000.00"


def test_la_cuenta_requiere_sesion(con_deuda):
    assert APIClient().get(f"/api/clientes/{con_deuda.pk}/cuenta/").status_code in (401, 403)
