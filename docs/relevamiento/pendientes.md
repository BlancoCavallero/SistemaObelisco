# Pendientes del relevamiento — Sistema Obelisco

Estado al 2025-11-18. **De 18 preguntas quedan 4**, y solo **2 pueden invalidar el diseño**.

---

## 1. Las preguntas que faltan

### Q1 — Placares y amoblamientos de cocina · **puede invalidar el diseño**

> **"Los placares y las cocinas que venden: ¿los compran ya armados a un fabricante, le encargan
> a un fabricante que los haga con las medidas del cliente, o los arman ustedes acá?"**

**Por qué importa.** Es el último cabo suelto del catálogo, y choca de frente con lo que ya
dijiste: **no hay pedidos por encargo** (D11). Si no se piden cosas que no están, estos artículos
tienen que estar en stock o ser una excepción que hay que nombrar.

**Qué cambia según la respuesta:**

| Respuesta | Consecuencia en el modelo |
|---|---|
| **Se compran hechos** | Son artículos de stock como cualquier otro. **Nada especial: el escenario más barato.** |
| **Se encargan con medidas** | **Existe un modo "a pedido"** que contradice D11. Obliga a modelar pedido, espera, precio por medida y qué pasa si el cliente se arrepiente. Es el escenario más caro de todos. |
| **Los arman ustedes** | Hay **insumos** (melamina, herrajes) y un proceso de producción que hoy no está en el modelo: el stock ya no es solo de artículos vendibles. |

**Si no se responde:** asumo "se compran hechos". Si es falso, hay que rehacer el corazón del
modelo de catálogo. **Es la única pregunta que no conviene dejar abierta.**

---

### Q2 — Juegos y combos · **puede invalidar el diseño**

> **"¿Venden juegos? Por ejemplo un living de 3 cuerpos o un comedor de 6 sillas. Si los venden,
> ¿el precio es del juego completo o de cada pieza? ¿Y pueden vender una pieza sola?"**

**Por qué importa.** Define si un juego es **un artículo** o **varios**, y eso toca el stock, el
precio y el documento de facturación al mismo tiempo.

**Qué cambia según la respuesta:**

| Respuesta | Consecuencia en el modelo |
|---|---|
| **No venden juegos** | Nada. El escenario más simple. |
| **Sí, como artículos separados con precio cada uno** | Simple: tres artículos, tres precios. |
| **Sí, con un precio único de conjunto** | Hace falta el concepto de **combo**: un precio agrupado que descuenta stock de varias piezas a la vez. Es la parte más delicada del catálogo. |

**Si no se responde:** asumo artículos individuales sin combos. Si hay combos con precio
agrupado, el MVP no los puede registrar bien y hay que agregarlos después.

---

### Q3 — Consignación · **barata de agregar después**

> **"¿Hay mercadería en el local que sea de un proveedor y que ustedes no hayan comprado?
> Por ejemplo: un sillón que el fabricante dejó para exhibir, y que le pagan solo si se vende."**

**Por qué importa.** Si existe, hay **stock que no es propio**. El sistema tiene que saber de
quién es cada cosa; si no, el total de inventario incluye mercadería ajena y el número deja de
ser real.

**Qué cambia:** si la respuesta es **no**, se descarta y no cuesta nada. Si es **sí**, se agrega un
campo de propiedad del artículo y el conteo separa propio de ajeno.

**Si no se responde:** asumo todo propio. Después se puede agregar el campo, pero los conteos ya
hechos mezclan las dos cosas.

---

### Q4 — Para el contador · **no bloquea el diseño, sí el módulo de documentos**

> **"¿Me podés dar una factura de ejemplo, o el listado de datos que usás, para que el sistema
> genere exactamente lo que necesitás?"**

**Por qué importa.** D6 dice que el sistema genera un documento **interno** para el personal o el
contador, sin CAE. Sin saber qué campos usa el contador, el documento se arma de memoria y
después falta algo.

**Lo que necesito ver:** fecha · cliente (nombre, CUIT o DNI, condición frente al IVA) · detalle de
artículos · cantidad · precio unitario · descuento · total · si discrimina IVA · y si hay algo
más que hoy copia a mano.

**Si no se responde:** genero un documento razonable y el contador lo va a retipear igual — con lo
cual el sistema no ahorra nada en ese punto.

---

### Q5 — Exhibición · **30 segundos, decisión menor**

> **"¿Necesitás saber qué está exhibido en el salón y qué está guardado en el depósito, o el
> salón es simplemente otro lugar donde hay mercadería?"**

**Por qué importa.** Define si "exhibido" es un **estado del artículo** o apenas una **ubicación**.
Si es un estado, alguien tiene que actualizarlo cada vez que algo sale o entra de exhibición —una
tarea nueva, justo lo que no queremos—.

**Si no se responde:** asumo que el salón es una **ubicación más**, que es lo más barato y lo que
el modelo ya soporta (A14).

---

## 2. Falta decidir (mío, 10 — todas desbloqueadas)

1. Parámetros configurables: margen por rubro (10%), descuento efectivo (5%), % de armado, plazo
   de devolución (15 días), localidades.
2. Hosting y despliegue web.
3. Usuarios, roles y sesión persistente.
4. Identidad de producto: duplicados y convención de nombre.
5. Cuenta corriente y saldo.
6. Vigencia de precios.
7. Carga progresiva del stock (entrada sin compra).
8. Imágenes de producto.
9. Baja lógica de artículos.
10. Devolución a proveedor por daño o falla.

---

## 3. Lo que ya está cerrado (para no volver a abrirlo)

Sistema anterior (D1) · factura electrónica (D2, fase 2) · volumen de ventas (D3) · volumetría
(D4) · cantidad de personas · nombre del Mocho (Norberto) · ubicación del local (Tres Lomas) ·
seña y reserva (A3 retirada) · destino del documento (D6) · descuento, armado, plazo y margen
(A21) · mantenimiento (D8) · equipos (A23) · localidades (Quenuma, ampliables) · un sector puede
mezclar categorías (A14) · usuarios y web (A24-A26) · pedidos por encargo (D11) · moneda en pesos
(S43) · devolución a proveedor (S43) · garantías del fabricante (S48) · colchones sin medidas
(S49) · verano como categoría (S47) · baja lógica con historial (A29) · el sistema reemplaza el
papel (D9) · arranque progresivo (S41) · diferencias de conteo: se ajustan ahora, se auditan
después (A28).
