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
BACKUP = Path(".github/workflows/backup.yml")

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
    "AWS_ENDPOINT_URL_S3",
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "APP_VERSION",
    "DJANGO_SUPERUSER_USERNAME",
    "DJANGO_SUPERUSER_PASSWORD",
    "DJANGO_SUPERUSER_EMAIL",
}

# Variables que usa el pipeline, no la aplicacion (pg_dump necesita la conexion directa).
SOLO_CI = {
    "DATABASE_URL_DIRECT",
    "GITHUB_TOKEN",
    "GCP_SERVICE_ACCOUNT",
    "GCP_WORKLOAD_IDENTITY_PROVIDER",
    "GH_TOKEN",  # lo usa gh dentro del job, no la app
    "WIF",  # alias interno del paso de validacion de Google Cloud
    "SA",  # alias de GCP_SERVICE_ACCOUNT dentro del paso de validacion
}


@pytest.mark.parametrize("workflow", [WORKFLOW, BACKUP])
def test_los_workflows_solo_pasan_variables_que_la_app_lee(workflow):
    texto = workflow.read_text(encoding="utf-8")
    # Dos formatos: linea de bloque `K=V` (release) y mapa YAML `K: V` (backup).
    pasadas = set(
        re.findall(r"^\s+([A-Z0-9_]+)\s*[=:]\s*\$\{\{\s*secrets\.", texto, re.MULTILINE)
    )

    assert pasadas, f"no se encontro ninguna variable en {workflow}"
    desconocidas = pasadas - (LEIDAS_POR_LA_APP | SOLO_CI)
    assert not desconocidas, (
        f"{workflow} pasa variables que nadie lee: " + str(sorted(desconocidas))
    )


def test_el_backup_puede_usar_un_s3_generico_y_no_solo_r2():
    texto = BACKUP.read_text(encoding="utf-8")

    assert "AWS_ENDPOINT_URL_S3" in texto
    assert "AWS_STORAGE_BUCKET_NAME" in texto
    assert "DATABASE_URL_DIRECT" in texto


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
