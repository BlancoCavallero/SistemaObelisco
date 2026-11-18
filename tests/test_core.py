"""Versioned parameters and users that are deactivated, never deleted."""

import datetime as dt

from core.models import Parametro


def test_parametro_vigente_usa_la_ultima_fecha(db):
    Parametro.objects.create(
        clave="margen", valor={"porcentaje": 10}, vigente_desde=dt.date(2025, 1, 1)
    )
    Parametro.objects.create(
        clave="margen", valor={"porcentaje": 15}, vigente_desde=dt.date(2026, 1, 1)
    )

    assert Parametro.valor_vigente("margen", dt.date(2025, 6, 1)) == {"porcentaje": 10}
    assert Parametro.valor_vigente("margen", dt.date(2026, 6, 1)) == {"porcentaje": 15}
    assert Parametro.valor_vigente("inexistente", dt.date(2026, 6, 1)) is None


def test_usuario_se_desactiva_y_conserva_sus_movimientos(producto, usuario):
    from inventario.models import Movimiento, TipoMovimiento

    Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=2, tipo=TipoMovimiento.ENTRADA_COMPRA
    )
    usuario.is_active = False
    usuario.save()

    usuario.refresh_from_db()
    assert usuario.is_active is False
    assert usuario.movimientos.count() == 1
