"""Deteccion de variables faltantes antes de desplegar."""

from core.management.commands.verificar_configuracion import (
    REQUERIDAS,
    variables_faltantes,
)

COMPLETO = {nombre: "valor" for nombre in REQUERIDAS}


def test_configuracion_completa_no_reporta_nada():
    assert variables_faltantes(COMPLETO) == []


def test_detecta_las_ausentes():
    entorno = dict(COMPLETO)
    entorno.pop("DATABASE_URL")
    entorno.pop("AWS_STORAGE_BUCKET_NAME")

    assert variables_faltantes(entorno) == ["DATABASE_URL", "AWS_STORAGE_BUCKET_NAME"]


def test_un_valor_vacio_cuenta_como_ausente():
    entorno = dict(COMPLETO)
    entorno["AWS_REGION"] = "   "

    assert variables_faltantes(entorno) == ["AWS_REGION"]


def test_entorno_vacio_reporta_todas():
    assert variables_faltantes({}) == list(REQUERIDAS)
