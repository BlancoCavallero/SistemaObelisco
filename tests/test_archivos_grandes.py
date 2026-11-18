"""La guardia que impide repetir el PDF de 102 MB en la historia."""

from scripts.archivos_grandes import grandes

MB = 1024 * 1024


def test_archivo_justo_en_el_limite_no_falla():
    assert grandes([("ok.bin", 5 * MB)]) == []


def test_archivo_por_encima_del_limite_falla():
    assert grandes([("grande.pdf", 5 * MB + 1)]) == [("grande.pdf", 5 * MB + 1)]


def test_devuelve_todos_los_que_exceden():
    entradas = [("chico.txt", 10), ("a.pdf", 100 * MB), ("b.pdf", 6 * MB)]
    assert [ruta for ruta, _ in grandes(entradas)] == ["a.pdf", "b.pdf"]


def test_limite_configurable():
    assert grandes([("x.bin", 2 * MB)], limite_mb=1) == [("x.bin", 2 * MB)]
