"""Contar: la unica forma de que el numero del sistema sea el real.

El conteo no es una campana ni una pantalla que se cierra (D-07): es una sesion en la que
alguien compara lo que hay contra lo que el sistema dice y registra la diferencia. Si el
numero coincide no se escribe nada; si no coincide, se escribe UN movimiento de ajuste con
su motivo, su autor y el estado que se conto. Nunca se edita el saldo: A28 pide auditar
despues.

Dos reglas sostienen que el ajuste no invente datos:

- El cliente manda el `esperado` que tenia en pantalla. Si entre que miro y apreto el boton
  entro o salio mercaderia, el server se niega (409) en lugar de convertir esa carrera en un
  ajuste fantasma.
- El ajuste va al estado que se conto. Si el stock esta repartido entre caja y armado, el
  server no adivina: pide que se elija. Adivinar deja `listo` en negativo y `en_caja`
  intacto, y despues armar deja pasar cajas que no existen.
"""

import pytest
from rest_framework.test import APIClient

from catalogo.models import Producto
from inventario.models import Movimiento


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def _mov(producto, usuario, cantidad, tipo="entrada_compra", estado="listo", posicion=None):
    return Movimiento.objects.create(
        producto=producto,
        usuario=usuario,
        cantidad=cantidad,
        tipo=tipo,
        estado=estado,
        posicion=posicion,
    )


def _contar(cliente, producto, contado, esperado, **extra):
    return cliente.post(
        "/api/conteo/",
        {"producto": producto.pk, "contado": contado, "esperado": esperado, **extra},
        format="json",
    )


# --- la hoja de conteo -------------------------------------------------------


def test_la_hoja_muestra_lo_que_el_sistema_dice_que_hay(cliente, usuario, producto):
    _mov(producto, usuario, 5)

    respuesta = cliente.get("/api/conteo/")

    assert respuesta.status_code == 200
    fila = next(f for f in respuesta.data["filas"] if f["producto"] == producto.pk)
    assert fila["esperado"] == 5
    assert fila["nombre"] == producto.nombre
    assert fila["id_visible"] == producto.id_visible


def test_la_hoja_incluye_articulos_sin_movimientos(cliente, usuario, producto):
    """Un articulo que esta en el catalogo pero nunca entro se cuenta igual.

    Si la hoja solo trae lo que ya tiene movimientos, el que encuentra dos sillones de un
    articulo sin historial no tiene donde anotarlo, y esos dos no existen para el sistema.
    """
    respuesta = cliente.get("/api/conteo/")

    filas = {f["producto"]: f["esperado"] for f in respuesta.data["filas"]}
    assert filas[producto.pk] == 0


def test_la_hoja_excluye_articulos_dados_de_baja(cliente, usuario, producto):
    Producto.objects.create(
        tipo=producto.tipo,
        color="negro",
        alto_cm=10,
        ancho_cm=10,
        largo_cm=10,
        activo=False,
    )

    respuesta = cliente.get("/api/conteo/")

    assert [f["producto"] for f in respuesta.data["filas"]] == [producto.pk]


def test_la_hoja_suma_todos_los_estados_y_ubicaciones(cliente, usuario, producto):
    """Contar es contar unidades, no cajas ni posiciones (A15)."""
    _mov(producto, usuario, 2, estado="en_caja")
    _mov(producto, usuario, 3, estado="listo")

    fila = next(
        f for f in cliente.get("/api/conteo/").data["filas"] if f["producto"] == producto.pk
    )

    assert fila["esperado"] == 5
    assert fila["en_caja"] == 2
    assert fila["listo"] == 3


def test_la_busqueda_acepta_varias_palabras(cliente, usuario, producto):
    """El que cuenta tipea 'sillon gris', no filtros exactos."""
    respuesta = cliente.get("/api/conteo/", {"q": "sillon gris"})

    assert [f["producto"] for f in respuesta.data["filas"]] == [producto.pk]


def test_la_busqueda_acepta_el_id_visible(cliente, usuario, producto):
    """El articulo tiene una etiqueta pegada: tipear esa etiqueta lo tiene que encontrar."""
    respuesta = cliente.get("/api/conteo/", {"q": producto.id_visible})

    assert [f["producto"] for f in respuesta.data["filas"]] == [producto.pk]


# --- registrar el conteo -----------------------------------------------------


def test_contar_de_menos_registra_un_ajuste_negativo(cliente, usuario, producto):
    _mov(producto, usuario, 5)

    respuesta = _contar(cliente, producto, 3, 5, motivo="Se rompieron dos")

    assert respuesta.status_code == 201
    assert respuesta.data["esperado"] == 5
    assert respuesta.data["contado"] == 3
    assert respuesta.data["ajuste"] == -2
    assert respuesta.data["estado"] == "listo"
    ajuste = Movimiento.objects.get(pk=respuesta.data["movimiento"])
    assert ajuste.tipo == "ajuste"
    assert ajuste.cantidad == -2
    assert ajuste.estado == "listo"
    assert ajuste.motivo == "Se rompieron dos"
    assert ajuste.usuario == usuario
    assert Movimiento.objects.count() == 2


def test_contar_de_mas_registra_un_ajuste_positivo(cliente, usuario, producto):
    respuesta = _contar(cliente, producto, 2, 0)

    assert respuesta.status_code == 201
    assert respuesta.data["ajuste"] == 2
    assert Movimiento.objects.get().cantidad == 2


