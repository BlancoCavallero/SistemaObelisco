"""Padron de proveedores: como se compra hoy, sin ordenes de compra.

S57: 40 a 50 proveedores, la mayoria por WhatsApp o telefono, algunos por mail, algunos
por viajante y unos pocos por portal. No hay ordenes de compra formales, asi que lo que
hace falta es el padron y el canal, no un circuito de aprobacion.
"""

import pytest
from rest_framework.test import APIClient

from inventario.models import Movimiento
from proveedores.models import CanalContacto, Proveedor


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def test_crear_un_proveedor_con_su_canal(cliente):
    respuesta = cliente.post(
        "/api/proveedores/",
        {
            "nombre": "Muebles La Fabrica",
            "canal": "whatsapp",
            "contacto": "Ruben",
            "telefono": "2392-555555",
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert Proveedor.objects.get().canal == CanalContacto.WHATSAPP


def test_un_canal_inventado_devuelve_400(cliente):
    respuesta = cliente.post(
        "/api/proveedores/", {"nombre": "X", "canal": "paloma-mensajera"}, format="json"
    )
    assert respuesta.status_code == 400


def test_el_canal_por_defecto_es_whatsapp(cliente):
    respuesta = cliente.post("/api/proveedores/", {"nombre": "Sin canal"}, format="json")

    assert respuesta.status_code == 201
    assert respuesta.data["canal"] == CanalContacto.WHATSAPP


def test_lista_solo_los_activos(cliente):
    Proveedor.objects.create(nombre="Activo")
    Proveedor.objects.create(nombre="Inactivo", activo=False)

    respuesta = cliente.get("/api/proveedores/")

    assert [p["nombre"] for p in respuesta.data] == ["Activo"]


def test_desactivar_un_proveedor_no_lo_borra(cliente):
    proveedor = Proveedor.objects.create(nombre="Viejo")

    cliente.patch(f"/api/proveedores/{proveedor.pk}/", {"activo": False}, format="json")

    proveedor.refresh_from_db()
    assert proveedor.activo is False
    assert Proveedor.objects.count() == 1


def test_los_proveedores_requieren_sesion():
    assert APIClient().get("/api/proveedores/").status_code in (401, 403)


def test_una_entrada_puede_registrar_de_que_proveedor_vino(cliente, usuario, producto):
    proveedor = Proveedor.objects.create(nombre="La Fabrica")

    respuesta = cliente.post(
        "/api/movimientos/",
        {
            "producto": producto.pk,
            "cantidad": 5,
            "tipo": "entrada_compra",
            "proveedor": proveedor.pk,
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert Movimiento.objects.get().proveedor == proveedor


def test_una_entrada_sin_proveedor_sigue_siendo_valida(cliente, producto):
    respuesta = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 1, "tipo": "entrada_inventario_inicial"},
        format="json",
    )
    assert respuesta.status_code == 201
    assert Movimiento.objects.get().proveedor is None
