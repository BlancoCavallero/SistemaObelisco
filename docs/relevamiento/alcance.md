# Sistema Obelisco — relevamiento y alcance

Sistema de gestión de stock para una empresa familiar de venta de muebles.
Estado: **captura de relevamiento en curso**. Sin implementación. Sin código.
El alcance se cierra por escrito y se valida con el negocio antes de la primera línea.

Fuente primaria: `bitacora.md` (lo que dice el cliente, literal). Este documento es la
síntesis: no afirma nada que no esté en la bitácora o confirmado por escrito en el repo.

## Specs

**S1 — Necesidad primaria.** "necesitan principalmente un buen sistema de stock".
El stock es el núcleo del sistema. Ventas, compras y entregas existen para moverlo.

**S2 — Horizonte de expansión.** "posteriormente ampliable a venta online y otros rubros".
Es una restricción de diseño de largo plazo, no alcance del MVP.
Consecuencia a validar: catálogo por atributos genéricos (no modelos fijos por rubro)
y precios/inventario desacoplados del canal de venta.

**S3 — Secuencia de trabajo.** "primero quiero hacer todo el relevamiento del alcance".
No se escribe código hasta que el alcance esté consolidado y validado con el negocio.

**S4 — Rubro.** "el rubro de venta de muebles".
Implica variantes por material/color/medida, unidades de venta mixtas (unidad vs m²/m)
y posible fabricación a medida. **Sin confirmar** (ver R1).

**S5 — Puntos de venta.** "Un local con depósito propio".
Un solo nodo comercial; salón y depósito comparten domicilio. El stock del salón está
a la vista y probablemente sea vendible: el salón es depósito, no una muestra (H2).

**S6 — Facturación.** "Necesitamos factura electrónica".
Emitir comprobantes AFIP/ARCA desde el sistema es requisito, no opcional. Pasa a estar
**dentro del alcance** y arrastra: condición fiscal del emisor, tipos de comprobante,
notas de crédito, remitos, precios con IVA y contingencia si el organismo está caído (H3–H9).

**S7 — Dolor principal.** "no hay sistema y todo tarda mucho".
No hay sistema previo: no hay datos históricos que migrar, pero tampoco procesos digitales
que preservar. La métrica de éxito del MVP es tiempo: cotizar y encontrar stock rápido,
no solo "tener stock".

`[pendiente]` S8..Sn: se numeran a medida que el negocio responde (ver Tasks R1–R6).

## Tasks

| ID | Tarea | Specs |
|----|-------|-------|
| R1 | Operación, estructura física, facturación y dolor principal | S1, S3 |
| R2 | Catálogo: modelo de producto, variantes, combos, medidas | S4 |
| R3 | Dinámica de stock: entradas, salidas, reservas, estados, tomas | S1 |
| R4 | Circuito de venta: presupuesto → seña → entrega, pagos, cambios | S1 |
| R5 | Compras, proveedores, costos y moneda | S1 |
| R6 | No funcionales: usuarios/roles, auditoría, hardware, hosting, presupuesto | S1, S2 |
| R7 | Consolidar documento de alcance + MVP + roadmap de expansión | S1, S2, S3 |
| R8 | Validar el alcance con el negocio (checklist firmable) | S3 |

## Decisiones del cliente

Decididas por el negocio, no por nosotros. Se registran con su razón declarada y su riesgo.

**D1 — Se construye de cero. (2025-11-18)**
"el sistema anterior no nos importa a nosotros, lo vamos a hacer de 0, con stock y todo".
No se integra, no se migra y no se audita el sistema anterior.

| Gana | Pierde |
|---|---|
| Sin migración de datos | Nada impide repetir la causa del fracaso |
| Sin compatibilidad con lo heredado | Se paga de nuevo lo que ya estaba pago |
| Sin hábitos que desaprender | El tiempo disponible sigue siendo el mismo |

**Riesgo asociado: R12.** El sistema anterior murió por falta de tiempo, no por falta de
funciones. La decisión de construir de cero es legítima; **ignorar por qué murió el anterior
no lo es.**

**D2 — Facturación fuera del alcance. (2025-11-18, decidido por el desarrollador)**
"la facturacion dejala de lado por ahora, no nos interesara, solo haremos una factura o una
lista con los datos necesarios para entregarselo al responzable o los contadores".

