"""La configuracion de deploy tiene que decir lo mismo que la app.

El bug que motiva estos tests: el workflow pasaba DJANGO_SECRET_KEY y la app leia
SECRET_KEY, asi que produccion arrancaba con la clave de desarrollo y nadie se enteraba.
"""

import re
from pathlib import Path

import pytest
from django.core.checks import run_checks
from django.test import override_settings

WORKFLOW = Path(".github/workflows/release.yml")

# Variables de entorno que la aplicacion realmente lee.
LEIDAS_POR_LA_APP = {
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "DATABASE_URL",
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET",
    "APP_VERSION",
}


def test_el_workflow_solo_pasa_variables_que_la_app_lee():
    texto = WORKFLOW.read_text(encoding="utf-8")
    pasadas = set(re.findall(r"^\s+([A-Z0-9_]+)=\$\{\{ secrets\.", texto, re.MULTILINE))

    assert pasadas, "no se encontro ninguna variable en el workflow"
    assert pasadas <= LEIDAS_POR_LA_APP, (
        "el workflow pasa variables que la app no lee: " + str(sorted(pasadas - LEIDAS_POR_LA_APP))
    )


def test_la_app_no_arranca_con_la_clave_de_desarrollo_en_produccion():
    with override_settings(DEBUG=False, SECRET_KEY="dev-insecure-key-change-me"):
        errores = run_checks()

    assert any(error.id == "core.E001" for error in errores)


def test_en_desarrollo_la_clave_de_ejemplo_no_es_un_error():
    with override_settings(DEBUG=True, SECRET_KEY="dev-insecure-key-change-me"):
        errores = [error for error in run_checks() if error.id == "core.E001"]

    assert errores == []


@pytest.mark.parametrize("clave", ["otra-clave-larga-y-secreta", "x" * 64])
def test_una_clave_real_no_es_un_error(clave):
    with override_settings(DEBUG=False, SECRET_KEY=clave):
        errores = [error for error in run_checks() if error.id == "core.E001"]

    assert errores == []
