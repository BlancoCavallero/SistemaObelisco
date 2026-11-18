# Lote de preguntas — cierre de captura

Emitido: 2025-11-18 · Actualizado con las respuestas del desarrollador.

## Estado de las respuestas

| Pregunta | Estado |
|---|---|
| P3 (facturación) | **Diferida a fase 2** — D2: fase 1 son los medios para facturar fácil; AFIP queda para después |
| P4 (quién carga) | Respondida parcial: "los empleados" al llegar la mercadería. Falta nombre y minutos |
| P5 (cuántos hay) | Respondida: **no se sabe**. Es el principal desafío |
| P5 (ventas/mes) | **Retirada** — D3 |
| P8 (catálogo) | Respondida: categoría, tipo, color, alto/ancho/largo |
| P36 (nombre) | Respondida: Norberto |
| P37, P38, P39 | Sin responder. No bloquean |
| Resto | Sin responder |

## Preguntas nuevas

**P41 `[cliente]` — ¿Cómo distinguís dos artículos iguales?**
Dos sillones grises, mismo tipo, mismas medidas, pero distinto modelo o de distinto
proveedor: ¿qué dato los diferencia en el sistema? ¿Hay un nombre comercial o un código de
fábrica que uses?
*Sin esto, la identidad del artículo queda incompleta (H13).*

**P42 `[cliente]` — ¿Para quién se imprime ese documento?**
El que va a generar el sistema, ¿se lo queda el negocio, se lo das al contador, o se lo
entregás al cliente?
*Si se lo entregás al cliente no es una lista interna: es un comprobante y necesita CAE.
D2 asume que es interno. Parcialmente respondida en el bloque 9: "los medios para que ellos
puedan facturar de manera sencilla". Falta el destinatario.*

**P43 `[cliente]` — ¿Qué datos necesita el contador para poder facturar?**
Pedile a un contador una factura de ejemplo y anotá exactamente qué campos usa.
*Es la entrada del módulo de comprobantes. Sin esto se construye de memoria.*

---

## Lo que queda por preguntar al cliente

Consolidado al 2025-11-18. **Ya no se pregunta:** el sistema anterior (D1), volumen de ventas
(D3), volumería (D4), factura electrónica (D2 fase 2), seña (A3 retirada), cantidad de
personas (no es requisito), nombre del Mocho (Norberto), ubicación del local (Tres Lomas).

### Bloquean el arranque (4)

**1. `P4` — ¿Cuántos minutos por día, reales, puede dedicar alguien a cargar datos?**
*Define si el MVP sobrevive. Es el único número del proyecto que puede hundirlo solo.*

**2. `P7` — ¿Todo lo que sale del depósito va a quedar registrado en el sistema?**
No pedir el detalle de lo que no se registra. Sólo necesitamos saber si se puede asumir que sí.
*Define si el criterio de éxito es alcanzable.*

**3. `P6` — ¿Quién hace el conteo inicial y cuánto tarda?**
Cerrar el local ya está resuelto (cualquiera lo hace). Falta: quién, en cuántas sesiones, por
sectores o todo junto.
*Define la arrancada del sistema.*

**4. `P42` — El documento que genera el sistema, ¿es para el contador o se lo das al cliente?**
*Si se lo das al cliente no es una lista: es un comprobante y necesita CAE. Define si hay
exposición fiscal.*

### Definen el modelo (5)

**5. `P11` — Placares y amoblamientos de cocina: ¿se compran hechos, se mandan a hacer, o los arman ustedes?**

**6. `P10` — ¿Venden juegos o combos? ¿El precio es del juego o por pieza? ¿Se puede vender una pieza sola?**

**7. `P12` — ¿Se puede pedir un mueble en una tela o color que no está en el salón? ¿Cuánto tarda?**

**8. `P25` — Devoluciones: ¿en qué plazo y en qué condiciones se aceptan? ¿Con caja cerrada? ¿Con o sin comprobante?**
*Sin regla, cada devolución es una negociación y los datos no sirven.*

**9. Cuenta corriente: ¿quién la obtiene, hay un límite, qué pasa si no paga a los 60 días? ¿Se cobra interés?**
*Es riesgo de crédito del negocio, no del procesador de pagos.*

### Operación (5)

**10. Proveedores: ¿cuántos? ¿Compran en pesos o en dólares? ¿Cuánto tardan en reponer? ¿Qué hacen con lo dañado?**

**11. ¿Quién actualiza las listas de precios de fábrica y cada cuánto llegan?**

**12. El 5% por efectivo: ¿es siempre? ¿Aplica aunque pidan comprobante?**

**13. El 6–7% de armado: ¿va aparte en el documento o dentro del precio del mueble?**

**14. ¿Qué porcentaje de ganancia usan por rubro?**
*No está en el MVP, pero es la única forma de que un precio signifique algo.*

### Proyecto (3)

**15. ¿Cuántos equipos y dónde? ¿La conexión del local es estable? ¿Necesitan vender si se corta internet?**