- El sistema **no emite comprobantes fiscales** ni se integra con AFIP/ARCA.
- Produce un **documento imprimible** con los datos de la operación para que el responsable
  o el contador emitan el comprobante real.
- Efecto inmediato: cae gran parte del riesgo regulatorio y **O12 deja de aplicar** (qué
  evento dispara la factura ya no lo decide el sistema).
- **Advertencia registrada:** si ese documento se entrega al cliente con el nombre "factura"
  sin CAE, no es un comprobante válido. La diferencia entre *lista interna para el contador* y
  *comprobante para el cliente* tiene que quedar clara antes de construir la impresión.
- **Contradicción con S6, resuelta en el roadmap (bloque 9):** el cliente dijo "Necesitamos
  factura electrónica" y el desarrollador dijo "no nos interesará". No son incompatibles si se
  leen como fases: **fase 1** proveer los medios para facturar de forma sencilla; **fase 2**
  integración de factura electrónica. S6 pasa de *reemplazada* a **diferida**.

**D3 — No se dimensiona por volumen de ventas. (2025-11-18)**
"no puedo decir cuantas ventas hay y no creo que nos deberia interesar". Se retira la pregunta.
El orden de magnitud del inventario sale del conteo; el volumen de ventas lo produce el
sistema cuando esté en uso.

**D4 — Volumetría fuera de alcance. (2025-11-18)**
"en cuanto al volumen no es algo que nos interese". No se calcula volumen en m³ ni capacidad
de carga por volumen. Consecuencia aceptada: la capacidad de la combi se estima por cantidad
de bultos. Las medidas (alto/ancho/largo) se guardan como atributo descriptivo del artículo,
no como input de cálculo.

**D5 — No hay techo de tiempo declarado. (2025-11-18)**
"Asumiremos que le dedicaran lo que haga falta". Se acepta. La regla A13 (cero rituales
nuevos) **sigue vigente igual**: el diseño no se relaja porque el negocio prometa tiempo.
Mitigación acordada: el sistema registra cuánto tarda cada carga y a los 30 días se revisa el
número real. Es la única respuesta que contradice la evidencia (O34, O66); por eso se mide.

**D6 — El documento es interno. (2025-11-18)**
"el documento es para el personal o el contador". No se entrega al cliente, **no es comprobante
fiscal y no necesita CAE**. El riesgo regulatorio del proyecto queda en cero. Si algún día se
entrega al cliente, cambia de naturaleza y hay que rediscutirlo.

**D7 — Sin restricción de presupuesto declarada. (2025-11-18)**
"infinito". Se interpreta como "no hay tope definido", no como "gastar sin criterio". El plazo
sigue sin definir.

**D8 — Mantenimiento a cargo del desarrollador. (2025-11-18)**
"yo". Hay un solo mantenedor, sin equipo detrás. Restricción de arquitectura: stack aburrido,
un despliegue simple, dependencias mínimas (A22).

**D9 — El sistema reemplaza el papel. (2025-11-18)**
"la idea es que el sistema reemplace el papel". **Una sola fuente de verdad**: no hay carpeta
paralela, no hay doble registro. Responde P34 y elimina el riesgo de los dos registros.

**D10 — Proyecto propio, sin plazo ni presupuesto externo. (2025-11-18)**
"el proyecto es propio asi que puedo tardar lo que quiera y el presupuesto es el que yo quiera,
el alcance tambien es para mi y el futuro desarrollo". No hay cliente esperando entrega ni fecha
comprometida. El alcance lo decide el desarrollador. **Riesgo asociado: R15.**

**D11 — No hay pedidos por encargo. (2025-11-18)**
"p12. no". No se pide un mueble en una tela o color que no está: se vende lo que hay en stock.
Sin plazos de entrega por pedido y sin reserva de fábrica. *Tensión abierta con P11 (placares y
cocinas a medida): si no hay encargos, esos artículos están en stock o son una excepción. Ver O86.*

## Decisiones de arquitectura a validar

Hipótesis iniciales. No se comprometen hasta cerrar el relevamiento.

