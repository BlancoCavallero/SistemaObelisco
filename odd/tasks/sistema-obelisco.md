# Sistema Obelisco — tracker ODD

Sistema de gestión de stock para una empresa familiar multi-rubro (muebles, electrodomésticos,
decoración, colchones, sillones, artículos de verano, oficina).
Estado: **MVP implementado y desplegado** (release v0.8.0). El relevamiento está cerrado salvo
R8 (validación del negocio). Documentación: `docs/relevamiento/`.

## Specs

Citas verbatim. Detalle y contexto en `docs/relevamiento/alcance.md`.

- **S1** — "necesitan principalmente un buen sistema de stock"
- **S2** — "posteriormente ampliable a venta online y otros rubros"
- **S3** — "primero quiero hacer todo el relevamiento del alcance"
- **S4** — "el rubro de venta de muebles"
- **S5** — "Un local con depósito propio"
- **S6** — "Necesitamos factura electrónica" → **DIFERIDA a fase 2**, no descartada (ver S14, D2)
- **S7** — "no hay sistema y todo tarda mucho"
- **S8** — "Hoy me preguntas cuánta mercadería tengo en el negocio, no lo sé"
- **S9** — "ya pusimos un sistema para hacer stock y eso porque, como te decía, no tenemos"
  → el sistema anterior no se investiga (D1)
- **S10** — "La mayoría de los muebles hoy en día vienen todos desarmados en caja, entonces
  antes de venderlo o de exhibirlo hay que armarlo"
- **S11** — "nos interesan las categorias (Electronico, mueble, decoracion, etc) y el tipo de
  articulo y el color como distintivos, ademas de datos como alto,ancho,largo"
- **S12** — "cuantos articulos hay no se sabe y es el principal desafio"
- **S13** — "los empleados cargan lo que entra en el momento en que llega y lo guardan en el
  almacen o lo ponen a la venta"
- **S14** — "la facturacion dejala de lado por ahora, no nos interesara, solo haremos una
  factura o una lista con los datos necesarios para entregarselo al responzable o los
  contadores" *(reemplaza S6 — decidido por el desarrollador, confirmar con el cliente)*
- **S15** — "el mocho se llama 'Norberto'"
- **S16** — "por ahora no nos meteremos en facturacion en si, sino que proveeremos los medios
  para que ellos puedan facturar de manera sencilla, en otro momento podriamos ampliar el
  alcance a facturacion electronica"
- **S17** — "por ahora numeraremos internamente el almacen dependiendo de la categoria por si
  en el futuro quieren devidir el/los almacenes en sectores cuando tengan los muebles
  organizados"
- **S18** — "los muebles se pueden o vender o se puede solicitar armado, para el armado creo
  seria mejor guardar la ciudad y direccion del cliente"
- **S19** — "como tambien hay clientes que tienen una cuenta corriente deberiamos guardarlos"
- **S20** — "aceptaremos que es posible realizar cambios y devoluciones"
- **S21** — "el local esta en Tres lomas, provincia de buenos aires"
- **S22** — "cualquiera puede abrir y cerrar el local, el primero que llega lo hace"
- **S23** — "no hay seña para reservar a menos que se venda y se pague en cuotas las cuales
  deberiamos gestionar"
- **S24** — "les pondremos un id a los productos pero si son iguales simplemente hay stock del
  mismo producto"
- **S25** — "Asumiremos que le dedicaran lo que haga falta"
- **S26** — "si todo lo que sale o entra al deposito deberia ser registrado en la app"
- **S27** — "el documento es para el personal o el contador"
- **S28** — "aceptaremos un plazo de 15 dias modificable"
- **S29** — "clientes habilitados obtendran una cuenta corriente, si el cliente no paga se le
  notifica al personal (ampliable en el futuro cuando los usuarios puedan registrarse por si
  mismos y comprar con un carrito online)"
- **S30** — "5% de descuento en efectivo modificable"
- **S31** — "si se hace una solicitud de armado se suma al precio, tambien modificable"
- **S32** — "es variable y modificable incialmente ponle un 10% a todos" (margen por rubro)
- **S33** — "intenet estable, equipos una pc y los celulares de los empleados en caso de ser
  necesario"
- **S34** — "infinito" (presupuesto)
- **S35** — "yo" (mantenimiento)
- **S36** — "Quenuma, las localidades se pueden ampliar si se solicita"
- **S37** — "si" (un sector puede mezclar categorías)
- **S38** — "no se sabe, eso depende enteramente de la fabrica y de cada cuanto se vende"
  (cadencia de actualización de listas de precios)
