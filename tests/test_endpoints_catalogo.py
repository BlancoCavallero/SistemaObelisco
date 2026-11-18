"""Endpoints que necesita la pantalla de recepcion: categorias y tipos para los selects."""

import pytest
from rest_framework.test import APIClient

from catalogo.models import Categoria, TipoProducto


@pytest.fixture
def cliente(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


def test_categorias_requiere_sesion():
    assert APIClient().get("/api/categorias/").status_code in (401, 403)


def test_lista_categorias_activas(cliente, categoria):
    Categoria.objects.create(nombre="Oculta", activo=False)

    respuesta = cliente.get("/api/categorias/")

    assert respuesta.status_code == 200
    assert [c["nombre"] for c in respuesta.data] == ["Muebles"]


def test_tipos_filtrados_por_categoria(cliente, categoria, tipo):
    otra = Categoria.objects.create(nombre="Electrodomesticos")
    TipoProducto.objects.create(categoria=otra, nombre="Heladera")

    respuesta = cliente.get("/api/tipos/", {"categoria": categoria.pk})

    assert respuesta.status_code == 200
    assert [t["nombre"] for t in respuesta.data] == ["Sillon 3 cuerpos"]


def test_tipos_sin_categoria_devuelve_todos(cliente, tipo):
    respuesta = cliente.get("/api/tipos/")
    assert len(respuesta.data) == 1


def test_colores_expone_las_opciones_validas(cliente):
    respuesta = cliente.get("/api/colores/")

    assert respuesta.status_code == 200
    valores = [c["valor"] for c in respuesta.data]
    assert "gris" in valores
    assert "fucsia" not in valores


def test_crear_categoria_desde_la_api(cliente):
    respuesta = cliente.post("/api/categorias/", {"nombre": "Blanqueria"}, format="json")

    assert respuesta.status_code == 201
    assert Categoria.objects.filter(nombre="Blanqueria").exists()


def test_crear_categoria_duplicada_devuelve_400(cliente, categoria):
    respuesta = cliente.post("/api/categorias/", {"nombre": "Muebles"}, format="json")
    assert respuesta.status_code == 400


def test_crear_tipo_en_una_categoria(cliente, categoria):
    respuesta = cliente.post(
        "/api/tipos/", {"categoria": categoria.pk, "nombre": "Mesa ratona"}, format="json"
    )
    assert respuesta.status_code == 201