**A1 — El stock no se edita: se registra.** Cada movimiento (ingreso, salida, reserva,
ajuste, transferencia, devolución) es un asiento inmutable con fecha, usuario y motivo.
El saldo es derivado y recalculable. Sin esto no hay auditoría ni toma de inventario
confiable. Consecuencia directa: `UPDATE stock = X` queda prohibido desde el día uno.

**A2 — Producto ≠ SKU.** El producto es el modelo ("Sillón Nórdico"); el SKU es la
combinación concreta de atributos (tela, color, patas). En muebles la explosión
combinatoria es real: 10 modelos × 5 telas × 4 colores = 200 SKUs de un solo living.
Hay que decidir qué combinaciones se stockean y cuáles son pedido a medida.

> **Confirmado (bloque 8):** los atributos que el negocio quiere son **categoría** (electrónico,
> mueble, decoración…), **tipo de artículo**, **color** y **alto/ancho/largo**. No hay cantidad
> de artículos definida: el catálogo **crece por recepción**, no por alta previa.
> Las medidas se guardan como dato descriptivo. **No se calcula volumen (D4).**

> **Hueco H13:** falta el discriminante que distingue dos artículos con igual categoría, tipo,
> color y medidas (modelo, nombre comercial o proveedor). Sin eso, la identidad del artículo
> queda incompleta.

**A3 — RETIRADA. No hay reserva ni seña.** Hipótesis inicial erronea: se propuso "reservado"
como estado de primera clase, y el negocio no reserva nada. No existe la seña; un artículo
está vendido o no está vendido. Lo que sí existe es la **venta en cuotas** (financiación
propia), que no reserva: el artículo sale y la deuda queda. Menos estados = menos lugares
donde el dato puede mentir.

**A4 — Monolito modular, no microservicios.** Un despliegue, módulos de dominio
separados (catálogo, stock, ventas, compras, fiscal) comunicados por interfaces
internas. La expansión a e-commerce es una API + un canal de venta nuevo, no un
reescribir.

**A5 — Precios y costos tienen vigencia, no son columnas.** Un producto cambia de
precio N veces por año y el costo puede variar por lote o por moneda. Un precio sin
fecha de vigencia hace impredecible la facturación pasada.

**A6 — Integración fiscal (AFIP/ARCA), confirmada como requisito.** Condiciona el circuito
de venta completo y es el ítem regulatorio más caro del proyecto. No se resuelve con
"agregar un botón de facturar" al final: define tipos de comprobante, precios con IVA,
notas de crédito y puntos de venta habilitados.

**A7 — Facturar no mueve stock; entregar sí.** Con factura electrónica y entrega diferida
(30–45 días es normal en muebles), el comprobante y el movimiento físico son dos eventos
distintos. Facturar crea la obligación fiscal y la reserva; la salida de stock ocurre en el
remito/entrega. Mezclarlos produce stock negativo o stock inventado, los dos síntomas
clásicos de un sistema de stock en el que nadie confía.

**A8 — Sin precio no hay venta.** El negocio lo declara como regla: "No se vende hasta que no
tengamos el precio en la carpeta". El sistema la hace cumplir **bloqueando**, no advirtiendo.
Un precio provisorio en la operación destruye la trazabilidad del margen (A5).

**A9 — La cuenta corriente es crédito propio, no un medio de pago.** Tres vencimientos
fijos (retiro, 30 y 60 días) otorgados por confianza. Es riesgo de cobranza del negocio:
necesita estado de cuenta por cliente, vencimientos, mora y remito firmado como evidencia.
Un procesador de pagos no cubre esto y no se debe modelar como si lo hiciera.

**A10 — Lo que se cobra no es flete, es armado.** El reparto en la zona es sin cargo; el
6–7% remunera el armado y viaja junto al producto. Son dos conceptos separados: el viaje es
un costo absorbido por el margen del producto, el armado es un servicio facturable. Si se
modelan juntos, el margen por rubro miente y el costo logístico desaparece.

**A11 — La entrega es una cola, no una fecha libre.** Rutas fijas por localidad con mínimo
de 3 o 4 pedidos por viaje. El sistema no calcula una fecha de entrega: **acumula pedidos por
zona hasta que la próxima ruta se justifica** y le promete al cliente esa fecha. Prometer
plazos por pedido individual es prometer algo que la operación no hace.

