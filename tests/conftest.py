"""Shared fixtures."""

import pytest

from catalogo.models import Categoria, Producto, TipoProducto
from core.models import Usuario


@pytest.fixture(autouse=True)
def sin_tls(settings):
    """Tests run over plain HTTP; production keeps the redirects on."""
    settings.SECURE_SSL_REDIRECT = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False


@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(username="diego", password="clave-segura-1")


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="Muebles")


@pytest.fixture
def tipo(categoria):
    return TipoProducto.objects.create(categoria=categoria, nombre="Sillon 3 cuerpos")


@pytest.fixture
def producto(tipo):
    return Producto.objects.create(tipo=tipo, color="gris", alto_cm=85, ancho_cm=90, largo_cm=180)
