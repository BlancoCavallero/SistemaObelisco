import { useEffect, useMemo, useState } from "react";
import { api, type Perfil, type Producto } from "../api";

type Fila = { codigo: string; valor: string };

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function Precios({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [faltantes, setFaltantes] = useState<Producto[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [fecha, setFecha] = useState(hoy());
  const [pegado, setPegado] = useState("");
  const [individual, setIndividual] = useState<Record<number, string>>({});
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  async function cargar() {
    const [sinCosto, todos] = await Promise.all([api.faltantes(), api.productos()]);
    setFaltantes(sinCosto);
    setProductos(todos);
  }

  useEffect(() => {
    cargar().catch((causa: Error) => setError(causa.message));
  }, []);

  const porCodigo = useMemo(() => {
    const mapa = new Map<string, Producto>();
    for (const producto of productos) mapa.set(producto.id_visible.toUpperCase(), producto);
    return mapa;
  }, [productos]);

  const filas: Fila[] = useMemo(
    () =>
      pegado
        .split("\n")
        .map((linea) => linea.trim())
        .filter(Boolean)
        .map((linea) => {
          const [codigo, valor] = linea.split(/\s*[;,\t]\s*|\s{2,}/);
          return { codigo: (codigo ?? "").trim(), valor: (valor ?? "").trim() };
        })
        .filter((fila) => fila.codigo && fila.valor),
    [pegado],
  );

  const resueltas = filas.map((fila) => ({
    ...fila,
    producto: porCodigo.get(fila.codigo.toUpperCase()),
  }));
  const sinResolver = resueltas.filter((f) => !f.producto);
  const invalidas = resueltas.filter(
    (f) => f.producto && !(Number(f.valor.replace(",", ".")) > 0),
  );
  const listas = resueltas.filter((f) => f.producto && Number(f.valor.replace(",", ".")) > 0);

  async function cargarPegado() {
    setOcupado(true);
    setError(null);
    setMensaje(null);
    try {
      const respuesta = await api.cargarPrecios(
        fecha,
        listas.map((f) => ({ producto: f.producto!.id, valor: f.valor.replace(",", ".") })),
      );
      setMensaje(`${respuesta.creados} costos cargados con fecha ${fecha}.`);
      setPegado("");
      await cargar();
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  async function cargarUno(producto: Producto) {
    const valor = (individual[producto.id] ?? "").replace(",", ".");
    if (!(Number(valor) > 0)) return;
    setOcupado(true);
    setError(null);
    try {
      await api.cargarPrecios(fecha, [{ producto: producto.id, valor }]);
      setMensaje(`Costo de ${producto.nombre} cargado.`);
      setIndividual((actual) => ({ ...actual, [producto.id]: "" }));
      await cargar();
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
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>Costos de fábrica</h1>
        <p>
          Un artículo sin costo no se puede vender. Cargá primero los que faltan y después
          actualizá la lista completa.
        </p>
      </header>

      <section className="formulario">
        <label>
          Fecha de la lista
          <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
        </label>
      </section>

      <section aria-label="Faltan costos">
        <h2 className="titulo-seccion">
          Faltan costos ({faltantes.length})
        </h2>
        {faltantes.length === 0 ? (
          <p className="estado">Todos los artículos tienen costo cargado.</p>
        ) : (
          <ul className="lista">
            {faltantes.slice(0, 50).map((producto) => (
              <li key={producto.id} className="linea-venta">
                <div>
                  <strong>{producto.nombre}</strong>
                  <span>{producto.id_visible}</span>
                </div>
                <input
                  type="number"
                  inputMode="numeric"
                  placeholder="costo"
                  value={individual[producto.id] ?? ""}
                  onChange={(e) =>
                    setIndividual((actual) => ({ ...actual, [producto.id]: e.target.value }))
                  }
                  aria-label={`Costo de ${producto.tipo}`}
                />
                <button
                  type="button"
                  className="link-fino"
                  onClick={() => cargarUno(producto)}
                  disabled={ocupado}
                >
                  Guardar
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Pegar lista">
        <h2 className="titulo-seccion">Pegar la lista</h2>
        <p className="estado">
          Una línea por artículo: <code>código;costo</code>. También sirve pegar dos columnas
          desde una planilla.
        </p>
        <textarea
          className="pegado"
          value={pegado}
          onChange={(e) => setPegado(e.target.value)}
          rows={8}
          placeholder={"MUE-0001;12000\nMUE-0002;8500"}
          spellCheck={false}
        />

        {filas.length > 0 && (
          <p aria-live="polite" className="estado">
            {listas.length} listas
            {sinResolver.length > 0 && ` · ${sinResolver.length} con código desconocido`}
            {invalidas.length > 0 && ` · ${invalidas.length} con valor inválido`}
          </p>
        )}

        <button
          className="principal"
          type="button"
          onClick={cargarPegado}
          disabled={ocupado || listas.length === 0 || sinResolver.length > 0 || invalidas.length > 0}
        >
          {ocupado ? "Cargando…" : `Cargar ${listas.length} costos`}
        </button>
      </section>

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </div>
  );
}