**16. ¿Presupuesto y plazo? ¿Quién mantiene el sistema después?**

### Triviales, si sobra tiempo (2)

**17. `P39` — “Quenumil” se escribe así? ¿Las cinco localidades son todas?**

**18. ¿Un sector del almacén puede mezclar categorías o se reserva a una sola?**
*Es el único hueco del modelo de ubicación (`mvp.md`, sección 3).*

---

## Cómo usar este lote

- **Nivel 1** se pregunta sí o sí. Sin esas respuestas no se puede proponer nada.
- **Nivel 2** define el modelo de datos. Se responde de a poco, en la misma charla.
- **Nivel 3** completa la operación. Se puede mandar por escrito.
- **Nivel 4** es de proyecto, no de negocio. Puede ir después.
- **Nivel 5** son discrepancias para limpiar en 2 minutos.

**Retiradas por decisión del cliente (D1):** el sistema anterior no se investiga. Las
preguntas P0, P1 y P2 quedan fuera de circulación. La restricción que importaba de ahí —el
tiempo real disponible por día— se captura con **P4**.

Versión para usar en la reunión: `entrevista.md`.

Etiquetas: `[cliente]` la responde el negocio · `[contador]` requiere al contador ·
`[vos]` la decidís vos, no el negocio · `[verificación]` se confirma con evidencia, no con
palabra.

Regla: todo lo que respondan se transcribe **verbatim** en `bitacora.md` antes de
interpretarlo. No se pregunta nada que ya esté respondido en la bitácora.

---

## Nivel 1 — Bloqueantes (5)

Sin estas no hay propuesta.

**P3 `[contador]` — ¿Qué evento dispara la factura?**
Condición fiscal del negocio (RI / monotributo / exento), por qué hoy salen facturas B y C,
quién maneja el certificado AFIP y los puntos de venta.
*Bloqueante legal: hoy se factura al terminar de pagar y eso no se puede replicar.*

**P4 `[cliente]` — ¿Quién carga el stock en el sistema, y cuándo?**
Nombre, momento del día o de la semana, y **cuántos minutos reales** va a tener por día.
*Riesgo #1. Si la respuesta es "nadie tiene tiempo", el proyecto no arranca: es exactamente
lo que mató al sistema anterior (D1).*

**P5 `[cliente]` — Números gruesos de hoy.**
¿Cuántos artículos distintos (modelos/SKU)? ¿Cuántos artículos físicos en total? ¿Cuántas
ventas por mes y ticket promedio? Aproximado está bien.
*Sin números no hay dimensionamiento, ni migración, ni cronograma.*

**P6 `[cliente]` — El stock inicial.**
¿Quién hace el conteo físico? ¿Se puede cerrar el local unas horas o hacerlo por sector
(depósito primero, salón después)? ¿Cuánto tardarían?
*Es el esfuerzo oculto más grande del proyecto y el que menos se presupuesta.*

**P7 `[cliente]` — ¿Todo el egreso de mercadería va a quedar registrado en el sistema nuevo?**
No necesito el detalle de lo que no se registra. Necesito saber si puedo asumir que sí.
Si la respuesta es "no", el stock va a tener diferencias permanentes y eso se acuerda por
escrito antes de empezar, no después.
*Define si el criterio de éxito (saber cuánto hay) es alcanzable.*

---

## Nivel 1-bis — Retiradas (3)

**Fuera de circulación por D1.** El cliente decidió que el sistema anterior no se investiga.
Se conservan acá solo para dejar constancia de que la decisión fue explícita y no un olvido.

**P0 — El día que se abandonó el sistema anterior.** Retirada.

**P1 — ¿Qué sistema de stock era?** Retirada.

**P2 — ¿Qué intentaron hacer con él y no pudieron?** Retirada.

> Lo único que se necesitaba de estas tres era **cuánto tiempo real hay por día para cargar
datos**. Eso se pregunta directamente en **P4** y no requiere hablar del sistema anterior.

---

## Nivel 2 — Modelo de datos (11)

**P8 `[cliente]` — ¿Cuántos modelos distintos manejan, y cuántas variantes por modelo?**
Ejemplo: sillón X en 5 telas y 4 colores, ¿son 20 artículos distintos o uno solo?

**P9 `[cliente]` — ¿Los muebles vienen con código del fabricante?**
¿Ese código identifica el artículo o cada proveedor usa el suyo? ¿Traen código de barras?

**P10 `[cliente]` — ¿Venden juegos o combos?** (living de 3 cuerpos, comedor de 6)
¿Precio por juego o por pieza? ¿Se puede vender una pieza sola?

**P11 `[cliente]` — Placares y amoblamientos de cocina: ¿se compran hechos, se encargan a un
tercero, o se arman ustedes?**
*Tercera vez que aparece "hacemos". No se puede resolver por el texto.*

**P12 `[cliente]` — ¿El cliente elige tela o color de un sillón que hay que pedir, o se vende
lo que está en el salón?**
*Define si existe el pedido por encargo, con espera, distinto de la venta de stock.*