**A12 — Un producto tiene estado físico, no solo cantidad.** La mayoría de los muebles llega
**desarmado en caja**. El mismo artículo existe como *en caja* (no exhibible) y como *armado*
(exhibible y vendible). El armado es un movimiento de inventario con responsable (Diego), y
un placard vendido se arma **en la casa del cliente**, que es un servicio facturable distinto.
Sin este estado, el sistema va a decir "hay 8" cuando en realidad hay 8 cajas que nadie abrió
y no se pueden entregar hoy.

**A13 — Cero rituales nuevos.** El sistema anterior murió porque exigía una tarea que nadie
podía sostener (D1, R12). La regla de diseño que se desprende no es una preferencia, es una
condición de supervivencia: **todo movimiento de stock tiene que ser un subproducto de algo
que ya ocurre** — abrir la mercadería que llegó, armar el mueble, vender, entregar, cobrar.
Si un movimiento requiere "acordarse de actualizar el stock", ese movimiento no se va a
registrar. El sistema no agrega tareas: se cuelga de las que ya existen.

**A14 — La ubicación es una dimensión, pero el número no lleva la categoría adentro.**
Hay almacén → sector → posición, y se numera desde ahora para reorganizar sin renumerar
(bloque 9). **Pero si el código del sector contiene la categoría**, el número miente el día que
una categoría cambie de sector, y hay que renumerar exactamente lo que se quería evitar.
La categoría es una **asignación de datos** sobre la posición, no su significado.
Además: soportar **N almacenes** desde el inicio (el cliente dijo "el/los almacenes"), aunque
hoy haya uno.

**A15 — La ubicación no puede ser requisito para contar.** El cliente habla de cuando "tengan
los muebles organizados": hoy el depósito no lo está. Si el conteo exige asignar sector a cada
artículo, el conteo no se hace y el MVP se cae. **Primero contar, después ubicar.**

**A16 — El cliente es una entidad, y su ciudad es la clave de ruteo.** Nombre, ciudad,
dirección y cuenta corriente. La ciudad conecta el padrón de clientes con las rutas fijas por
localidad (A11) y con el armado en destino. Una venta sin ciudad no tiene fecha de entrega ni
precio de armado.

**A17 — El armado es una opción de compra, no un proceso interno.** El cliente elige: se lo
lleva en caja, o pide armado (6–7%). Esa elección cambia tres cosas a la vez: el precio, el
estado del artículo y quién lo entrega. Tiene que ser una decisión explícita registrada en la
venta, no un atributo deducible.

**A18 — Una devolución es un movimiento con estado, no un borrado.** El artículo vuelve al
stock solo si está en condiciones; se registra cómo vuelve. Si la venta fue en cuenta
corriente, el saldo se ajusta en el mismo acto. Una devolución que borra la venta destruye la
trazabilidad y deja la cuenta corriente inconsistente.

**A19 — Se cuenta por producto, no por pieza.** No hay número de serie: dos artículos iguales
son el mismo registro y solo importa cuántos hay. Consecuencia: el riesgo principal del
catálogo deja de ser la ambigüedad y pasa a ser **la duplicación**. Si el mismo sillón se crea
dos veces ("Sillón gris 180" / "Sillon Gris 1.80"), el stock se parte en dos y la suma real
se vuelve invisible. **La carga tiene que empezar buscando si el producto ya existe**, no
creando uno nuevo por reflejo. Es el punto más frágil del MVP.

**A20 — No hay responsables fijos, pero sí hay que saber quién tocó qué.** Abre y cierra el
local el primero que llega: no existen turnos, así que el sistema no puede pedir "usuario del
turno". Precisamente por eso cada movimiento necesita autor registrado — cuando no hay
proceso que controle, la trazabilidad es lo único que queda.

**A21 — Parámetros configurables: lista cerrada, no "todo configurable".** El negocio pidió
cuatro cosas modificables (margen por rubro, % descuento por efectivo, % de armado, plazo de
devolución) y una lista abierta de localidades. Exactamente esas cinco se configuran, con
defaults y con cambio auditable. **Todo lo demás queda en código.** "Configurable" es la
palabra más peligrosa de un requerimiento: si cualquier regla es un parámetro, el sistema deja
de tener reglas y cada cambio hay que probarlo a mano.