- **S39** — "tambien hace falta hacer usuarios para los diferentes empleados"
- **S40** — "pienso que la app sea web"
- **S41** — "contamos todo y de manera progresiva, tanto cuando entra como cuando sale y cuando
  nosotros querramos cargar ms cosas"
- **S42** — "p12. no" (sin pedidos por encargo)
- **S43** — "no es posible saberlo. moneda en pesos y lo dañado puede devolverse a la
  fabrica/proveedor"
- **S44** — "el proyecto es propio asi que puedo tardar lo que quiera y el presupuesto es el que
  yo quiera, el alcance tambien es para mi y el futuro desarrollo"
- **S45** — "la idea es que el sistema reemplace el papel ya que tendremos imagenes de los
  productos, colores, tamaños etc"
- **S46** — "por ahora solo se arreglara en el futuro se debera poder auditar"
- **S47** — "los articulos de verano se guardan, es mas una categoria que una estacion"
- **S48** — "las garantias son del fabricante"
- **S49** — "no hay colchones a medida solo los comprados"
- **S50** — "el articulo se oculta, para guardar historico de ventas"
- **S51** — "Nosotros tenemos dos negocios. Ahora el que abrimos hace poquito, que ese lo usamos
  como exhibición, no hacemos atención al público"
- **S52** — "medimos, tomamos las medidas, hacemos un plano... se lo pasamos a la fábrica, la
  fábrica nos presupuesta... le ponemos un margen de ganancia, se lo pasamos al cliente... en 15,
  20 días nos manda los muebles hechos"
- **S53** — "no es que somos carpinteros, sino que a nosotros nos hacen una fábrica los muebles y
  nosotros después vamos y se los armamos a la casa"
- **S54** — "Vendemos juegos completos y también por separado... El precio es lo mismo"
- **S55** — "todo lo que es blanquería, todo lo que es sábanas, toallones, repasadores, acolchados,
  cover de verano... barrales, soportes para cortinas"
- **S56** — "Hacemos cortinas de blackout a medida, de la misma forma que con los muebles a medida"
- **S57** — "Deben ser entre 40 y 50 proveedores diferentes... la mayoría nos comunicamos por
  WhatsApp o por teléfono"

## Decisiones

- **D1** — Se construye de cero. El sistema anterior no se integra ni se investiga.
- **D2** — Fase 1: proveer los medios para facturar de forma sencilla (documento/lista).
  **Fase 2:** factura electrónica, como ampliación de alcance.
- **D3** — No se dimensiona por volumen de ventas.
- **D4** — Volumetría fuera de alcance: no se calcula volumen ni capacidad por m³.
- **D5** — No hay techo de tiempo declarado ("lo que haga falta"); A13 sigue vigente y el
  tiempo real de carga se mide en el sistema y se revisa a los 30 días.
- **D6** — El documento es interno (personal o contador): no requiere CAE, riesgo fiscal cero.
- **D7** — Sin restricción de presupuesto declarada ("infinito"); plazo sin definir.
- **D8** — Mantenimiento a cargo del desarrollador: stack aburrido, un despliegue simple.
- **D9** — El sistema reemplaza el papel: una sola fuente de verdad, sin carpeta paralela.
- **D10** — Proyecto propio, sin plazo ni presupuesto externo; el alcance lo decide el
  desarrollador (Riesgo 15: el proyecto puede no terminar nunca).
- **D11** — Sin pedidos de *variantes* de artículos de stock.
- **D12** — Sí hay pedidos a medida (no fabrican): medir, plano, presupuesto de fábrica, margen,
  confirmación, 15-20 días, armado o colocación. Fuera del MVP.
- **D13** — Los juegos no tienen precio propio: una venta con varias líneas.

## Tasks

Estado real contra el código, no contra el relevamiento. `Evidencia` son los commits que
sostienen el estado; sin commit, la fila es documentación o no está hecha.

