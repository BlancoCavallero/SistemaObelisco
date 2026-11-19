import { useEffect, useState } from "react";
import { api, type Perfil } from "../api";

type Cliente = { id: number; nombre: string; ciudad: string; habilitado_cuenta_corriente: boolean };
type Cuenta = Awaited<ReturnType<typeof api.cuentaDe>>;
type Moroso = { cliente: { id: number; nombre: string; ciudad: string }; vencido: string };

function pesos(texto: string): string {
  return Number(texto).toLocaleString("es-AR", { style: "currency", currency: "ARS" });
}

export default function Cuentas({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [vista, setVista] = useState<"clientes" | "morosos">("clientes");
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [morosos, setMorosos] = useState<Moroso[]>([]);
  const [elegido, setElegido] = useState<number | null>(null);
  const [cuenta, setCuenta] = useState<Cuenta | null>(null);
  const [monto, setMonto] = useState("");
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  const [nuevo, setNuevo] = useState({ nombre: "", ciudad: "", habilitado: true });

  function refrescar() {
    api.clientes().then(setClientes).catch(() => setClientes([]));
    api.morosos().then(setMorosos).catch(() => setMorosos([]));
    if (elegido !== null) {
      api.cuentaDe(elegido).then(setCuenta).catch(() => setCuenta(null));
    }
  }

  useEffect(refrescar, [elegido]);

  async function pagar() {
    if (elegido === null || !monto) return;
    setOcupado(true);
    setError(null);
    setMensaje(null);
    try {
      const resultado = await api.registrarPago(elegido, monto.replace(",", "."));
      setMensaje(`Pago registrado. Saldo: ${pesos(resultado.saldo)}`);
      setMonto("");
      refrescar();
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  async function crear(evento: React.FormEvent) {
    evento.preventDefault();
    setOcupado(true);
    setError(null);
    try {
      await api.crearCliente({
        nombre: nuevo.nombre.trim(),
        ciudad: nuevo.ciudad.trim(),
        habilitado_cuenta_corriente: nuevo.habilitado,
      });
      setNuevo({ nombre: "", ciudad: "", habilitado: true });
      setMensaje("Cliente creado.");
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
        <a href="/deposito" className="link-fino">Depósito</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>Cuentas</h1>
        <p>Quién debe, cuánto debe y desde cuándo.</p>
      </header>

      <nav className="colecciones" aria-label="Vistas">
        <button className="chip" aria-pressed={vista === "clientes"} onClick={() => setVista("clientes")}>
          Clientes · {clientes.length}
        </button>
        <button className="chip" aria-pressed={vista === "morosos"} onClick={() => setVista("morosos")}>
          Con deuda vencida · {morosos.length}
        </button>
      </nav>

      {vista === "morosos" ? (
        morosos.length === 0 ? (
          <p className="estado">Nadie tiene cuotas vencidas.</p>
        ) : (
          <ul className="lista">
            {morosos.map((m) => (
              <li key={m.cliente.id}>
                <button type="button" className="opcion" onClick={() => setElegido(m.cliente.id)}>
                  <strong>{m.cliente.nombre}</strong>
                  <span>{pesos(m.vencido)} vencido</span>
                </button>
              </li>
            ))}
          </ul>
        )
      ) : clientes.length === 0 ? (
        <p className="estado">Todavía no hay clientes cargados.</p>
      ) : (
        <ul className="lista">
          {clientes.map((c) => (
            <li key={c.id}>
              <button type="button" className="opcion" onClick={() => setElegido(c.id)}>
                <strong>{c.nombre}</strong>
                <span>
                  {c.ciudad}
                  {c.habilitado_cuenta_corriente ? " · cuenta corriente" : ""}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {elegido !== null && cuenta && (
        <section aria-label="Cuenta del cliente">
          <h2 className="titulo-seccion">{cuenta.cliente.nombre}</h2>
          <p className="total">
            Saldo {pesos(cuenta.saldo)}
            {Number(cuenta.vencido) > 0 && ` · vencido ${pesos(cuenta.vencido)}`}
          </p>

          <div className="formulario">
            <label>
              Registrar un pago
              <input
                type="number"
                inputMode="decimal"
                min={0}
                value={monto}
                onChange={(e) => setMonto(e.target.value)}
                placeholder="monto"
              />
            </label>
            <button className="principal" type="button" onClick={pagar} disabled={ocupado || !monto}>
              {ocupado ? "Registrando…" : "Registrar pago"}
            </button>
          </div>

          <ul className="lista">
            {cuenta.movimientos.map((m) => (
              <li key={m.id} className="linea-venta">
                <div>
                  <strong>
                    {m.tipo === "cargo" ? "Cuota" : m.tipo === "pago" ? "Pago" : "Ajuste"}{" "}
                    {pesos(m.monto)}
                  </strong>
                  <span>
                    {m.vencimiento ? `vence ${m.vencimiento}` : m.motivo || ""}
                  </span>
                </div>
                <button
                  type="button"
                  className="link-fino"
                  onClick={() => setElegido(null)}
                >
                  Cerrar
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-label="Nuevo cliente">
        <h2 className="titulo-seccion">Nuevo cliente</h2>
        <form className="formulario" onSubmit={crear}>
          <label>
            Nombre
            <input
              value={nuevo.nombre}
              onChange={(e) => setNuevo({ ...nuevo, nombre: e.target.value })}
              required
            />
          </label>
          <label>
            Ciudad
            <input
              value={nuevo.ciudad}
              onChange={(e) => setNuevo({ ...nuevo, ciudad: e.target.value })}
              required
            />
          </label>
          <label className="casilla">
            <input
              type="checkbox"
              checked={nuevo.habilitado}
              onChange={(e) => setNuevo({ ...nuevo, habilitado: e.target.checked })}
            />
            Habilitado para cuenta corriente
          </label>
          <button className="secundario" type="submit" disabled={ocupado}>
            Crear cliente
          </button>
        </form>
      </section>

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </div>
  );
}
