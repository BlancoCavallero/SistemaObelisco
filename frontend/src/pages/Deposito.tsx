import { useEffect, useState } from "react";
import { api, type Perfil, type Producto } from "../api";

type FilaStock = {
  producto: number;
  id_visible: string;
  nombre: string;
  total: number;
  en_caja: number;
  listo: number;
};

type Posicion = { id: number; etiqueta: string; almacen: number };

type Resumen = { id: number | null; codigo: string; nombre: string; total: number };
type FilaUbicacion = {
  producto: number;
  id_visible: string;
  nombre: string;
  estado: string;
  posicion: number | null;
  etiqueta: string;
  cantidad: number;
};

function Buscador({
  onElegir,
  etiqueta,
}: {
  onElegir: (producto: Producto) => void;
  etiqueta: string;
}) {
  const [texto, setTexto] = useState("");
  const [resultados, setResultados] = useState<Producto[]>([]);

  useEffect(() => {
    const termino = texto.trim();
    if (termino.length < 2) {
      setResultados([]);
      return;
    }
    let vigente = true;
    api
      .buscar({ q: termino })
      .then((encontrados) => vigente && setResultados(encontrados))
      .catch(() => vigente && setResultados([]));
    return () => {
      vigente = false;
    };
  }, [texto]);

  return (
    <div className="formulario">
      <label>
        {etiqueta}
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="sillón, heladera…"
          autoComplete="off"
        />
      </label>
      {resultados.length > 0 && (
        <ul className="lista">
          {resultados.map((producto) => (
            <li key={producto.id}>
              <button
                type="button"
                className="opcion"
                onClick={() => {
                  onElegir(producto);
                  setTexto("");
                  setResultados([]);
                }}
              >
                <strong>{producto.nombre}</strong>
                <span>
                  {producto.id_visible} · {producto.stock} disp.
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Deposito({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [stock, setStock] = useState<FilaStock[]>([]);
  const [posiciones, setPosiciones] = useState<Posicion[]>([]);

  const [paraArmar, setParaArmar] = useState<Producto | null>(null);
  const [cantidadArmar, setCantidadArmar] = useState("1");

  const [paraMover, setParaMover] = useState<Producto | null>(null);
  const [cantidadMover, setCantidadMover] = useState("1");
  const [desde, setDesde] = useState<number | "">("");
  const [hasta, setHasta] = useState<number | "">("");

  const [porUbicacion, setPorUbicacion] = useState<{ almacenes: Resumen[]; filas: FilaUbicacion[] }>({
    almacenes: [],
    filas: [],
  });
  const [almacen, setAlmacen] = useState<number | null>(null);

  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  function refrescar() {
    api.stock().then(setStock).catch(() => setStock([]));
    api.posiciones().then(setPosiciones).catch(() => setPosiciones([]));
    api
      .stockUbicaciones(almacen ?? undefined)
      .then(setPorUbicacion)
      .catch(() => setPorUbicacion({ almacenes: [], filas: [] }));
  }

  useEffect(refrescar, [almacen]);

  const fila = (id: number | undefined) => stock.find((f) => f.producto === id);

  async function armar() {
    if (!paraArmar) return;
    setOcupado(true);
    setError(null);
    setMensaje(null);
    try {
      const resultado = await api.armar(paraArmar.id, Number(cantidadArmar));
      setMensaje(`Armadas ${resultado.armado}. ${paraArmar.nombre}`);
      setParaArmar(null);
      setCantidadArmar("1");
      refrescar();
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  async function transferir() {
    if (!paraMover || desde === "" || hasta === "") return;
    setOcupado(true);
    setError(null);
    setMensaje(null);
    try {
      const resultado = await api.transferir({
        producto: paraMover.id,
        cantidad: Number(cantidadMover),
        desde,
        hasta,
      });
      setMensaje(`Movidas ${resultado.transferido}. ${paraMover.nombre}`);
      setParaMover(null);
      setCantidadMover("1");
      refrescar();
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  return (
    <div className="contenedor estrecho">
      <nav className="barra">
        <a href="/venta" className="link-fino">Cobrar</a>
        <a href="/recepcion" className="link-fino">Recibir</a>
        <a href="/conteo" className="link-fino">Contar</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>Depósito</h1>
        <p>Armar lo que vino en caja y mover mercadería entre locales.</p>
      </header>

      <section aria-label="Armado">
        <h2 className="titulo-seccion">Armar</h2>
        {paraArmar ? (
          <div className="linea-venta">
            <div>
              <strong>{paraArmar.nombre}</strong>
              <span>
                en caja: {fila(paraArmar.id)?.en_caja ?? 0} · armado:{" "}
                {fila(paraArmar.id)?.listo ?? 0}
              </span>
            </div>
            <input
              type="number"
              inputMode="numeric"
              min={1}
              value={cantidadArmar}
              onChange={(e) => setCantidadArmar(e.target.value)}
              aria-label="Cantidad a armar"
            />
            <button className="link-fino" onClick={() => setParaArmar(null)}>Cambiar</button>
          </div>
        ) : (
          <Buscador etiqueta="¿Qué se arma?" onElegir={setParaArmar} />
        )}
        {paraArmar && (
          <button
            className="principal"
            type="button"
            onClick={armar}
            disabled={ocupado || !cantidadArmar}
          >
            {ocupado ? "Armando…" : "Registrar armado"}
          </button>
        )}
      </section>

      <section aria-label="Transferencia">
        <h2 className="titulo-seccion">Mover entre locales</h2>
        {paraMover ? (
          <>
            <div className="linea-venta">
              <div>
                <strong>{paraMover.nombre}</strong>
                <span>disponible: {fila(paraMover.id)?.total ?? 0}</span>
              </div>
              <input
                type="number"
                inputMode="numeric"
                min={1}
                value={cantidadMover}
                onChange={(e) => setCantidadMover(e.target.value)}
                aria-label="Cantidad a mover"
              />
              <button className="link-fino" onClick={() => setParaMover(null)}>Cambiar</button>
            </div>
            <div className="formulario">
              <label>
                Desde
                <select value={desde} onChange={(e) => setDesde(e.target.value ? Number(e.target.value) : "")}>
                  <option value="">Elegí…</option>
                  {posiciones.map((p) => (
                    <option key={p.id} value={p.id}>{p.etiqueta}</option>
                  ))}
                </select>
              </label>
              <label>
                Hasta
                <select value={hasta} onChange={(e) => setHasta(e.target.value ? Number(e.target.value) : "")}>
                  <option value="">Elegí…</option>
                  {posiciones
                    .filter((p) => p.id !== desde)
                    .map((p) => (
                      <option key={p.id} value={p.id}>{p.etiqueta}</option>
                    ))}
                </select>
              </label>
            </div>
            <button
              className="principal"
              type="button"
              onClick={transferir}
              disabled={ocupado || desde === "" || hasta === "" || !cantidadMover}
            >
              {ocupado ? "Moviendo…" : "Mover"}
            </button>
          </>
        ) : (
          <Buscador etiqueta="¿Qué se mueve?" onElegir={setParaMover} />
        )}
      </section>

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}

      <section aria-label="Por ubicación">
        <h2 className="titulo-seccion">Cuánto hay en cada lugar</h2>
        <nav className="colecciones" aria-label="Filtrar por local">
          <button
            className="chip"
            aria-pressed={almacen === null}
            onClick={() => setAlmacen(null)}
          >
            Todo
          </button>
          {porUbicacion.almacenes.map((a) => (
            <button
              key={a.codigo}
              className="chip"
              aria-pressed={almacen === a.id}
              onClick={() => setAlmacen(a.id)}
            >
              {a.codigo} · {a.total}
            </button>
          ))}
        </nav>
        {porUbicacion.filas.length === 0 ? (
          <p className="estado">Sin mercadería ubicada todavía.</p>
        ) : (
          <ul className="lista">
            {porUbicacion.filas.slice(0, 25).map((f) => (
              <li key={`${f.producto}-${f.etiqueta}-${f.estado}`} className="linea-venta">
                <div>
                  <strong>{f.nombre}</strong>
                  <span>
                    {f.etiqueta} · {f.estado === "en_caja" ? "en caja" : "armado"}
                  </span>
                </div>
                <span className="disponibles">{f.cantidad}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Stock">
        <h2 className="titulo-seccion">Total por artículo</h2>
        {stock.length === 0 ? (
          <p className="estado">Sin artículos cargados todavía.</p>
        ) : (
          <ul className="lista">
            {stock.slice(0, 20).map((f) => (
              <li key={f.producto} className="linea-venta">
                <div>
                  <strong>{f.nombre}</strong>
                  <span>{f.id_visible}</span>
                </div>
                <a className="link-fino" href={`/producto?id=${f.producto}`}>
                  caja {f.en_caja} · listo {f.listo}
                </a>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