**A22 — Un solo mantenedor, stack aburrido.** El que escribe el sistema también lo mantiene
(D8), sin equipo. Eso descarta infraestructura exótica, servicios administrados propios y
cualquier pieza que el autor no pueda diagnosticar solo dentro de dos años.

**A23 — Un equipo y celulares personales.** Una PC en el local y los teléfonos de los
empleados como equipos de operación (S33). El sistema es web y tiene que funcionar en un
celular, con la misma cuenta por persona que el resto (A20). No hay app nativa ni hardware
especial.

**A24 — Roles por permiso, nunca por persona.** Hay seis personas y alcanzan **dos roles**:
administración (parámetros, usuarios, cobranza) y operación (cargar movimientos, vender,
contar). Un rol por empleado es una lista de nombres disfrazada de sistema de permisos, y se
mantiene para siempre.

**A25 — La sesión tiene que ser barata o la auditoría muere.** La trazabilidad exige saber
quién hizo cada movimiento (A20), y el login por persona es fricción (O76). Si entrar cuesta,
comparten una cuenta y no hay autor. Consecuencia: sesión persistente por dispositivo, entrada
en pocos segundos, y ningún paso de login entre dos ventas seguidas.

**A26 — Un usuario no se borra, se desactiva.** Los movimientos quedan con su autor: borrar el
usuario deja la historia huérfana o se lleva los registros con él. Contraseñas con hash, nunca
en texto plano (O79).

**A27 — No hay "conteo inicial": hay carga progresiva.** "contamos todo y de manera progresiva"
(S41). Declarar lo que hay es una **entrada sin compra** (motivo: inventario inicial), y se hace
de a poco, cuando se puede. No existe una campaña de conteo que bloquee el arranque.

**A28 — La auditoría es una vista, no un modelo nuevo.** Si los movimientos son inmutables (A1),
"en el futuro se deberá poder auditar" (S46) se cumple **consultando**, sin migrar nada. Si el
ajuste de una diferencia editara el saldo, la auditoría futura sería imposible sin reescribir
el histórico. La decisión de hoy es lo que hace posible la función de mañana.

**A29 — Un artículo no se borra: se oculta, y el historial queda.** "el articulo se oculta, para
guardar historico de ventas" (S50). Es el mismo principio que A26 con los usuarios: lo que
participó de una operación no desaparece.

**A30 — La imagen es parte del producto.** Fotos de productos, colores y tamaños (S45), subidas
desde el celular (A23). No es decoración: es lo que reemplaza al papel cuando hay que reconocer
un artículo entre dos parecidos.

## Riesgos tempranos

- **Riesgo 1 — Alcance.** "Muebles" y "otros rubros" pueden implicar modelos de catálogo
  incompatibles. Si el catálogo se diseña solo para muebles, la expansión obliga a migrar
  datos. Mitigación: atributos genéricos desde el inicio (A2).
- **Riesgo 2 — Datos.** El stock inicial hay que cargarlo y conciliar contra un conteo
  físico. La migración desde Excel/papel suele ser el mayor esfuerzo oculto del proyecto.
- **Riesgo 3 — Operativo.** Si el sistema exige más disciplina que la que el local sostiene
  hoy, el stock sigue sin coincidir aunque el software esté bien. Hay que relevar la
  operación real, no la ideal.
- **Riesgo 4 — Legal.** Facturación electrónica, datos personales de clientes (Ley 25.326)
  y conservación de comprobantes.
- **Riesgo 5 — Cumplimiento del flujo actual.** Hoy el comprobante se emite al terminar de
  pagar, no al vender. Ese flujo no es replicable en un sistema con factura electrónica sin
  exponer al negocio. **Decisión del cliente con su contador, antes del MVP**: define qué
  evento dispara la factura (venta, entrega o último pago).
- **Riesgo 6 — Conciliación.** Existía egreso de mercadería fuera del circuito documentado
  (C1). El cliente declaró que **todo lo que entra y sale del depósito se registra** (S26), así
  que la conciliación **es posible**. El riesgo cambia de naturaleza: ya no es falta de
  información, es **sostenibilidad de la política**. Si un día se deja de registrar, la
  diferencia aparece y el sistema queda marcado como no confiable. Mitigación: conteos
  periódicos y el criterio de éxito declarado en palabras del cliente (S8).
