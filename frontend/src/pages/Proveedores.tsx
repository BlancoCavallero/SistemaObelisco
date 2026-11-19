import { useEffect, useState } from "react";
import { api, type Perfil } from "../api";

type Proveedor = {
  id: number;
  nombre: string;
  canal: string;
  contacto: string;
  telefono: string;
  email: string;
  notas: string;
};

const VACIO = { nombre: "", canal: "whatsapp", contacto: "", telefono: "", email: "", notas: "" };

export default function Proveedores({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [canales, setCanales] = useState<{ valor: string; etiqueta: string }[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [nuevo, setNuevo] = useState(VACIO);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  function refrescar() {
    api.proveedores().then(setProveedores).catch(() => setProveedores([]));
  }

  useEffect(() => {
    refrescar();
    api.canalesDeProveedor().then(setCanales).catch(() => setCanales([]));
  }, []);

  const filtrados = proveedores.filter((p) => {
    const texto = busqueda.trim().toLowerCase();
    if (!texto) return true;
    return [p.nombre, p.contacto, p.telefono, p.email].some((campo) =>
      campo.toLowerCase().includes(texto),
    );
  });

  const etiqueta = (valor: string) =>
    canales.find((c) => c.valor === valor)?.etiqueta ?? valor;

  async function crear(evento: React.FormEvent) {
    evento.preventDefault();
    setOcupado(true);
    setError(null);
    setMensaje(null);
    try {
      await api.crearProveedor({
        nombre: nuevo.nombre.trim(),
        canal: nuevo.canal,
        contacto: nuevo.contacto.trim(),
        telefono: nuevo.telefono.trim(),
        email: nuevo.email.trim(),
        notas: nuevo.notas.trim(),
      });
      setNuevo(VACIO);
      setMensaje("Proveedor cargado.");
      refrescar();
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  async function darDeBaja(proveedor: Proveedor) {
    setOcupado(true);
    setError(null);
    try {
      await api.desactivarProveedor(proveedor.id);
      setMensaje(`${proveedor.nombre} quedó inactivo. El historial se conserva.`);
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
        <a href="/precios" className="link-fino">Costos</a>
        <a href="/recepcion" className="link-fino">Recibir</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>Proveedores</h1>
        <p>Quiénes son y por dónde se les compra. Sin órdenes de compra: como se compra hoy.</p>
      </header>

      <section className="formulario">
        <label>
          Buscar
          <input
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="nombre, contacto, teléfono"
            autoComplete="off"
          />
        </label>
      </section>

      <h2 className="titulo-seccion">{filtrados.length} proveedores</h2>
      {filtrados.length === 0 ? (
        <p className="estado">Todavía no hay proveedores cargados.</p>
      ) : (
        <ul className="lista">
          {filtrados.map((p) => (
            <li key={p.id} className="linea-venta">
              <div>
                <strong>{p.nombre}</strong>
                <span>
                  {etiqueta(p.canal)}
                  {p.contacto ? ` · ${p.contacto}` : ""}
                  {p.telefono ? ` · ${p.telefono}` : ""}
                </span>
              </div>
              <button className="link-fino" onClick={() => darDeBaja(p)} disabled={ocupado}>
                Dar de baja
              </button>
            </li>
          ))}
        </ul>
      )}

      <section aria-label="Nuevo proveedor">
        <h2 className="titulo-seccion">Agregar</h2>
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
            Cómo se le compra
            <select
              value={nuevo.canal}
              onChange={(e) => setNuevo({ ...nuevo, canal: e.target.value })}
            >
              {canales.map((c) => (
                <option key={c.valor} value={c.valor}>{c.etiqueta}</option>
              ))}
            </select>
          </label>
          <label>
            Contacto
            <input
              value={nuevo.contacto}
              onChange={(e) => setNuevo({ ...nuevo, contacto: e.target.value })}
              placeholder="quién atiende"
            />
          </label>
          <label>
            Teléfono
            <input
              value={nuevo.telefono}
              onChange={(e) => setNuevo({ ...nuevo, telefono: e.target.value })}
              inputMode="tel"
            />
          </label>
          <label>
            Email
            <input
              type="email"
              value={nuevo.email}
              onChange={(e) => setNuevo({ ...nuevo, email: e.target.value })}
            />
          </label>
          <label>
            Notas
            <input
              value={nuevo.notas}
              onChange={(e) => setNuevo({ ...nuevo, notas: e.target.value })}
              placeholder="plazo de entrega, día que pasa el viajante…"
            />
          </label>
          <button className="principal" type="submit" disabled={ocupado}>
            {ocupado ? "Guardando…" : "Agregar proveedor"}
          </button>
        </form>
      </section>

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </div>
  );
}
