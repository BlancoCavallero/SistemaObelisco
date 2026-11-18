import { useEffect, useState } from "react";
import { api, type Catalogo, type Producto } from "../api";

function Tarjeta({ producto, indice }: { producto: Producto; indice: number }) {
  const alt = `${producto.tipo} ${producto.color}, ${producto.medidas} cm`;
  return (
    <article className="tarjeta" style={{ "--i": indice } as React.CSSProperties}>
      <div className="retrato">
        {producto.imagen ? (
          <img src={producto.imagen} alt={alt} loading="lazy" decoding="async" />
        ) : (
          <span className="vacio" aria-hidden="true">
            sin foto
          </span>
        )}
      </div>
      <div className="datos">
        <h3>{producto.nombre}</h3>
        <p className="medidas">{producto.medidas} cm</p>
        <span className="disponibles">{producto.stock} disponible{producto.stock === 1 ? "" : "s"}</span>
      </div>
    </article>
  );
}

export default function CatalogoPagina() {
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [categoria, setCategoria] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    api
      .catalogo(categoria)
      .then((datos: Catalogo) => {
        if (vigente) setCatalogo(datos);
      })
      .catch((causa: Error) => {
        if (vigente) setError(causa.message);
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, [categoria]);

  const productos = catalogo?.productos ?? [];
  const categorias = catalogo?.categorias ?? [];

  return (
    <div data-ambiente={categoria ?? ""} className="contenedor">
      <header className="cabecera">
        <h1>Lo que hay en el local</h1>
        <p>
          Muebles, electrodomésticos, blanquería y todo lo demás. Lo que ves es lo que está
          disponible hoy.
        </p>
      </header>

      {categorias.length > 0 && (
        <nav className="colecciones" aria-label="Categorías">
          <button
            className="chip"
            aria-pressed={categoria === undefined}
            onClick={() => setCategoria(undefined)}
          >
            Todo
          </button>
          {categorias.map((c) => (
            <button
              key={c.nombre}
              className="chip"
              aria-pressed={categoria === c.nombre}
              onClick={() => setCategoria(c.nombre)}
            >
              {c.nombre} <span aria-hidden="true">·</span> {c.total}
            </button>
          ))}
        </nav>
      )}

      <p aria-live="polite" className="estado" hidden={!cargando && !error}>
        {cargando ? "Cargando el catálogo…" : error}
      </p>

      <section className="grilla" aria-label="Artículos disponibles">
        {productos.map((producto, indice) => (
          <Tarjeta key={producto.id} producto={producto} indice={indice} />
        ))}
      </section>

      {!cargando && !error && productos.length === 0 && (
        <p className="estado">Todavía no hay artículos cargados en esta categoría.</p>
      )}
    </div>
  );
}