- **Riesgo 7 — Información sensible del cliente.** Este repositorio se versiona y puede
  compartirse. No se transcriben acá hechos que expongan al cliente ante un tercero: se
  registra la consecuencia de ingeniería, nunca el hecho ni su detalle.
- **Riesgo 8 — Margen inflado por costo logístico invisible.** El reparto en cinco
  localidades es gratis para el cliente y se paga con combustible, tiempo y desgaste. Si ese
  costo no se imputa a los productos, el margen por rubro que ya hoy se estima a ojo (O4) se
  va a reportar todavía más alto de lo real, y las decisiones de precio se van a tomar sobre
  un número falso.
- **Riesgo 9 — Promesa de entrega.** Es fácil prometer "te lo llevamos" al vender; el
  sistema tiene que mostrar la próxima ruta real por localidad y no un plazo genérico. Una
  entrega incumplida cuesta más que un precio mal puesto.
- **Riesgo 10 — Nadie es dueño del dato de stock.** Seis roles declarados y ninguno tiene
  asignada la carga del inventario. Esta es la causa raíz de que hoy el dueño no sepa cuánta
  mercadería tiene. **Es el riesgo número uno del proyecto y no se resuelve con software:**
  si no hay una persona responsable de cargar y conciliar, el sistema queda perfecto y vacío.
  Antes del MVP hay que definir nombre, momento del día y alcance de esa carga.
- **Riesgo 11 — El sistema anterior ya falló una vez.** No por funcionalidad: "nunca lo
  implementaron por falta de tiempo" (D1). Ese fracaso no se resuelve cambiando de software.
  **Antes de escribir código hay que nombrar quién carga, cuándo y en cuántos minutos.**
  Ver A13.
- **Riesgo 12 — El sistema nuevo compite contra el mismo déficit de tiempo.** Seis personas en
  un mostrador, compras a la noche, un solo local. Si el sistema pide un ritual diario que no
  entra en ese día, se abandona igual que el anterior, y esta vez es nuestro código el que
  queda sin usar. **El éxito se mide en adopción sostenida, no en funcionalidades entregadas.**
- **Riesgo 13 — Devoluciones sin política.** El cliente acepta que existen, pero no definió
  cuándo corresponde. El sistema puede registrar; no puede decidir. Sin un criterio escrito
  (plazo, condición, con o sin caja), cada devolución es una negociación y los datos de
  devolución no sirven para sacar ninguna conclusión. Ver O57.
  *Actualización: el plazo quedó en 15 días configurables (S28). Falta la condición del artículo.*
- **Riesgo 14 — Superficie de seguridad nueva.** Con usuarios reales aparecen contraseñas,
  sesiones, recuperación y permisos. Es la primera pieza del proyecto que cae en el ítem 2 del
  criterio de riesgo (credenciales y controles de acceso). Un usuario dado de baja que sigue
  entrando, o una contraseña en texto plano, son fallas graves de un sistema que hoy no las
  tiene porque no tiene usuarios.
- **Riesgo 15 — El proyecto no tiene final.** "puedo tardar lo que quiera y el presupuesto es el
  que yo quiera" (D10). El riesgo dejó de ser la falta de tiempo y pasó a ser **no terminar
  nunca**: un proyecto propio, sin cliente ni fecha, no muere de apuro — muere de perfeccionismo
  y de alcance que crece sin freno. Mitigación: el MVP de `mvp.md` es un corte concreto y
  entregable; antes de sumar la primera función nueva, el MVP tiene que estar en uso diario.

## Fuera de alcance (borrador, a confirmar)

- Venta online transaccional. Solo se prepara la arquitectura; no está en el MVP.
- Fabricación propia y costeo de producción, si no hay taller (pendiente R1).

## Huecos a llenar con el cliente

Las hipótesis **no son requisitos** hasta que el cliente las confirme. Sirven para que la
entrevista sea de confirmación y no de descubrimiento: se le propone y él corrige.