| ID | Tarea | Specs | Estado | Evidencia |
|----|-------|-------|--------|-----------|
| R1 | Placares y amoblamientos de cocina: ¿se fabrican o se encargan? | S4 | respondida (D12) | `7c332cf` |
| R2 | Catálogo: categoría, tipo, color, medidas + discriminante de producto | S11 | hecho (H13 respondida) | `3e31340` `3897a57` `9ff164a` |
| R3 | Dinámica de stock: entradas, estados, toma de inventario | S1, S12 | parcial: falta el conteo | `3e12e27` `92d6f25` |
| R4 | Circuito de venta: seña, cambios, devoluciones | S1 | parcial: falta devolución | `d9cfaba` `d91ca5a` |
| R5 | Compras y proveedores | S1, S57 | hecho | `3e31340` `4e14e65` `dcac8b5` |
| R6 | No funcionales: hardware, hosting, presupuesto, mantenimiento | S1, S2 | hecho | `9a2c976` `59becb9` `7a5bb68` `8952ed9` |
| R7 | Consolidar alcance + MVP + roadmap | S1–S3 | parcial: falta el roadmap | `7c332cf` |
| R8 | Validar el alcance con el negocio | S3 | **bloqueado**: espera al negocio | — |
| R9 | Precios: lista de fábrica, margen por rubro, vigencia, 5% efectivo | S1, S30, S32 | hecho | `6fc61ba` `35dcffb` `0193607` `22981eb` |
| R10 | Entrega y logística: rutas fijas, carga mínima, armado | S1, S18 | parcial: armado sí, entrega sin marcar | `92d6f25` `11daff5` |
| R11 | Cuenta corriente: vencimientos, mora, estado de cuenta | S1, S23, S29 | hecho | `08e14c6` `51a61e4` |
| R12 | Zona de influencia y ubicación del local | S1, S21, S36 | parcial: la localidad no es entidad | `d9cfaba` |
| R13 | ~~Sistema de stock incumbente~~ | — | descartada (D1) | `7c332cf` |
| R14 | Dueño del dato de stock: quién carga y cuándo | S13, A20 | parcial: falta medir el tiempo de carga (D5) | `3e12e27` `73d88e3` |
| R15 | **MVP como conteo: hacer posible saber cuántos hay** | S12, A15 | **en curso** | — |
| R16 | Documento/lista para el contador (no comprobante fiscal) | S14, S16, S27 | pendiente (D2) | — |
| R17 | Ubicaciones: almacén → sector → posición, numeradas ahora; categoría como asignación | S17, A14, A15 | hecho | `8603c4c` `9636c27` |
| R18 | Cliente: ciudad, dirección, cuenta corriente | S18, S19, A16 | hecho | `08e14c6` `d9cfaba` |
| R19 | Devoluciones y cambios: movimiento con estado + ajuste de cuenta | S20, A18 | parcial: falta circuito y política | `3e12e27` |
| R20 | Identidad de producto: ID compartido, búsqueda antes de crear, control de duplicados | S24, A19 | hecho | `3e12e27` `3e31340` `9ff164a` |
| R21 | Venta en cuotas: plan, vencimientos, saldo | S23 | hecho | `d9cfaba` `08e14c6` `51a61e4` |
| R22 | Usuarios y roles: uno por empleado, dos roles, desactivar sin borrar | S39, A24-A26 | hecho | `73d88e3` `648eeb1` |
| R23 | Aplicación web: responsive, sesión persistente por dispositivo | S40, A23, A25 | hecho | `3e12e27` `3897a57` `539a360` |
| R24 | Imágenes de producto: subida desde celular, asociadas al artículo | S45, A30 | parcial: modelo sí, falta subida | `3e12e27` `9fc57e6` |
| R25 | Carga progresiva del stock: entrada sin compra, sin evento de conteo | S41, A27 | hecho | `3e31340` `9ff164a` |
| R26 | Baja lógica de artículos: ocultar conservando historial | S50, A29 | parcial: campo sí, falta la baja desde la app | `3e12e27` |
| R27 | Devolución a fábrica/proveedor por daño o falla | S43, S48 | parcial: tipo y proveedor sí, falta circuito | `3e12e27` `4e14e65` |
| R28 | Segundo local: exhibición sin atención, con transferencias entre locales | S51 | hecho | `92d6f25` `11daff5` `9636c27` |
| R29 | Pedido a medida: medición, plano, presupuesto, margen, confirmación, 15-20 días | S52, S53, S56 | fase 2 (D12) | — |
| R30 | Proveedores: padrón de 40-50 con canal de contacto, sin órdenes de compra | S57 | hecho | `4e14e65` `dcac8b5` |
| R31 | Venta con varias líneas (juegos sin precio propio) | S54, A32 | hecho | `d9cfaba` |

## Log

**L1 — Pedido original (verbatim), 2025-11-18:**
"este proyecto arranca de 0, sistema obelisco es una empresa familiar que se enecarga del rubro de venta de muebles y necesitan principalmente un buen sistema de stock, posteriormente ampliable a venta online y otros rubros, primero quiero hacer todo el relevamiento del alcance"

