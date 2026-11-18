"""Sesion del personal: entra, se identifica y sale."""

import pytest
from rest_framework.test import APIClient

from core.models import Usuario


@pytest.fixture
def cliente():
    return APIClient()


def test_login_valido_devuelve_el_perfil(cliente, usuario):
    respuesta = cliente.post(
        "/api/auth/login/", {"username": "diego", "password": "clave-segura-1"}, format="json"
    )

    assert respuesta.status_code == 200
    assert respuesta.data["username"] == "diego"
    assert respuesta.data["rol"] == "operador"


def test_login_invalido_no_revela_cual_de_los_dos_fallo(cliente, usuario):
    respuesta = cliente.post(
        "/api/auth/login/", {"username": "diego", "password": "mal"}, format="json"
    )

    assert respuesta.status_code == 400
    assert respuesta.data["detail"] == "Usuario o contrasena incorrectos."


def test_login_sin_datos_devuelve_400(cliente):
    assert cliente.post("/api/auth/login/", {}, format="json").status_code == 400


def test_usuario_desactivado_no_entra_y_no_se_puede_enumerar_usuarios(cliente, usuario):
    """Un usuario dado de baja no entra, pero la respuesta no delata que existe."""
    usuario.is_active = False
    usuario.save()

    respuesta = cliente.post(
        "/api/auth/login/", {"username": "diego", "password": "clave-segura-1"}, format="json"
    )

    assert respuesta.status_code == 400
    assert respuesta.data["detail"] == "Usuario o contrasena incorrectos."
    assert cliente.get("/api/auth/me/").status_code in (401, 403)


def test_me_sin_sesion_devuelve_403(cliente):
    assert cliente.get("/api/auth/me/").status_code in (401, 403)


def test_me_con_sesion_devuelve_el_perfil(cliente, usuario):
    cliente.force_authenticate(user=usuario)

    respuesta = cliente.get("/api/auth/me/")

    assert respuesta.status_code == 200
    assert respuesta.data["username"] == "diego"


def test_logout_cierra_la_sesion(cliente, usuario):
    cliente.force_authenticate(user=usuario)

    assert cliente.post("/api/auth/logout/").status_code == 204


def test_la_sesion_sobrevive_en_el_cliente(cliente, usuario):
    cliente.post(
        "/api/auth/login/", {"username": "diego", "password": "clave-segura-1"}, format="json"
    )

    assert cliente.get("/api/auth/me/").status_code == 200


def test_usuario_nuevo_es_operador_por_defecto(usuario):
    assert usuario.rol == Usuario._meta.get_field("rol").default