def test_contar_lo_esperado_no_escribe_nada(cliente, usuario, producto):
    """Un conteo que coincide no deja rastro: el ledger no guarda ruido."""
    _mov(producto, usuario, 5)

    respuesta = _contar(cliente, producto, 5, 5)

    assert respuesta.status_code == 200
    assert respuesta.data == {"esperado": 5, "contado": 5, "ajuste": 0, "movimiento": None}
    assert Movimiento.objects.count() == 1


def test_el_conteo_deja_el_stock_en_lo_contado(cliente, usuario, producto):
    _mov(producto, usuario, 5)
    _contar(cliente, producto, 3, 5, motivo="Faltaban dos")

    stock = {f["producto"]: f["total"] for f in cliente.get("/api/stock/").data}

    assert stock[producto.pk] == 3


def test_el_ajuste_va_al_estado_que_se_conto(cliente, usuario, producto):
    """Contar cajas no puede dejar el armado en negativo."""
    _mov(producto, usuario, 5, estado="en_caja")

    respuesta = _contar(cliente, producto, 3, 5, estado="en_caja", motivo="Faltaban dos")

    assert respuesta.status_code == 201
    stock = {f["producto"]: f for f in cliente.get("/api/stock/").data}[producto.pk]
    assert stock["total"] == 3
    assert stock["en_caja"] == 3
    assert stock["listo"] == 0


def test_si_el_stock_esta_repartido_hay_que_decir_que_se_conto(cliente, usuario, producto):
    """Elegir por el operador es inventar cual de las dos pilas se achico."""
    _mov(producto, usuario, 2, estado="en_caja")
    _mov(producto, usuario, 3, estado="listo")

    respuesta = _contar(cliente, producto, 4, 5, motivo="Faltaba una")

    assert respuesta.status_code == 400
    assert "estado" in respuesta.data
    assert Movimiento.objects.count() == 2


def test_un_faltante_exige_motivo(cliente, usuario, producto):
    """Un ajuste sin motivo es un numero magico y no se puede auditar (D-08)."""
    _mov(producto, usuario, 5)

    respuesta = _contar(cliente, producto, 3, 5)

    assert respuesta.status_code == 400
    assert "motivo" in respuesta.data
    assert Movimiento.objects.count() == 1


def test_un_sobrante_no_exige_motivo(cliente, usuario, producto):
    """Que aparezca mercaderia no necesita explicacion para corregir el numero."""
    respuesta = _contar(cliente, producto, 2, 0)

    assert respuesta.status_code == 201
    assert Movimiento.objects.get().motivo == "Diferencia de conteo"


def test_el_motivo_del_conteo_se_conserva(cliente, usuario, producto):
    _mov(producto, usuario, 5)
    respuesta = _contar(cliente, producto, 4, 5, motivo="Se rompio una pata")

    assert Movimiento.objects.get(pk=respuesta.data["movimiento"]).motivo == "Se rompio una pata"


def test_si_el_esperado_cambio_se_rechaza_sin_escribir(cliente, usuario, producto):
    """Entre mirar la hoja y apretar el boton puede entrar o salir mercaderia.

    Contar contra el numero que el operador ya no esta viendo convierte una carrera en un
    ajuste fantasma. Se rechaza y se le muestran los numeros de ahora.
    """
    _mov(producto, usuario, 5)
    _mov(producto, usuario, -2, tipo="venta")

    respuesta = _contar(cliente, producto, 5, 5, motivo="Conteo")

    assert respuesta.status_code == 409
    assert respuesta.data["esperado"] == 3
    assert Movimiento.objects.count() == 2


def test_el_conteo_no_admite_cantidad_negativa(cliente, usuario, producto):
    _mov(producto, usuario, 5)

    respuesta = _contar(cliente, producto, -1, 5)

    assert respuesta.status_code == 400
    assert "contado" in respuesta.data
    assert Movimiento.objects.count() == 1


def test_el_conteo_necesita_un_producto_del_catalogo(cliente, usuario):
    respuesta = cliente.post(
        "/api/conteo/", {"producto": 9999, "contado": 1, "esperado": 0}, format="json"
    )

    assert respuesta.status_code == 400
    assert "producto" in respuesta.data
    assert Movimiento.objects.count() == 0


# --- el ajuste suelto exige motivo -------------------------------------------


def test_el_ajuste_suelto_exige_motivo(cliente, usuario, producto):
    """D-08: un ajuste sin motivo es un numero magico y no se puede auditar."""
    respuesta = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": -2, "tipo": "ajuste"},
        format="json",
    )

    assert respuesta.status_code == 400
    assert "motivo" in respuesta.data
    assert Movimiento.objects.count() == 0


def test_la_entrada_no_exige_motivo(cliente, usuario, producto):
    """La regla nueva es del ajuste, no de todo el ledger."""
    respuesta = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 3, "tipo": "entrada_compra"},
        format="json",
    )

    assert respuesta.status_code == 201
    assert Movimiento.objects.get().motivo == ""


def test_el_ajuste_con_motivo_sigue_funcionando(cliente, usuario, producto):
    """El ajuste manual que ya existia no se rompe: solo se le exige el motivo."""
    respuesta = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": -2, "tipo": "ajuste", "motivo": "conteo fisico"},
        format="json",
    )

    assert respuesta.status_code == 201
    assert Movimiento.objects.get().motivo == "conteo fisico"
