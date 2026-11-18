# Diseño — Sistema Obelisco

Decisiones de diseño derivadas del relevamiento (`alcance.md`, `mvp.md`, `pendientes.md`).
No es código ni esquema final: son las decisiones que el código va a tener que respetar, con su
razón y su consecuencia. Donde una decisión depende de información que todavía no existe, está
marcada `[abierto]`.

Estado: **9 de 10 decisiones cerradas.** La 10 (stack) depende de un dato del desarrollador.

---

## D-01 · Parámetros con vigencia, no configuración editable

Los cinco parámetros de A21 se guardan en un registro con **fecha de vigencia**, igual que los
precios:

| Parámetro | Default | Alcance |
|---|---|---|
| Margen por categoría | 10% | global, con override por categoría |
| Descuento por efectivo | 5% | global |
| Porcentaje de armado | 6,5% | global `[a confirmar: el cliente dijo "6% o 7%"]` |
| Plazo de devolución | 15 días | global |
| Localidades de reparto | Tres Lomas, Salliqueló, 30 de Agosto, Casbas, Quenuma, Trenque | lista ampliable |

**Por qué con vigencia y no editables en el lugar.** Si hoy subís el margen del 10% al 15%, las
ventas de ayer tienen que seguir explicando su margen del 10%. Un parámetro que se edita en el
lugar reescribe el pasado en silencio. Es el mismo mecanismo que A5 para los precios: **nada que
afecte un número histórico se edita; se versiona.**

**Consecuencia:** no hay pantalla de "configuración". Hay un historial de parámetros, y agregar
uno nuevo es agregar una fila, no tocar código.

---

## D-02 · Gratis, sin equipo propio, sin servidor que administrar

Restricciones fijas: **$0 de costo** (pedido explícito), **nada encendido en tu casa**, **un solo
mantenedor** (D8), **web** (S40), una PC y celulares (A23), y datos que si se pierden no se
recuperan.

**Los números dicen que alcanza con holgura.** Estimación con 600 productos, 2 fotos por producto y
12.000 movimientos por año:

| Recurso | Año 1 | Año 5 | Gratuito típico | Margen |
|---|---|---|---|---|
| Base de datos | 7,8 MB | 38,9 MB | 500 MB – 1 GB | ~300x |
| Imágenes (comprimidas) | 211 MB (total) | 211 MB | 10 GB | ~50x |

### Arquitectura propuesta

| Pieza | Opción gratuita | Por qué esa |
|---|---|---|
| Aplicación | Runtime serverless (Cloudflare Workers/Pages, o Vercel) | Sin servidor que administrar y **no duerme** |
| Base | **Neon Postgres free** (o Supabase) | Postgres estándar; Neon despierta solo tras inactividad |
| Imágenes | Cloudflare R2 free (10 GB, sin costo de egreso) | Archivos afuera de la base, no blobs |
| Backup | **GitHub Actions** (cron nocturno) → `pg_dump` → R2 | Corre en la nube: **no necesita tu PC encendida** |

**Verificá las condiciones vigentes al contratar:** los planes gratuitos cambian sin aviso. Los
números de la tabla son límites típicos, no un contrato.

### Las tres cosas que sí pueden romperlo

1. **Pausa por inactividad.** Algunos planes gratuitos **duermen el proyecto**, no solo la
   aplicación: Supabase gratuito pausa tras días sin uso y hay que reactivarlo a mano. Si el
   negocio cierra dos semanas, vuelve a un sistema apagado que no se despierta solo. *Neon
   despierta al recibir la primera conexión: por eso va primero.* Un servicio web gratuito que se
   duerme a los 15 minutos solo cuesta 30–50 segundos en la primera venta del día.
2. **Los términos cambian.** Heroku eliminó su plan gratuito en 2022 y se llevó miles de proyectos.
   Por eso: **Postgres estándar y archivos por API S3**, nunca una API propietaria que no se pueda
   exportar. Migrar debe ser un `pg_dump` y una copia de archivos, no una reescritura.
3. **Sin SLA y sin soporte.** Si se rompe un sábado, no hay a quién llamar. Ese es el precio real de
   $0, y con un solo mantenedor es el riesgo que más pesa.

### La regla que no se negocia

> **Gratis el alojamiento, nunca el backup.**

Si el plan gratuito pierde los datos, el proyecto falla exactamente en aquello para lo que existe:
saber cuánta mercadería hay. Consecuencias obligatorias:

- **Dump nocturno** de la base a almacenamiento externo: retención 30 días + una copia mensual
  permanente.
- **Restauración probada una vez por mes.** Un backup que nunca se restauró es una esperanza, no un
  backup.
- El backup **incluye las imágenes**, no solo la base.
- El trabajo corre en la nube (cron gratuito), no en tu máquina: **nada encendido en tu casa**.

### Lo que el runtime serverless impone al diseño

- **La compresión de imágenes en el navegador (D-10) deja de ser comodidad y pasa a ser
  estructural:** es lo que mantiene el consumo dentro del plan gratuito.
- **Pooling de conexiones**, porque las funciones serverless abren y cierran conexiones todo el
  tiempo.
- **Consultas chicas.** Los límites gratuitos de CPU castigan los reportes pesados: se resuelven
  con consultas preparadas, no recalculando todo en cada carga.

### Stack elegido (2025-11-18)

**Python + React**, con una decisión que simplifica todo: **un solo despliegue**.

| Capa | Elección | Por qué |
|---|---|---|
| Lenguaje | **Python** | Pedido del desarrollador y el más usado en el mercado |
| API | **Django + Django REST Framework** | Autenticación, sesiones, migraciones, ORM y **un panel de administración** ya hechos. Con un solo mantenedor, "aburrido y completo" gana a "liviano y a mano" |
| Front | **React + TypeScript con Vite** | SPA. **No Next.js**: con una API Django, las funciones de servidor de Next son peso muerto y agregan un segundo runtime |
| Servido | El **build de React dentro del contenedor de Django** (WhiteNoise) | Mismo origen: **sin CORS**, sin dos deploys, una sola cosa que se rompe |
| Deploy | **Cloud Run** (nivel gratuito, escala a cero) | Corre Django como Django, sin las limitaciones de las funciones serverless |
| Base | **Neon Postgres** (endpoint con pooler) | Pooling obligatorio: contenedores que escalan abren y cierran conexiones |
| Imágenes | **Cloudflare R2** | **Obligatorio**: el disco del contenedor es efímero, no se puede guardar una foto ahí |
| CI y backup | **GitHub Actions** | Build, deploy y `pg_dump` nocturno hacia R2 |

**Una sola cosa que levantar, una sola que arreglar.** Django sirve el HTML, la API y las sesiones
desde el mismo origen. Eso elimina CORS, tokens entre servicios y la mitad de los errores de
integración que suelen consumir más tiempo que la lógica de negocio.

`[a confirmar]` Cloud Run pide una cuenta de facturación con tarjeta, aunque el consumo se mantenga
en el nivel gratuito (2 millones de requests por mes). No hay costo, sí hay registro. Si no querés
dar una tarjeta, el plan B es Render gratuito con el mismo código, aceptando que **se duerme a los
15 minutos** y que la primera venta del día tarda 30–50 segundos en responder.

**Costo aceptado: cold start.** La primera petición del día tarda 2–4 segundos (contenedor que
arranca + base que despierta). Mitigación de UX, no de infraestructura: la pantalla de login es
estática y carga al instante, así que mientras el operador escribe la contraseña la API se está
despertando. El costo se esconde dentro de un paso que ya existía.

**Riesgo asumido con React.** El front de esta aplicación son formularios y listas, usados en un
celular. React lo resuelve bien, pero la complejidad no está en la librería: está en el andamiaje
(build, router, estado, tipado). Con un solo mantenedor, la regla es **React sin adornos**: Vite,
`react-router`, formularios controlados y `fetch`. Sin librería de estado global, sin
generación de clientes, sin capas de caché. Si una pantalla necesita estado global, es síntoma de
una pantalla mal partida.

---

## D-03 · Usuarios, roles y sesión

**Dos roles**, no seis (A24):

| | `admin` | `operador` |
|---|---|---|
| Cargar entrada, venta, entrega, devolución, carga inicial | sí | sí |
| Ver stock y clientes | sí | sí |
| Cambiar parámetros, precios y usuarios | sí | no |
| Habilitar cuenta corriente y ajustar saldos | sí | no |

**Sesión persistente de 90 días, renovable, por dispositivo.** Login con identificador corto
(`diego`, `norberto`) y contraseña de 8 caracteres mínimo, sin reglas de mayúsculas ni símbolos:
la longitud protege más que la complejidad y la complejidad es lo que hace que compartan la cuenta.
Bloqueo de un minuto tras cinco intentos fallidos.

