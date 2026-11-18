"""El front se sirve desde Django: mismo origen, sin CORS, un solo despliegue."""

import pytest


@pytest.fixture
def con_build(tmp_path, settings):
    (tmp_path / "index.html").write_text(
        '<!doctype html><div id="raiz"></div>', encoding="utf-8"
    )
    settings.FRONTEND_DIST = tmp_path
    return tmp_path


def test_sirve_el_index(client, con_build):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert b'id="raiz"' in respuesta.content


def test_las_rutas_del_spa_devuelven_el_mismo_shell(client, con_build):
    for ruta in ["/catalogo", "/catalogo/muebles/", "/recepcion"]:
        respuesta = client.get(ruta)
        assert respuesta.status_code == 200, ruta
        assert b'id="raiz"' in respuesta.content


def test_sin_build_explica_como_construirlo(client, settings, tmp_path):
    settings.FRONTEND_DIST = tmp_path / "no-existe"

    respuesta = client.get("/")

    assert respuesta.status_code == 503
    assert b"npm run build" in respuesta.content


def test_la_api_no_cae_en_el_spa(client, con_build):
    respuesta = client.get("/api/stock/")
    assert respuesta.status_code in (401, 403)


def test_health_sigue_siendo_json(client, con_build):
    respuesta = client.get("/health/")
    assert respuesta.json()["status"] == "ok"
