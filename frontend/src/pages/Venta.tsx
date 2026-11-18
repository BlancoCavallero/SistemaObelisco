import { useEffect, useState } from "react";
import { api, type Perfil, type Producto } from "../api";

type Linea = { producto: Producto; cantidad: number };
type Medio = "efectivo" | "transferencia" | "tarjeta" | "cuenta_corriente";
type Cliente = { id: number; nombre: string; ciudad: string; habilitado_cuenta_corriente: boolean };

const MEDIOS: { valor: Medio; etiqueta: string }[] = [
  { valor: "efectivo", etiqueta: "Efectivo" },
  { valor: "transferencia", etiqueta: "Transferencia" },
  { valor: "tarjeta", etiqueta: "Tarjeta" },
  { valor: "cuenta_corriente", etiqueta: "Cuenta corriente" },
];

function pesos(valor: number): string {
  return valor.toLocaleString("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 });
}

export default function Venta({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [busqueda, setBusqueda] = useState("");
  const [resultados, setResultados] = useState<Producto[]>([]);
  const [lineas, setLineas] = useState<Linea[]>([]);
  const [medio, setMedio] = useState<Medio>("efectivo");
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [cliente, setCliente] = useState<number | "">("");
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    api.clientes().then(setClientes).catch(() => setClientes([]));
  }, []);

  useEffect(() => {
    const texto = busqueda.trim();
    if (texto.length < 2) {
      setResultados([]);
      return;
    }
    let vigente = true;
    api.buscar({ q: texto })
      .then((encontrados) => vigente && setResultados(encontrados.filter((p) => p.stock > 0)))
      .catch(() => vigente && setResultados([]));
    return () => {
      vigente = false;
    };
  }, [busqueda]);

  function agregar(producto: Producto) {
    setMensaje(null);
    setError(null);
    setLineas((actuales) => {
      const existente = actuales.find((l) => l.producto.id === producto.id);
      if (existente) {
        return actuales.map((l) =>
          l.producto.id === producto.id
            ? { ...l, cantidad: Math.min(l.cantidad + 1, l.producto.stock) }
            : l,
        );
      }
      return [...actuales, { producto, cantidad: 1 }];
    });
    setBusqueda("");
    setResultados([]);
  }

  function cambiarCantidad(id: number, cantidad: number) {
    setLineas((actuales) =>
      actuales.map((l) => (l.producto.id === id ? { ...l, cantidad } : l)),
    );
  }

  const total = lineas.reduce(
    (suma, l) => suma + Number(l.producto.precio_venta ?? 0) * l.cantidad,
    0,
  );
  const excede = lineas.filter((l) => l.cantidad > l.producto.stock);
  const faltaCliente = medio === "cuenta_corriente" && cliente === "";

  async function cobrar() {
    setOcupado(true);
    setError(null);
    setMensaje(null);
    try {
      const venta = await api.vender({
        medio_pago: medio,
        cliente: cliente === "" ? null : cliente,
        lineas: lineas.map((l) => ({ producto: l.producto.id, cantidad: l.cantidad })),
      });
      setMensaje(`Venta #${venta.id} por ${pesos(Number(venta.total))}.`);
      setLineas([]);
      setCliente("");
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  return (
    <div className="contenedor estrecho">
      <nav className="barra">
        <a href="/recepcion" className="link-fino">Cargar mercadería</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>Cobrar</h1>
        <p>Buscá el artículo, poné la cantidad y elegí cómo paga.</p>
      </header>

      <section className="formulario">
        <label>
          Buscar artículo
          <input
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="sillón, heladera, colchón…"
            autoComplete="off"
          />
        </label>
      </section>

      {resultados.length > 0 && (
        <ul className="lista" aria-live="polite">
          {resultados.map((p) => (
            <li key={p.id}>
              <button type="button" className="opcion" onClick={() => agregar(p)}>
                <strong>{p.nombre}</strong>
                <span>
                  {pesos(Number(p.precio_venta ?? 0))} · {p.stock} disp.
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {lineas.length > 0 && (
        <section aria-label="Artículos en la venta">
          <h2 className="titulo-seccion">En la venta</h2>
          <ul className="lista">
            {lineas.map((l) => (
              <li key={l.producto.id} className="linea-venta">
                <div>
                  <strong>{l.producto.nombre}</strong>
                  <span>{pesos(Number(l.producto.precio_venta ?? 0))} c/u</span>
                </div>
                <input
                  type="number"
                  inputMode="numeric"
                  min={1}
                  max={l.producto.stock}
                  value={l.cantidad}
                  onChange={(e) => cambiarCantidad(l.producto.id, Number(e.target.value))}
                  aria-label={`Cantidad de ${l.producto.tipo}`}
                />
                <button
                  type="button"
                  className="link-fino"
                  onClick={() => setLineas((a) => a.filter((x) => x.producto.id !== l.producto.id))}
                >
                  Quitar
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {lineas.length > 0 && (
        <section className="formulario" aria-label="Forma de pago">
          <label>
            Forma de pago
            <select value={medio} onChange={(e) => setMedio(e.target.value as Medio)}>
              {MEDIOS.map((m) => (
                <option key={m.valor} value={m.valor}>{m.etiqueta}</option>
              ))}
            </select>
          </label>

          <label>
            Cliente {medio === "cuenta_corriente" ? "(obligatorio)" : "(opcional)"}
            <select value={cliente} onChange={(e) => setCliente(e.target.value ? Number(e.target.value) : "")}>
              <option value="">Consumidor final</option>
              {clientes
                .filter((c) => medio !== "cuenta_corriente" || c.habilitado_cuenta_corriente)
                .map((c) => (
                  <option key={c.id} value={c.id}>{c.nombre} — {c.ciudad}</option>
                ))}
            </select>
          </label>

          <p className="total">Total {pesos(total)}</p>

          <button
            className="principal"
            type="button"
            onClick={cobrar}
            disabled={ocupado || excede.length > 0 || faltaCliente}
          >
            {ocupado ? "Cobrando…" : "Confirmar venta"}
          </button>

          {excede.length > 0 && (
            <p className="error" role="alert">
              Hay más cantidad que stock en {excede.map((l) => l.producto.nombre).join(", ")}.
            </p>
          )}
        </section>
      )}

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </div>
  );
}
