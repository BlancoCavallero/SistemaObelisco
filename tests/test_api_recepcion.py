"""Recepcion de mercaderia: buscar antes de crear, y todo lo que entra queda como movimiento."""

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from catalogo.models import Producto
from inventario.models import Movimiento


@pytest.fixture
def cliente(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


def _payload(tipo, **over):
    base = {
        "tipo": tipo.pk,
        "color": "gris",
        "alto_cm": 85,
        "ancho_cm": 90,
        "largo_cm": 180,
        "modelo": "",
    }
    base.update(over)
    return base


# --- buscar antes de crear -------------------------------------------------


def test_buscar_producto_por_atributos(cliente, producto):
    r = cliente.get(
        "/api/productos/buscar/",
        {"tipo": producto.tipo_id, "color": "gris", "alto_cm": 85, "ancho_cm": 90, "largo_cm": 180},
    )
    assert r.status_code == 200
    assert [p["id_visible"] for p in r.data] == [producto.id_visible]


def test_buscar_por_texto_libre(cliente, producto):
    r = cliente.get("/api/productos/buscar/", {"q": "sillon"})
    assert r.status_code == 200
    assert len(r.data) == 1


def test_buscar_sin_coincidencias_devuelve_lista_vacia(cliente, producto):
    r = cliente.get("/api/productos/buscar/", {"color": "rojo"})
    assert r.status_code == 200
    assert r.data == []


# --- no se puede duplicar --------------------------------------------------


def test_crear_producto_duplicado_devuelve_conflicto_y_no_crea(cliente, tipo, producto):
    r = cliente.post("/api/productos/", _payload(tipo), format="json")

    assert r.status_code == 409
    assert r.data["producto_existente"]["id_visible"] == producto.id_visible
    assert Producto.objects.count() == 1


def test_crear_producto_nuevo_devuelve_201_y_id_visible(cliente, tipo):
    r = cliente.post("/api/productos/", _payload(tipo, color="negro"), format="json")

    assert r.status_code == 201
    assert r.data["id_visible"].startswith("MUE-")
    assert r.data["nombre"] == "Sillon 3 cuerpos - Negro - 85x90x180"
    assert Producto.objects.count() == 1


def test_crear_producto_con_color_invalido_devuelve_400(cliente, tipo):
    r = cliente.post("/api/productos/", _payload(tipo, color="fucsia"), format="json")

    assert r.status_code == 400
    assert "color" in r.data


# --- la entrada es un movimiento -------------------------------------------


def test_entrada_suma_stock_y_registra_autor(cliente, usuario, producto):
    r = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 6, "tipo": "entrada_compra"},
        format="json",
    )

    assert r.status_code == 201
    mov = Movimiento.objects.get()
    assert mov.usuario == usuario
    assert mov.cantidad == 6


def test_entrada_sin_posicion_es_valida(cliente, producto):
    r = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 2, "tipo": "entrada_inventario_inicial"},
        format="json",
    )
    assert r.status_code == 201
    assert Movimiento.objects.get().posicion is None


def test_entrada_con_cantidad_cero_devuelve_400(cliente, producto):
    r = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 0, "tipo": "entrada_compra"},
        format="json",
    )
    assert r.status_code == 400


def test_entrada_rechaza_tipo_desconocido(cliente, producto):
    r = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 1, "tipo": "inventado"},
        format="json",
    )
    assert r.status_code == 400


def test_movimiento_requiere_autenticacion(producto):
    r = APIClient().post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 1, "tipo": "entrada_compra"},
        format="json",
    )
    assert r.status_code in (401, 403)
    assert Movimiento.objects.count() == 0


# --- el stock es derivado --------------------------------------------------


def test_stock_refleja_la_suma_de_movimientos(cliente, usuario, producto):
    for cantidad, tipo in [
        (10, "entrada_compra"),
        (3, "entrada_inventario_inicial"),
        (-4, "venta"),
    ]:
        Movimiento.objects.create(producto=producto, usuario=usuario, cantidad=cantidad, tipo=tipo)

    r = cliente.get("/api/stock/")

    assert r.status_code == 200
    fila = next(f for f in r.data if f["producto"] == producto.pk)
    assert fila["total"] == 9
    assert fila["nombre"] == producto.nombre


def test_stock_no_incluye_productos_inactivos(cliente, usuario, producto):
    Movimiento.objects.create(producto=producto, usuario=usuario, cantidad=5, tipo="entrada_compra")
    producto.activo = False
    producto.save()

    r = cliente.get("/api/stock/")

    assert r.status_code == 200
    assert r.data == []


def test_el_movimiento_sigue_siendo_inmutable_desde_la_api(cliente, usuario, producto):
    mov = Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=5, tipo="entrada_compra"
    )
    with pytest.raises(ValidationError):
        mov.cantidad = 99
        mov.save()


@pytest.mark.parametrize("tipo_no_representable", ["armado", "transferencia"])
def test_movimientos_que_cambian_otra_dimension_no_se_cargan_a_mano(
    cliente, producto, tipo_no_representable
):
    """`armado` and `transferencia` do not change the total but change a dimension the
    ledger lacks today. Accepting them here would silently distort stock."""
    r = cliente.post(
        "/api/movimientos/",
        {"producto": producto.pk, "cantidad": 1, "tipo": tipo_no_representable},
        format="json",
    )
    assert r.status_code == 400
    assert Movimiento.objects.count() == 0


def test_el_staff_ve_el_stock_disponible(cliente, usuario, producto):
    from inventario.models import Movimiento

    Movimiento.objects.create(producto=producto, usuario=usuario, cantidad=7, tipo="entrada_compra")

    respuesta = cliente.get("/api/productos/buscar/")

    assert respuesta.data[0]["stock"] == 7


def test_el_detalle_de_un_producto(cliente, producto):
    respuesta = cliente.get(f"/api/productos/{producto.pk}/")

    assert respuesta.status_code == 200
    assert respuesta.data["id"] == producto.pk
    assert respuesta.data["id_visible"] == producto.id_visible
    assert "precio_venta" in respuesta.data


def test_detalle_de_un_producto_inexistente(cliente):
    assert cliente.get("/api/productos/999999/").status_code == 404


def test_el_detalle_requiere_sesion(producto):
    from rest_framework.test import APIClient

    assert APIClient().get(f"/api/productos/{producto.pk}/").status_code in (401, 403)
