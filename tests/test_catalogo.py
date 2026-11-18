"""Catalog identity: the name is derived, so the same article cannot exist twice."""

import pytest
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, transaction

from catalogo.models import Producto


def test_nombre_producto_es_derivado(producto):
    assert producto.nombre == "Sillon 3 cuerpos - Gris - 85x90x180"
    with pytest.raises(FieldDoesNotExist):
        Producto._meta.get_field("nombre")


def test_nombre_incluye_modelo_solo_si_existe(tipo):
    sin_modelo = Producto.objects.create(
        tipo=tipo, color="negro", alto_cm=80, ancho_cm=90, largo_cm=190
    )
    con_modelo = Producto.objects.create(
        tipo=tipo, color="negro", alto_cm=80, ancho_cm=90, largo_cm=200, modelo="Nordico"
    )
    assert "Nordico" not in sin_modelo.nombre
    assert con_modelo.nombre.endswith("Nordico")


def test_no_se_puede_duplicar_el_mismo_producto(tipo):
    datos = dict(tipo=tipo, color="gris", alto_cm=85, ancho_cm=90, largo_cm=180)
    Producto.objects.create(**datos)
    with pytest.raises(IntegrityError), transaction.atomic():
        Producto.objects.create(**datos)


def test_id_visible_usa_prefijo_de_categoria(producto):
    assert producto.id_visible == f"MUE-{producto.pk:04d}"