**P13 `[cliente]` — ¿Necesitan saber qué pieza física entregaron?**
Número de serie, etiqueta, remito con detalle. ¿Hay garantías formales que lo exijan?

**P14 `[cliente]` — Electrodomésticos: ¿la garantía la da el negocio o el fabricante?**
¿Hay devoluciones por falla? ¿Qué hacen con el artículo?

**P15 `[cliente]` — Colchones: ¿medidas fijas o a medida?** ¿Tienen lógica de stock distinta
al resto?

**P16 `[cliente]` — ¿Cuándo un artículo figura como disponible: en caja o armado?**
¿Se puede vender en caja si el cliente lo pide? ¿Quién arma y en qué orden?

**P17 `[cliente]` — Artículos de verano: ¿se guardan de un año para otro o se liquidan?**
*Un stock estacional que no rota cambia la estrategia de reposición.*

**P18 `[cliente]` — ¿Hay mercadería en consignación?**
Artículos de un proveedor exhibidos sin comprarlos. Si no hay, mejor: se saca del modelo.

---

## Nivel 3 — Operación (10)

**P19 `[cliente]` — ¿Cada cuánto cuentan el stock a mano, quién lo hace y cuánto tardan?**

**P20 `[cliente]` — Cuando aparece una diferencia, ¿qué hacen?** ¿Se ajusta y listo o se
investiga?

**P21 `[cliente]` — Proveedores: ¿cuántos activos?** ¿Compran en pesos o en dólares? ¿Pagan
contado o a plazo?

**P22 `[cliente]` — ¿Cuánto tarda un proveedor en reponer?**
*Si repone rápido, conviene reposición (sillones). Si tarda, hay que stockear.*

**P23 `[cliente]` — ¿Hay devoluciones a proveedor o mercadería dañada?** ¿Quién se come el
costo?

**P24 `[cliente]` — ¿El cliente deja seña para reservar?** ¿De cuánto? ¿Qué pasa si no vuelve?
*No apareció en ningún bloque. Puede no existir.*

**P25 `[cliente]` — Cambios y devoluciones de clientes: ¿existen?** ¿Con qué criterio y en qué
plazo? ¿Se devuelve la plata o se cambia por otro artículo?

**P26 `[cliente]` — El 5% por efectivo: ¿es siempre?** ¿Aplica también si piden factura?

**P27 `[cliente]` — El 6–7% de armado: ¿se cobra aparte en la factura o va dentro del precio
del producto?**
*Define si el armado es un ítem vendible o un recargo.*

**P28 `[cliente]` — Cuando el cliente retira en el local, ¿se lo lleva armado o en caja?**

---

## Nivel 4 — Proyecto y no funcionales (7)

**P29 `[cliente]` — ¿Quién va a usar el sistema y desde dónde?**
¿Computadora fija en el mostrador, celular, tablet? ¿Cuántos a la vez?

**P30 `[vos]` — Hosting.** ¿Nube o servidor propio? ¿La conexión del local es estable?

**P31 `[cliente]` — ¿Necesitan seguir vendiendo si se corta internet?**
*Si la respuesta es sí, es un requisito de arquitectura, no un detalle.*

**P32 `[cliente]` — Presupuesto y plazo.** ¿Hay un número y una fecha, o se define después?
*Cambia todo lo que se puede proponer.*

**P33 `[vos]` — ¿Quién mantiene el sistema después de entregado?**
¿Vos, un tercero, nadie? Si la respuesta es "nadie", el diseño tiene que ser mucho más
conservador.

**P34 `[cliente]` — ¿Qué pasa con el papel actual?** ¿Se digitaliza algo o la carpeta sigue
existiendo en paralelo?
*Dos registros en paralelo es la forma más rápida de que ninguno sea confiable.*

**P35 `[cliente]` — Datos de clientes.** ¿Se guarda nombre, dirección, teléfono, deuda?
*Cuenta corriente sí o sí. Ley 25.326 aplica.*

---

## Nivel 5 — Discrepancias a limpiar (5)

**P36 `[cliente]` — "Tal Mocho" es "el Mocho"?** ¿Nombre real?
*El mismo párrafo dice después "el Mocho y el Chino del negocio anterior".*

**P37 `[cliente]` — ¿Son cinco personas o seis?** ¿La hija del Chino trabaja en el negocio o
solo hace lo administrativo desde afuera?

**P38 `[cliente]` — ¿Dónde está el local?**
*Nunca se dijo. Trenque figura como destino de reparto, así que el local probablemente no
está en Trenque.*

**P39 `[cliente]` — ¿Las cinco localidades son todas?** ¿"Quenumil" se escribe así?

**P40 `[cliente]` — Los pedidos que se hacen fuera de horario: ¿se cargan en el sistema en ese
momento o se anotan para cargar después?**
*Define si la pantalla de compras tiene que funcionar sin conexión o fuera del local.*
