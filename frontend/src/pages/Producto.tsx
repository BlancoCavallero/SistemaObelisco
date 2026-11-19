import { useEffect, useState } from "react";
import { api, type Perfil, type Producto } from "../api";

type Movimiento = {
  id: number;
  fecha: string;
  tipo: string;
  cantidad: number;
  estado: string;
  motivo: string;
  referencia: string;
  usuario: string;
  saldo_acumulado: number;
};

type Costo = { valor: string; vigente_desde: string };

const ETIQUETAS: Record<string, string> = {
  entrada_compra: "Entrada por compra",
  entrada_inventario_inicial: "Inventario inicial",
  armado: "Armado",
  venta: "Venta",
  devolucion_cliente: "Devolución de cliente",
  devolucion_proveedor: "Devolución a proveedor",
  ajuste: "Ajuste",
  transferencia: "Transferencia",
};

function pesos(valor: string | null): string {
  if (valor === null) return "sin precio";
  return Number(valor).toLocaleString("es-AR", { style: "currency", currency: "ARS" });
}

function fecha(iso: string): string {
  return new Date(iso).toLocaleDateString("es-AR", { day: "2-digit", month: "2-digit", year: "2-digit" });
}

export default function Producto({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [producto, setProducto] = useState<Producto | null>(null);
  const [movimientos, setMovimientos] = useState<Movimiento[]>([]);
  const [total, setTotal] = useState(0);
  const [costos, setCostos] = useState<Costo[]>([]);
  const [error, setError] = useState<string | null>(null);

  const id = Number(new URLSearchParams(window.location.search).get("id") ?? 0);

  useEffect(() => {
    if (!id) {
      setError("Falta el identificador del artículo.");
      return;
    }
    api
      .producto(id)
      .then(setProducto)
      .catch((causa: Error) => setError(causa.message));
    api
      .movimientosDe(id)
      .then((datos) => {
        setMovimientos(datos.movimientos);
        setTotal(datos.total);
      })
      .catch(() => setMovimientos([]));
    api.preciosDe(id).then(setCostos).catch(() => setCostos([]));
  }, [id]);

  return (
    <div className="contenedor estrecho">
      <nav className="barra">
        <a href="/deposito" className="link-fino">Depósito</a>
        <a href="/venta" className="link-fino">Cobrar</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      {error ? (
        <p className="error" role="alert">{error}</p>
      ) : (
        <>
          <header className="cabecera">
            <h1>{producto?.nombre ?? "Cargando…"}</h1>
            {producto && (
              <p>
                {producto.id_visible} · {producto.stock} en total ·{" "}
                <strong>{pesos(producto.precio_venta)}</strong>
              </p>
            )}
          </header>

          <section aria-label="Costos">
            <h2 className="titulo-seccion">Costo de fábrica</h2>
            {costos.length === 0 ? (
              <p className="estado">Sin costo cargado: el artículo no se puede vender.</p>
            ) : (
              <ul className="lista">
                {costos.map((c) => (
                  <li key={c.vigente_desde} className="linea-venta">
                    <div>
                      <strong>{pesos(c.valor)}</strong>
                      <span>desde {c.vigente_desde}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section aria-label="Movimientos">
            <h2 className="titulo-seccion">Historial ({total} en stock)</h2>
            {movimientos.length === 0 ? (
              <p className="estado">Sin movimientos.</p>
            ) : (
              <ul className="lista">
                {movimientos.map((m) => (
                  <li key={m.id} className="linea-venta">
                    <div>
                      <strong>
                        {m.cantidad > 0 ? "+" : ""}
                        {m.cantidad} · {ETIQUETAS[m.tipo] ?? m.tipo}
                      </strong>
                      <span>
                        {fecha(m.fecha)} · {m.usuario}
                        {m.motivo ? ` · ${m.motivo}` : ""}
                        {m.estado === "en_caja" ? " · en caja" : " · armado"}
                      </span>
                    </div>
                    <span className="disponibles">{m.saldo_acumulado}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