**Sin recuperación por email.** No hay casillas de empleados y agregar un servicio de correo es una
dependencia nueva para un solo mantenedor. La contraseña la resetea el `admin`.

**Un usuario nunca se borra:** `activo = false` (A26). Cada movimiento guarda `usuario_id`, así que
un usuario eliminado dejaría la historia huérfana.

**Consecuencia de diseño:** si el login molesta, la gente comparte la cuenta y la trazabilidad
muere (A25). Por eso la sesión dura 90 días y no hay pasos intermedios entre dos ventas.

---

## D-04 · El nombre del producto se deriva, no se escribe

El riesgo número uno del MVP es que el mismo sillón quede cargado dos veces (A19, O62). La única
forma de que eso no dependa de la memoria del operador es **no dejar que escriba el nombre**:

```
producto = categoría + tipo + color + alto × ancho × largo (+ modelo opcional)
nombre_visible = "Sillón 3 cuerpos · gris · 180×90×85"     ← derivado
id_visible     = "MUE-0007"                                 ← autogenerado
```

**Por qué.** "Sillón gris 180" y "Sillon Gris 1.80" son el mismo artículo y ninguna búsqueda los va
a unir si el nombre es texto libre. Derivándolo, la duplicación por tipeo desaparece **por
construcción**, no por disciplina.

**Reglas de captura:**

- **Color desde lista**, nunca texto libre. Un color escrito a mano genera tres variantes.
- **Medidas numéricas en cm**, sin unidades en el texto.
- **Tipo desde lista por categoría** (la lista arranca por categoría y crece con altas del `admin`).
- Texto libre solo para `modelo` y observaciones, que son opcionales.

**Al crear un producto**, antes de guardar:

1. Se busca por categoría + tipo y se muestran los existentes **con foto** (A30: la foto es lo que
   distingue dos parecidos).
2. Si los atributos coinciden exactamente, el sistema **no crea**: ofrece sumar cantidad al
   producto existente.
3. Si el operador insiste en crear uno parecido, queda registrado quién lo hizo y cuándo.

---

## D-05 · El saldo se deriva, igual que el stock

La cuenta corriente **no guarda un saldo**. Guarda movimientos:

| Movimiento | Efecto |
|---|---|
| Cargo por venta en cuotas | + |
| Pago de cuota | − |
| Ajuste por devolución | − |
| Ajuste manual del `admin` | ± (con motivo obligatorio) |

El saldo es la suma. **Es la misma decisión que A1 aplicada al dinero:** si el saldo se edita, no
hay forma de responder por qué un cliente debe lo que debe.

**Plan de cuotas:** por defecto 3 (al retirar, 30 y 60 días), con el porcentaje y los días como
parámetros si se necesitan variantes.

**Impago (S29).** Una cuota vencida pone al cliente en la lista **"a notificar"** que mira el
`admin`. No hay envío automático: no hay canal de mensajería en el MVP.

**Habilitación.** Solo clientes marcados como habilitados pueden comprar en cuotas. La
habilitación es del `admin`, porque es riesgo de crédito del negocio, no del sistema.

---

## D-06 · El precio se congela en la línea de la venta

El producto **no tiene precio**. El precio de venta se calcula:

```
precio_venta = precio_lista_proveedor_vigente × (1 + margen_categoria_vigente)
```

**Cada línea de venta guarda el precio unitario aplicado.** Ese número no se recalcula nunca más.

**Por qué.** Las listas de fábrica llegan sin calendario conocido (S38) y el margen cambia (S32).
Si el precio se recalculara al mostrarlo, el importe de una venta de hace tres meses cambiaría
solo. Congelarlo en la línea es lo que permite que el histórico diga la verdad.

**Consecuencia:** no existe "actualización de precios programada". Existe una lista nueva con una
fecha, y desde esa fecha el cálculo da otro número.

---

## D-07 · Una sola cuenta de stock, y la carga inicial es una entrada

**No hay doble registro de "disponible" y "físico".** El stock es uno.

- **La venta descuenta stock en el acto.** Lo vendido ya no es vendible, aunque siga en el depósito
  hasta el jueves. No hay reserva (A3 retirada).
- **La entrega es un evento logístico, no un movimiento de stock.** Marca la línea de venta como
  entregada y la saca de la cola de reparto (A11).
- **Carga progresiva (A27):** declarar lo que hay es una entrada con motivo `inventario_inicial`,
  de a lotes, cuando se puede. **No hay campaña de conteo ni pantalla de conteo cerrado.**