| # | Hueco | Hipótesis por defecto | Se confirma en |
|---|-------|----------------------|----------------|
| H1 | Origen del producto: reventa, taller propio o a medida | Reventa de terminados + pedidos a medida tercerizados | R1, pregunta 1 |
| H2 | El mueble en exhibición, ¿es vendible? | Sí: el salón es stock vendible, se marca "exhibición" y se repone | R1, pregunta 4 |
| H3 | Condición fiscal del emisor | Responsable Inscripto con IVA 21% | R1 + contador |
| H4 | Comprobante por tipo de cliente | Factura B a consumidor final, A a empresas | R4 + contador |
| H5 | Remito de entrega | Necesario: la entrega es diferida respecto de la venta (A7) | R4 |
| H6 | Notas de crédito | Necesarias para cambios y devoluciones | R4 |
| H7 | Contingencia con AFIP caído | Emisión diferida con reintento; nunca bloquear la venta | R4 + contador |
| H8 | Precios de salón con IVA incluido | Sí (retail); el IVA se discrimina solo en el comprobante | R1, pregunta 2 |
| H9 | Certificado WSAA y puntos de venta | Los gestiona el negocio; el sistema solo los consume | Contador |
| H10 | Unidad de venta | Unidad para muebles; m²/metro si hay tapicería o telas por metro | R2 |
| H11 | Cantidad de usuarios | 1 a 3 simultáneos; roles dueño / vendedor / depósito | R1, pregunta 3 |
| H12 | Número de serie por pieza | No hay hoy; se agrega solo si hay garantías formales que lo exijan | R2 |

## Guía de entrevista (EN PAUSA)

> Las preguntas no se emiten de a una: se entrega un solo lote al cerrar la captura de la
> bitácora. Esta sección queda como material de trabajo, no como tarea activa.

**Cerrar R1 — operación y gente**

1. ¿De dónde sale el mueble que venden: lo compran hecho, lo fabrican, o lo mandan a hacer
   a medida? Si fabrican: ¿taller propio? ¿guardan madera, telas, herrajes?
2. ¿Quién factura hoy y con qué condición fiscal? ¿Los precios del salón ya incluyen IVA?
3. ¿Cuántas personas trabajan en el local y en el depósito? ¿Quién atiende, quién cobra,
   quién prepara la entrega?
4. El mueble que está en el salón, ¿se vende o es solo muestra? Si se vende, ¿qué ponen en
   su lugar?

**R2 — catálogo**

5. ¿Cuántos modelos distintos manejan? ¿Y cuántas variantes de tela, color o patas por modelo?
6. ¿Venden juegos o combos (living de 3 cuerpos)? ¿El precio es del juego o por pieza?
7. ¿Hay productos a medida del cliente? ¿Quién pone el precio y con qué criterio?
8. ¿Necesitan saber *qué pieza* entregaron? (número de serie, para garantía o reclamo)
9. ¿Venden algo que no sea mueble: bazar, decoración, colchones, alfombras?

**Números — los que definen el tamaño real**

10. ¿Cuántas ventas por mes? ¿Ticket promedio? ¿Cuántos artículos distintos hay hoy en depósito?
11. ¿Cada cuánto cuentan el stock a mano? ¿Quién lo hace y cuánto tarda?
12. ¿Cuántos proveedores tienen? ¿Reponen seguido? ¿Compran en pesos o en dólares?

## Log

**L1 — Pedido original (verbatim), 2025-11-18:**
"este proyecto arranca de 0, sistema obelisco es una empresa familiar que se enecarga del rubro de venta de muebles y necesitan principalmente un buen sistema de stock, posteriormente ampliable a venta online y otros rubros, primero quiero hacer todo el relevamiento del alcance"

**L2 — Ronda 1 de preguntas enviada:** operación, estructura física, facturación, dolor principal.

**L3 — Respuestas de la ronda 1 (entrevista en curso con el cliente), verbatim:**

- Operación: "ahora estoy en entrevista con el cliente te voy pasando lo que me va diciendo y nosotros llenamos los huecos" → **pendiente**, se recibe por partes.
- Estructura: "Un local con depósito propio" → S5.
- Facturación: "Necesitamos factura electrónica" → S6, dentro del alcance.
- Dolor principal: "no hay sistema y todo tarda mucho" → S7.

Método acordado: el usuario transmite lo que dice el cliente y el relevamiento se completa
por huecos explícitos (sección Huecos), nunca por invención silenciosa.
