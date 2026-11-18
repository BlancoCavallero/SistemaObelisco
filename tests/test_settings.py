"""El parseo de listas desde variables de entorno.

Un ALLOWED_HOSTS vacio no puede dejar la app rechazando todo: ese es el fallo de deploy
mas silencioso que existe, porque la app arranca y responde 400 a todo.
"""

from config.settings import parse_lista


def test_lista_separa_y_limpia():
    assert parse_lista(" a, b ,,c ") == ["a", "b", "c"]


def test_vacio_usa_el_default():
    assert parse_lista("", default=["*"]) == ["*"]
    assert parse_lista(None, default=["*"]) == ["*"]


def test_vacio_sin_default_es_lista_vacia():
    assert parse_lista("") == []
    assert parse_lista(None) == []


def test_solo_comas_usa_el_default():
    assert parse_lista(" , , ", default=["*"]) == ["*"]


def test_el_default_no_se_muta():
    default = ["*"]
    resultado = parse_lista("", default=default)
    resultado.append("otro")
    assert default == ["*"]
