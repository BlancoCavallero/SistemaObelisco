# Documentación — Sistema Obelisco

Carpeta de documentación del proyecto. Todo lo que se releva, se decide y se acuerda
vive acá, en texto plano y versionado con el código.

## Estructura

```
docs/
└── relevamiento/
    ├── README.md      ← este índice
    ├── bitacora.md    ← lo que dice el cliente, literal y cronológico (fuente primaria)
    ├── entrevista.md  ← guion para usar en la reunión (lenguaje hablado, por bloques)
    ├── preguntas.md   ← registro de referencia: P0–P43, razón de cada una, quién responde
    ├── pendientes.md  ← qué falta definir: preguntas, decisiones y huecos sin nombrar
    ├── mvp.md         ← MVP como conteo, ritual mínimo en minutos, modelo de ubicación
    ├── diseno.md      ← 10 decisiones de diseño: parámetros, usuarios, producto, precios, movimientos
    └── alcance.md     ← síntesis por dominio: specs, decisiones, riesgos
```

La **bitácora** es la fuente. El **alcance** es la interpretación. Nada entra al alcance
que no esté en la bitácora o confirmado por escrito en este repo.

## Protocolo de captura (vigente)

1. El usuario transmite lo que dijo el cliente. Se registra en `bitacora.md` **literal**,
   con fecha y sin corregir, resumir ni completar.
2. No se interpreta durante la captura. Las contradicciones se marcan, no se resuelven.
3. No se hacen preguntas durante la captura. Cuando el usuario avise que terminó, se emite
   **un solo lote de preguntas** ordenado por impacto.
4. Los huecos se registran como huecos. Nunca se completan por invención.
5. Al cerrar la captura, `alcance.md` se consolida por dominio y se valida con el negocio.

## Estado

| Dominio | Estado | Documento |
|---|---|---|
| Contexto del negocio | capturado | `alcance.md` |
| Líneas de producto | capturado | `bitacora.md` bloque 1 |
| Equipo y roles | capturado | `bitacora.md` bloque 6 |
| Compras y proveedores | parcial | `bitacora.md` bloque 3 |
| Stock y armado | parcial | `bitacora.md` bloques 3, 6 |
| Precios | parcial | `bitacora.md` bloque 3 |
| Ventas, cobro y fiscal | parcial | `bitacora.md` bloque 4 |
| Entrega y zona | capturado | `bitacora.md` bloque 5 |
| Estado de sistemas | capturado, **incógnita crítica** | `bitacora.md` bloque 6 |
| Catálogo y variantes | **sin capturar** | — |
| Tomas de inventario | **sin capturar** | — |
| No funcionales (hardware, hosting, presupuesto) | **sin capturar** | — |
| Alcance del MVP | no iniciado — **bloqueado** | — |

**Captura cerrada** el 2025-11-18. El cliente pidió preguntas ("Decime vos"). Lote emitido en
`preguntas.md`: 40 preguntas en 5 niveles. La consolidación del alcance espera esas respuestas.

## Reglas del proyecto

- **No se escribe código** hasta que el alcance esté consolidado y validado con el negocio.
- Los requisitos se citan **verbatim**. Si el cliente dijo "tarda mucho", no se escribe
  "el proceso es ineficiente".
- Toda decisión de arquitectura se registra como hipótesis hasta que haya evidencia.
- Los supuestos se marcan `[H]`. Un `[H]` que sobrevive hasta el MVP es deuda, no acuerdo.

## Información sensible

Este repo se versiona, se comparte y puede hacerse público. Por eso:

- No se transcribe acá ningún hecho que exponga al cliente ante un tercero: prácticas
  fiscales irregulares, montos no declarados, ni datos de personas en situación sensible.
- Se registra la **consecuencia de ingeniería** de esos hechos, nunca el hecho en sí ni su
  detalle. Ver `C1` en la bitácora.
- Si un dato de ese tipo es necesario para decidir algo, se discute verbalmente y queda
  anotado como restricción, no como testimonio.
- **No se construye funcionalidad para sostener una práctica irregular.** Si el negocio
  necesita que el stock cierre, la decisión previa es del negocio, no un módulo del sistema.
