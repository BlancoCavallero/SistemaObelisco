"""Version bump rules. The release workflow depends on this being deterministic."""

import contextlib
import io

import pytest

from scripts.version import next_version, ultima_version


@pytest.mark.parametrize(
    ("actual", "mensajes", "esperado"),
    [
        # Sin tags previos: primer release.
        (None, ["feat: algo"], "0.1.0"),
        (None, ["fix: algo"], "0.1.0"),
        # Antes de 1.0.0: features suben minor, fixes suben patch.
        ("0.1.0", ["fix: corrige un total"], "0.1.1"),
        ("0.1.0", ["feat: agrega busqueda"], "0.2.0"),
        ("0.2.3", ["feat: agrega ventas", "fix: corrige stock"], "0.3.0"),
        # Antes de 1.0.0 un cambio incompatible NO salta a 1.0.0: sube minor.
        ("0.3.1", ["feat!: cambia el modelo"], "0.4.0"),
        # Desde 1.0.0 aplica semver completo.
        ("1.2.3", ["fix: corrige"], "1.2.4"),
        ("1.2.3", ["feat: agrega"], "1.3.0"),
        ("1.2.3", ["feat!: rompe"], "2.0.0"),
        # BREAKING CHANGE en el cuerpo tambien cuenta.
        ("1.2.3", ["chore: limpia\n\nBREAKING CHANGE: cambia el contrato"], "2.0.0"),
        # Commits que no son feat ni fix producen patch: el release siempre avanza.
        ("0.1.0", ["docs: actualiza readme"], "0.1.1"),
        ("1.0.0", ["test: agrega casos"], "1.0.1"),
        # Los merges y los mensajes raros no rompen el calculo.
        ("1.0.0", ["Merge branch 'develop'", "wip"], "1.0.1"),
    ],
)
def test_next_version(actual, mensajes, esperado):
    assert next_version(actual, mensajes) == esperado


def test_ultima_version_ignora_tags_que_no_son_semver():
    assert ultima_version(["v1.2.3", "v1.3.0", "nightly", "v2.0.0-rc1"]) == "1.3.0"


def test_ultima_version_sin_tags_devuelve_none():
    assert ultima_version(["nightly", "latest"]) is None


def test_si_el_commit_ya_tiene_tag_no_sube_la_version():
    """Re-ejecutar el release no puede inventar un tag nuevo."""
    from scripts.version import main

    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        main(["--last-tag", "v0.2.0", "--head-already-tagged"])

    assert salida.getvalue().strip() == "0.2.0"


def test_sin_el_flag_el_mismo_caso_sube_patch():
    from scripts.version import main

    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        main(["--last-tag", "v0.2.0"])

    assert salida.getvalue().strip() == "0.2.1"