**L2–L7 — Captura por bloques (2025-11-18):** líneas de producto, Instagram, compras/stock/precio, venta/cobro/fiscal, atención/zona/reparto, equipo/sistemas. Detalle literal en `docs/relevamiento/bitacora.md`.

**L8 — Decisión del cliente:** construir de cero; el sistema anterior no importa. → D1

**L9 — Respuestas del desarrollador:** catálogo por categoría/tipo/color/medidas; no se sabe cuántos artículos hay; volumen de ventas descartado; el Mocho es Norberto; los empleados cargan lo que entra al llegar; facturación fuera de alcance. → S11–S15, D2, D3

**L10 — Requisito reemplazado:** S6 ("Necesitamos factura electrónica", dicho por el cliente) queda reemplazada por S14 (decisión del desarrollador). La contradicción se registra, no se resuelve. Confirmar con el cliente antes de construir comprobantes.

**L11 — Corrección de alcance:** S6 no queda reemplazada sino **diferida a fase 2**. Fase 1 = proveer los medios para facturar de forma sencilla. Se descarta volumetría (D4) y se agrega la numeración interna de almacén por categoría (S17). Ver S16, S17, D2, D4, A14, A15.

**L12 — Respuestas finales:** venta en caja o con armado solicitado; guardar ciudad y dirección del cliente; los clientes con cuenta corriente se guardan; se aceptan cambios y devoluciones; el local está en Tres Lomas. Se retira la pregunta sobre cantidad de personas, por no ser un requisito. → S18–S21, A16–A18

**L13 — Hipótesis retirada:** A3 (reserva como estado) queda descartada porque no hay seña. Existe venta en cuotas con financiación propia (S23). La identidad es por producto, no por unidad: no hay número de serie (S24). Riesgo del catálogo: duplicación, no ambigüedad (A19). Sin turnos: cualquiera abre y cierra (S22), por lo que cada movimiento necesita autor registrado (A20).

**L14 — Cierre de bloqueantes:** `P7` respondida con SÍ (todo entra y sale registrado) → el criterio de éxito es alcanzable. `P42` respondida: documento interno, sin CAE (D6). `P4` respondida sin número ("lo que haga falta" → D5). Cuatro parámetros "modificables" → A21 (lista cerrada). Mantenimiento = el desarrollador (D8, A22). Una PC + celulares (A23). Margen inicial 10% para todos, configurable. Devoluciones 15 días configurable. Localidades ampliables, la localidad es Quenuma. Un sector puede mezclar categorías (confirma A14). Sin responder: P11, P10, P12, P21-P23, plazo, y P6 por incomprensión.

**L15 — Usuarios y web:** usuarios por empleado (S39) y aplicación web (S40). Roles por permiso y no por persona: dos alcanzan (A24). La sesión debe ser barata o la auditoría muere (A25). Usuario se desactiva, no se borra (A26). Nueva superficie de seguridad: Riesgo 14.

**L16 — Bloque 15:** Q1 y Q2 respondidas. No fabrican: hay pedido a medida con fábrica externa (D12, fuera del MVP). Los juegos no tienen precio propio (D13) → sin entidad de combo. Dos locales: el nuevo es solo exhibición (S51) → contradice S5, que queda ampliada. Nuevas categorías: blanquería, barrales, cortinas de blackout (S55, S56). 40-50 proveedores por WhatsApp, sin órdenes de compra (S57). Evidencia directa de A14: las categorías están mezcladas en el espacio físico.

**L16 — Cierre del bloque de alcance:** carga progresiva, sin evento de conteo (S41, A27). El sistema reemplaza el papel (D9). Sin pedidos por encargo (D11). Pesos, sin dólar (S43). Dañado vuelve al proveedor (S43). Garantía del fabricante (S48). Verano es categoría (S47). Sin colchones a medida (S49). Baja lógica con historial (S50, A29). Imágenes de producto (S45, A30). Proyecto propio sin plazo (D10) → Riesgo 15. Queda pendiente P10, P11 y reformular consignación.

**L17 — Corrección de estado (2026-11-19):** pedido del usuario: "prosigue entonces". Se
detectó que la tabla de Tasks seguía diciendo "a diseñar" sobre código ya desplegado en v0.8.0:
el documento describía el relevamiento, no la implementación. Se reconcilia fila por fila contra
el código y se agrega la columna `Evidencia` con el commit que sostiene cada estado. Nueve filas
pasan a `hecho`, seis quedan `parcial` con el hueco nombrado, R8 sigue bloqueada por el negocio.
Arranca R15 (conteo), que es el corazón del MVP y lo único que el ledger todavía no cubre.
