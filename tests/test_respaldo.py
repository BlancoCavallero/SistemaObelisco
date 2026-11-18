"""Nombre y poda de respaldos: las dos reglas que se pueden romper en silencio."""

import datetime as dt

from core.management.commands.respaldar import a_conservar, nombre_de_backup


def test_el_nombre_ordena_por_fecha_como_texto():
    antes = nombre_de_backup(dt.datetime(2026, 1, 5, tzinfo=dt.UTC))
    despues = nombre_de_backup(dt.datetime(2026, 1, 12, tzinfo=dt.UTC))

    assert antes < despues
    assert antes.startswith("obelisco-2026-01-05T")


def test_el_nombre_es_unico_por_segundo():
    momento = dt.datetime(2026, 3, 1, 12, 30, 45, tzinfo=dt.UTC)
    assert nombre_de_backup(momento) == "obelisco-2026-03-01T12-30-45Z.dump"


def test_no_borra_nada_si_hay_menos_que_el_limite():
    assert a_conservar(["a.dump", "b.dump"], 30) == []


def test_borra_los_mas_viejos():
    nombres = [f"obelisco-2026-01-{dia:02d}.dump" for dia in range(1, 11)]

    sobran = a_conservar(nombres, 3)

    assert len(sobran) == 7
    assert "obelisco-2026-01-10.dump" not in sobran
    assert "obelisco-2026-01-08.dump" not in sobran
    assert "obelisco-2026-01-01.dump" in sobran


def test_conservar_cero_borraria_todo_por_eso_el_comando_lo_rechaza():
    """La funcion es literal; la proteccion vive en el comando, no en la aritmetica."""
    assert a_conservar(["a.dump", "b.dump"], 0) == ["a.dump", "b.dump"]
