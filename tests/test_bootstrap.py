"""El arranque crea lo que falta y no toca lo que existe."""

import io
import os
from unittest import mock

import pytest
from django.core.management import call_command

from core.models import Rol, Usuario
from inventario.models import Almacen, Posicion

VARIABLES = {
    "DJANGO_SUPERUSER_USERNAME": "fede",
    "DJANGO_SUPERUSER_PASSWORD": "clave-inicial-larga",
}


def _bootstrap():
    call_command("bootstrap", stdout=io.StringIO())


@pytest.mark.django_db
def test_sin_variables_no_crea_nada():
    with mock.patch.dict(os.environ, {}, clear=False):
        for nombre in VARIABLES:
            os.environ.pop(nombre, None)
        _bootstrap()

    assert not Usuario.objects.exists()


@pytest.mark.django_db
def test_con_variables_crea_el_administrador():
    with mock.patch.dict(os.environ, VARIABLES, clear=False):
        _bootstrap()

    usuario = Usuario.objects.get(username="fede")
    assert usuario.is_superuser and usuario.is_staff
    assert usuario.rol == Rol.ADMIN
    assert usuario.check_password("clave-inicial-larga")


@pytest.mark.django_db
def test_no_cambia_la_contrasena_de_un_administrador_existente():
    with mock.patch.dict(os.environ, VARIABLES, clear=False):
        _bootstrap()

    with mock.patch.dict(
        os.environ, {**VARIABLES, "DJANGO_SUPERUSER_PASSWORD": "otra-distinta-123"}, clear=False
    ):
        _bootstrap()

    assert Usuario.objects.count() == 1
    assert Usuario.objects.get().check_password("clave-inicial-larga")


@pytest.mark.django_db
def test_no_crea_un_segundo_administrador_con_otro_nombre():
    Usuario.objects.create_superuser(username="previo", password="clave-previa-123")

    with mock.patch.dict(os.environ, VARIABLES, clear=False):
        _bootstrap()

    assert not Usuario.objects.filter(username="fede").exists()


@pytest.mark.django_db
def test_crea_las_ubicaciones_si_no_hay_ninguna():
    with mock.patch.dict(os.environ, VARIABLES, clear=False):
        _bootstrap()

    assert Almacen.objects.count() == 2
    assert Posicion.objects.count() == 25


@pytest.mark.django_db
def test_no_duplica_las_ubicaciones():
    with mock.patch.dict(os.environ, VARIABLES, clear=False):
        _bootstrap()
        _bootstrap()

    assert Posicion.objects.count() == 25
