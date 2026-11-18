# Interfaz del catálogo — brief de diseño

Referencias pedidas: `articolostudios.com/lookbooks` (catálogo) y
`brisa-serena-costa.vercel.app` (movimiento).

---

## Qué se toma de cada una

### Articolo Studios — la estructura

| Se toma | Por qué |
|---|---|
| Catálogo organizado en **colecciones**, no en una lista plana de SKUs | El negocio ya tiene categorías (muebles, electro, blanquería, verano, oficina). El catálogo las usa como índice |
| **Portada vertical**, una imagen grande que manda | Un mueble se reconoce por su silueta, no por su nombre de 6 campos |
| Texto mínimo: título + una línea + acción | El nombre derivado (`Sillón 3 cuerpos · Gris · 85x90x180`) ya es largo: no compite con párrafos |
| Navegación por categoría arriba, contenido visual abajo | Escaneo rápido en el celular |

**No se toma:** el peso del sitio (WordPress + veinte plugins), el tono corporativo de
"digital lookbook", ni el idioma.

### Brisa Serena — el movimiento

| Se toma | Por qué |
|---|---|
| **El scroll como línea de tiempo**: un estado ambiental continuo que evoluciona | Es la técnica que hace que algo se sienta vivo sin ser molesto |
| Animaciones en **CSS y SVG, sin librerías** | Cero KB extra, nada que mantener, y el autor del sitio lo puede leer |
| Una serif para títulos + una sans para texto | Da jerarquía sin esfuerzo. Propuesta: Bitter + Libre Franklin (las mismas, son libres) |
| Paleta restringida con un solo color de tema | Evita el catálogo multicolor que se ve barato |
| Detalles: botón flotante, toast, diálogo de ficha, `aria-live`, `noscript` | Están resueltos y son accesibles |

**No se toma la metáfora.** Sol, mar, luna y noche funcionan para alquileres de playa. Copiarla
en una mueblería sería un disfraz. **La técnica se copia; el tema no.**

### La metáfora propia: la luz del local

El equivalente honesto para este negocio es **la luz sobre el material**. El estado ambiental
del catálogo cambia de temperatura según la categoría:

```
muebles      → luz cálida, madera        (ámbar apagado)
blanquería   → luz difusa, neutra        (crema)
electro      → luz fría, de showroom     (azul grisáceo)
verano       → luz alta, exterior        (celeste pálido)
oficina      → luz plana, fluorescente   (gris frío)
```

Es un solo color de fondo que interpola al cambiar de categoría. Sutil, continuo, sin dibujos.

---

## Dos superficies, dos lenguajes

Esta es la decisión que más importa y la más fácil de arruinar:

| Superficie | Quién la usa | Animación |
|---|---|---|
| **Catálogo** | El cliente, en el local o desde Instagram | Sí: scroll, entradas escalonadas, transición de categoría |
| **Operación** (recepción, venta, armado) | Empleados, con el cliente adelante | **Ninguna.** Feedback de 150 ms máximo |

Animar la pantalla de recepción sería violar A13: en el mostrador, la animación es el enemigo.
El catálogo es vidriera; la operación es mostrador.

---

## Especificación de movimiento

| Regla | Valor |
|---|---|
| Propiedades animadas | **Solo `transform` y `opacity`.** Nunca `width`, `top`, `height` ni `box-shadow` |
| Micro (hover, tap) | 150 ms |
| Entrada de tarjeta | 300–400 ms |
| Transición de categoría | 600–900 ms |
| Easing de entrada | `cubic-bezier(.22, .61, .36, 1)` |
| Easing atado al scroll | `linear`, calculado sobre el progreso |
| Escalonado de la grilla | 40 ms por índice, tope 8 elementos |
| `prefers-reduced-motion: reduce` | Todo a 0 ms, sin parallax, sin estado ambiental animado |
| Bucles infinitos | Prohibidos salvo un detalle decorativo y **pausado** cuando la pestaña no está visible |

## Presupuesto de rendimiento

Es un plan gratuito y un celular en 4G: el diseño no puede comerlo.

- Imágenes **WebP**, 1600 px de alto máximo, 150–250 KB, `loading="lazy"`, `decoding="async"`,
  `srcset` con dos tamaños.
- **Cero librerías de animación.** CSS propio, como la referencia.
- JS inicial **< 120 KB** comprimido.
- Lighthouse móvil **≥ 90** en performance. Si baja, se recorta animación, no contenido.

## Accesibilidad

- Contraste AA, foco visible en toda la grilla.
- `alt` real en cada foto (`Sillón 3 cuerpos gris, 180 cm`), no el nombre del archivo.
- Navegación por teclado en la grilla y en el diálogo de ficha.
- `aria-live="polite"` en el resultado del filtro: "12 artículos".
- `noscript` con un mensaje y el enlace al listado en JSON (`/api/catalogo/`).
  *Corrección:* una SPA no puede renderizar la lista completa sin JavaScript. Servir el
  catálogo desde plantillas Django sería la alternativa, y contradice la decisión de un solo
  front en React. Se acepta la degradación y se deja dicho.

---

## Decisión de producto pendiente

**¿El catálogo público muestra precios?**

Hoy el precio es `lista de fábrica × margen` y se resuelve en el mostrador. Publicarlo lo
congela de hecho y obliga a mantenerlo al día en un lugar donde los clientes lo van a comparar.

**Recomendación:** catálogo **sin precio**, con "consultar". El precio aparece solo en el modo
empleado. Si el negocio quiere mostrarlo, es un campo más en el endpoint, no un rediseño.