- **Diferencia encontrada** → movimiento de `ajuste`, con motivo y autor (A28: auditar es consultar
  después, no migrar).

**Consecuencia operativa para el conteo:** un artículo **vendido y no entregado está físicamente en
el depósito**. Si la lista de conteo no lo marca, el que cuenta encuentra mercadería "de más" y
desconfía del sistema. La lista de conteo muestra esas unidades como *vendidas, pendientes de
entrega*.

---

## D-08 · Movimientos: el registro único del que todo se deriva

Todo lo que cambia el stock es una fila en `movimiento`, inmutable (A1):

| Tipo | Cuándo | Descuenta stock |
|---|---|---|
| `entrada_compra` | llega mercadería | − (suma) |
| `entrada_inventario_inicial` | carga progresiva de lo que ya había | − (suma) |
| `armado` | Diego arma una caja | convierte *en caja* en *armado*, no cambia cantidad |
| `venta` | en el mostrador | sí |
| `devolucion_cliente` | vuelve un artículo | suma, si vuelve en condiciones |
| `devolucion_proveedor` | sale dañado o fallado | resta del stock propio, queda pendiente de proveedor |
| `ajuste` | diferencia de conteo | sí, con motivo obligatorio |
| `transferencia` | mueve entre ubicaciones | no cambia el total |

Campos mínimos: producto, cantidad, fecha/hora, `usuario_id`, tipo, motivo (cuando corresponde),
ubicación (opcional: **la ubicación nunca es obligatoria**, A15), y la referencia a la venta o al
proveedor si aplica.

**Por qué todo en un solo registro.** El conteo, el stock actual, el historial de un artículo, la
auditoría futura y los reportes son **consultas distintas sobre la misma tabla**. Agregar un tipo
de movimiento no cambia el modelo: agrega un valor.

---

## D-09 · Lo que participó de una operación no se borra

| Entidad | Baja | Por qué |
|---|---|---|
| Producto | `activo = false` (A29) | Conserva el historial de ventas |
| Usuario | `activo = false` (A26) | Los movimientos conservan su autor |
| Cliente | `activo = false` | Conserva deuda y compras |
| Parámetro / precio | nunca se borra: se agrega con vigencia (D-01, D-06) | La historia no se reescribe |
| Movimiento | **nunca** | Es la fuente de verdad |

**Reactivación:** si vuelve a entrar mercadería de un producto inactivo, **se reactiva el mismo
registro**, no se crea uno nuevo. Si no, el historial se parte en dos — el mismo problema que D-04.

---

## D-10 · Imágenes: parte del producto, subidas desde el celular

- 1 foto principal + adicionales por producto (S45).
- Subida desde el celular con la cámara directa.
- **Se comprime en el navegador antes de subir.** Una foto de 4 MB en 4G tarda, falla y hace que
  el operador abandone la carga; el objetivo de A13 es que capturar no cueste.
- Archivo en disco (o almacenamiento del proveedor si es PaaS), ruta en la base. Los blobs no van
  en la base: complican el backup y no aportan nada.
- `[abierto]` El backup tiene que incluir las imágenes, no solo la base. Si el despliegue elegido
  en D-02 no lo garantiza, se resuelve antes de cargar la primera foto.

---

## Lo que este diseño deja afuera a propósito

- **Combos con precio agrupado** — depende de Q2. Si existen, el modelo cambia.
- **Modo "a pedido"** — depende de Q1. Hoy está negado por D11.
- **Consignación** — depende de Q3. Si existe, se agrega propiedad al stock.
- **Auditoría con vistas propias** — A28: los datos ya están, la pantalla es después.
- **Interés por mora** — no definido. Si aparece, es un parámetro nuevo, no un rediseño.
- **Stock por ubicación como requisito** — A15: primero contar, ubicar después.

## Riesgos de este diseño

- **Dato (ítem 1):** un movimiento mal registrado no se corrige editando; se corrige con un
  movimiento de ajuste. Es más incómodo a propósito.
- **Seguridad (ítem 2):** credenciales, sesiones de 90 días y una sola base. Sin HTTPS y sin
  backup probado, esto es el punto más frágil del sistema.
- **Contratos (ítem 3):** los parámetros con vigencia y el nombre derivado son decisiones difíciles
  de revertir después de cargar datos reales. Confirmarlas antes de la primera carga.
