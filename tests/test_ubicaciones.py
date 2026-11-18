"""Almacenes, sectores y posiciones: sin ellos la transferencia existe pero no se puede usar."""

import io

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from inventario.models import Almacen, Posicion, Sector


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def test_crear_almacen(cliente):
    respuesta = cliente.post(
        "/api/almacenes/", {"codigo": "ALM-01", "nombre": "Local Tres Lomas"}, format="json"
    )
    assert respuesta.status_code == 201
    assert Almacen.objects.get().codigo == "ALM-01"


def test_crear_sector_dentro_de_un_almacen(cliente):
    almacen = Almacen.objects.create(codigo="ALM-01", nombre="Local")

    respuesta = cliente.post(
        "/api/sectores/", {"almacen": almacen.pk, "codigo": "SEC-01"}, format="json"
    )

    assert respuesta.status_code == 201
    assert Sector.objects.get().almacen == almacen


def test_el_codigo_de_sector_se_repite_entre_almacenes(cliente):
    uno = Almacen.objects.create(codigo="ALM-01", nombre="Local")
    dos = Almacen.objects.create(codigo="ALM-02", nombre="Exhibicion")

    cliente.post("/api/sectores/", {"almacen": uno.pk, "codigo": "SEC-01"}, format="json")
    respuesta = cliente.post(
        "/api/sectores/", {"almacen": dos.pk, "codigo": "SEC-01"}, format="json"
    )

    assert respuesta.status_code == 201
    assert Sector.objects.filter(codigo="SEC-01").count() == 2


def test_el_mismo_sector_no_se_repite_en_el_mismo_almacen(cliente):
    almacen = Almacen.objects.create(codigo="ALM-01", nombre="Local")

    cliente.post("/api/sectores/", {"almacen": almacen.pk, "codigo": "SEC-01"}, format="json")
    respuesta = cliente.post(
        "/api/sectores/", {"almacen": almacen.pk, "codigo": "SEC-01"}, format="json"
    )

    assert respuesta.status_code == 400


def test_crear_posicion(cliente):
    sector = Sector.objects.create(
        almacen=Almacen.objects.create(codigo="ALM-01", nombre="Local"), codigo="SEC-01"
    )

    respuesta = cliente.post(
        "/api/posiciones/", {"sector": sector.pk, "codigo": "POS-01"}, format="json"
    )

    assert respuesta.status_code == 201
    assert Posicion.objects.get().codigo == "POS-01"


def test_listar_posiciones_filtradas_por_almacen(cliente):
    uno = Almacen.objects.create(codigo="ALM-01", nombre="Local")
    dos = Almacen.objects.create(codigo="ALM-02", nombre="Exhibicion")
    for almacen in (uno, dos):
        sector = Sector.objects.create(almacen=almacen, codigo="SEC-01")
        Posicion.objects.create(sector=sector, codigo="POS-01")

    respuesta = cliente.get("/api/posiciones/", {"almacen": uno.pk})

    assert len(respuesta.data) == 1
    assert respuesta.data[0]["almacen"] == uno.pk


def test_las_ubicaciones_requieren_sesion():
    assert APIClient().get("/api/almacenes/").status_code in (401, 403)


def test_el_comando_crea_el_esquema_inicial(db):
    salida = io.StringIO()

    call_command("crear_ubicaciones", stdout=salida)

    assert Almacen.objects.count() == 2
    assert Sector.objects.count() == 5
    assert Posicion.objects.count() == 25
    assert "ALM-01" in salida.getvalue()


def test_el_comando_es_idempotente(db):
    call_command("crear_ubicaciones", stdout=io.StringIO())
    call_command("crear_ubicaciones", stdout=io.StringIO())

    assert Almacen.objects.count() == 2
    assert Posicion.objects.count() == 25
