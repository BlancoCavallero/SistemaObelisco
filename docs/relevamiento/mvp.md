# MVP — Sistema Obelisco: primero el conteo

Qué es: el entregable mínimo, derivado de `alcance.md` (S1–S24, D1–D4, A1–A20, Riesgos 1–13)
y de `bitacora.md` (O1–O63). No agrega hechos: lo que no está respondido va `[abierto]` con
la pregunta (P#) que lo cerraría. Es una **propuesta**, no un acuerdo: por S3 no se construye
nada hasta que el negocio la valide por escrito. Fuera de alcance de este documento: stack,
motor de base de datos, pantallas y diagramas.

---

## 1. Alcance del MVP — "primero el conteo"

**Objetivo, en palabras del negocio:** que la pregunta "cuánta mercadería tengo en el
negocio" tenga respuesta y que ese número sea el real — hoy el dueño no la sabe (S8) y
"cuantos articulos hay no se sabe y es el principal desafio" (S12, O31, O37).

El MVP no es un sistema de gestión: es el sistema que **hace posible el conteo** (O37). El
resto (precios, cuotas, rutas, comprobantes) se cuelga después, sobre el mismo registro de
movimientos.

### Lo que entra

| # | Capacidad | Por qué | Código |
|---|---|---|---|
| 1 | Registrar la entrada cuando la mercadería llega: categoría, tipo, color, alto, ancho, largo y cantidad | Es el punto de captura que ya existe en el negocio | S13, S11, O40, O38 |
| 2 | Un solo registro por producto: la carga **empieza buscando** si ya existe | Si el mismo sillón se crea dos veces, el stock se parte y la suma real se vuelve invisible | A19, S24, O62 |
| 3 | Consultar qué hay | Es la pregunta que hoy nadie puede responder | S8, S12 |
| 4 | Contar y registrar el conteo | No hay histórico ni planilla previa: el número inicial sale del conteo | S12, A15, O49, D3 |
| 5 | Distinguir *en caja* de *armado* | Un placard en caja no es exhibible ni entregable | S10, A12, O25 |
| 6 | Generar el documento/lista para que el responsable o el contador facturen | Fase 1: "proveeremos los medios para que ellos puedan facturar de manera sencilla" | S16, S14, D2 |
| 7 | Registrar la salida: venta, entrega, armado, devolución | Sin salida el conteo no explica ninguna diferencia: sólo cuenta lo que entró | A1, A13, A18 |
| 8 | Un usuario por empleado, sesión persistente, dos roles como máximo | Sin autor registrado no hay trazabilidad, y sin trazabilidad un conteo no se puede auditar ni corregir | S39, A20, A24, A25 |

Los movimientos del punto 7 son el mínimo que la sección 2 demuestra que se puede capturar
sin agregar tareas. No incluyen precios, cuotas ni rutas: cada uno de esos es alcance de R9,
R11 y R10, no del MVP.

### Lo que NO entra, y por qué

| Fuera | Razón declarada | Código |
|---|---|---|
| Factura electrónica (AFIP/ARCA) | Fase 2: primero los medios para facturar fácil, la integración después | D2, S16, S6 |
| Volumetría: m³, capacidad de carga por volumen | "en cuanto al volumen no es algo que nos interese" | D4, O46 |
| Reservas y señas | Hipótesis retirada: "no hay seña para reservar". Lo que existe es venta en cuotas, que no reserva | A3, S23, O59 |
| Número de serie por unidad | "si son iguales simplemente hay stock del mismo producto": la identidad es por producto | A19, S24, O61 |
| Reportes de rotación o márgenes | No hay histórico que reportar, y el volumen de ventas se retiró como pregunta | D3, O43 |
| Venta online | Expectativa sin fecha ni decisión: condiciona el diseño, no el entregable | S2, O32 |
| Permisos finos por empleado | Dos roles alcanzan; un rol por persona es una lista de nombres disfrazada de permisos | A24, O77 |
| Ubicación obligatoria al recibir | El depósito hoy no está organizado; si ubicar es requisito, el conteo no se hace | A15, O49 |

Consecuencia aceptada del MVP: el stock **no va a cerrar** contra el conteo mientras exista
egreso que no pasa por el circuito documentado. Es un límite del negocio, no del software
(C1, Riesgo 6, y la respuesta a P7).

---

## 2. El ritual mínimo — presupuesto de tiempo

Regla de diseño: **todo movimiento de stock es subproducto de algo que ya ocurre** (A13). Si
un movimiento obliga a "acordarse de actualizar el stock", no se registra y el sistema muere
igual que el anterior: no falló por funciones, "nunca lo implementarion por falta de tiempo"
(D1, R11, R12, O34, O35).

### Los seis movimientos y el hecho del que cuelga cada uno

| Movimiento | Momento en que ya ocurre (evidencia) | Campos que tipea el operador | Presupuesto |
|---|---|---|---|
| Recepción | Al abrir la mercadería que llega: "una vez que ingresa la mercadería, se abre" (S13, O40) | Artículo nuevo: categoría, tipo, color, alto, ancho, largo, cantidad → **7**. Artículo existente: cantidad → **1** (A19) | 90 s por artículo nuevo · 15 s por línea repetida |
| Armado en depósito | Cuando Diego arma la caja antes de exhibir o vender (S10, A12, O25) | producto + cantidad → **2** | 10 s por unidad |
| Venta | En el mostrador, con el cliente adelante: "se larga la venta" (O21, O13) | producto + cantidad + cliente + modalidad (en caja o con armado) → **3** si el cliente ya está cargado, **6** si es nuevo (A16, A17) | 60 s |
| Entrega / reparto | Al cerrar la ruta del día: 3 o 4 pedidos por viaje a una localidad (A11, O18, O19) | un tilde por pedido → **1 por pedido** | 5 s por pedido · 2 min por viaje |
| Devolución | Cuando el cliente vuelve con el artículo (A18, O55) | producto + cantidad + estado en que vuelve, y ajuste de cuenta si fue en cuotas → **3 o 4** (O56) | 60 s; es esporádico y no entra al presupuesto diario (Riesgo 13, P25) |
| Conteo | Después del cierre, y lo puede hacer cualquiera porque cualquiera cierra (O63) | cantidad contada → **1 por artículo** | 3–5 s por artículo; es una sesión, no una tarea diaria (P6, P19) |

### Presupuesto por día

El costo de cada movimiento está acotado; el total diario **no se puede cerrar todavía**:
cuántos artículos y cuántas ventas hay por día no se sabe, y la pregunta se retiró (S12, D3,
O43, P5 retirada). La cuenta queda planteada, no resuelta:

`min/día = (altas × 90 s + líneas repetidas × 15 s) + (armados × 10 s) + (ventas × 60 s) + (pedidos entregados × 5 s)`

Propuesta de techo de diseño: **15 minutos por día** para el conjunto de movimientos diarios,
con el conteo como sesión aparte. Ese techo es una propuesta nuestra, no un dato del cliente.

> `[abierto]` — **Cuántos minutos por día tiene el negocio para esto no está respondido.**
> Lo cierra **P4** ("cuántos minutos reales va a tener por día"). Sin esa respuesta, el
> presupuesto de arriba es una hipótesis, y el sistema nuevo compite contra el mismo déficit
> de tiempo que mató al anterior (Riesgo 10, Riesgo 11, R14).

**Si la respuesta es menor que el presupuesto**, el orden de recorte ya está decidido por las
specs y no por gusto. Primero cae el registro de entrega: se reconstruye del remito firmado
que ya se guarda en carpeta (O14). Después cae el armado en depósito, y el estado *caja /
armado* queda estimado (A12). Lo último que se sostiene es **recepción + conteo**, que es
exactamente el MVP de la sección 1. Si ni la recepción entra en el día, no hay MVP posible:
no existe sistema de stock que sobreviva a cero minutos (R12).

### Capturas que NO pueden existir

Crean un ritual nuevo o duplican algo que ya ocurre en otro soporte.

- **Editar el saldo de stock a mano** (A1: el stock no se edita, se registra; el saldo es derivado).
- **Dar de alta el catálogo antes de recibir**: el catálogo crece por recepción, no por planilla previa (O38, A2).
- **Asignar sector y posición a cada artículo al recibirlo**, como paso obligatorio (A15, O49).
- **Tipear el precio unitario en cada recepción**: el precio se forma con la lista de fábrica y el margen del rubro, no se transcribe (O4, A5; R9 sigue abierto).
- **Registrar número de serie por unidad** (A19, S24).
- **Cargar reservas o señas** (A3, S23).
- **Transcribir la carpeta al sistema en paralelo**: dos registros vivos es la forma más rápida de que ninguno sirva (P34, Riesgo 2).
- **Registrar el egreso que no pasa por el circuito documentado**: no se construye funcionalidad para sostenerlo (C1).

---

## 3. Modelo de ubicación — almacén, sector, posición

Tres niveles: **almacén → sector → posición** (S17, A14, O47). Se numera **ahora**, aunque el
depósito no esté organizado, para poder reorganizarlo físicamente más adelante sin renumerar
(S17, O49).

S17 dice "numeraremos internamente el almacen dependiendo de la categoria". A14 y O48 leen esa
frase como la trampa a evitar, y acá se resuelve así:

1. **El código no lleva la categoría adentro** (A14, O48). La categoría es una **asignación de
   datos** sobre la posición: se cambia cuando se mueve el mobiliario y el número no se toca.
   Si el número contiene la categoría, miente el día que esa categoría cambia de sector y
   obliga a renumerar justo lo que se quería evitar.
2. **N almacenes desde el inicio**, aunque hoy haya uno: el cliente dijo "el/los almacenes"
   (S17, O50). Un identificador de almacén fijo se paga caro después.
3. **La ubicación no es requisito para contar** (A15, O49): "cuando tengan los muebles
   organizados" implica que hoy no lo están. **Primero contar, después ubicar.**

### Flujo en dos fases

**Fase 1 — contar como está.** El conteo registra producto y cantidad, sin sector ni posición.
La ubicación queda vacía y no bloquea ni invalida el conteo. A lo sumo registra en qué
almacén se contó, porque puede haber más de uno (O50). Esto es lo que hace que el conteo
ocurra: con el depósito desordenado, exigir ubicación equivale a no contar (A15, O49).

**Fase 2 — ubicar de a poco.** Cada vez que se guarda mercadería y se sabe dónde, se asigna
sector y posición a ese producto. La asignación es incremental y opcional: no hay campaña de
ubicación obligatoria ni "pendientes de ubicar". Un producto sin ubicación es un producto
**contado**, no un producto incompleto (A13, A15).

### Códigos de ejemplo: el patrón correcto y el que hay que evitar

| Nivel | Patrón correcto | Por qué | Patrón a evitar | Qué rompe |
|---|---|---|---|---|
| Almacén | `ALM-01`, `ALM-02` | Numérico y neutro: soporta N almacenes (O50) | `ALM-MUEBLES`, `ALM-DEPOSITO` | Ata el almacén al rubro de hoy |
| Sector | `SEC-01` … `SEC-12` | Secuencial y neutral: se reasigna sin renumerar | `SEC-MUE-01`, `SEC-ELEC-02`, `SEC-DECO` | Lleva la categoría adentro: hay que renumerar al reorganizar (O48) |
| Posición | `POS-01` … `POS-40` dentro del sector | Orden físico, sin significado comercial | `POS-SILLON-GRIS`, `POS-COLCHONES-A` | Se renombra cada vez que cambia el contenido |
| Código completo | `ALM-01/SEC-07/POS-03` | Ubica, no describe | `ALM-01/MUEBLES/SILLONES` | No ubica: describe el contenido y queda viejo el primer día |

> `[abierto]` — Si un sector puede mezclar categorías o se reserva a una sola: ningún P# del
> lote vigente lo cubre, hace falta una pregunta nueva. Mientras no haya respuesta, el modelo
> no puede impedir mezclar, y eso es coherente con A14: la categoría es dato, no regla del
> número.
