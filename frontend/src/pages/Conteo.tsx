import { useEffect, useState } from "react";
import { api, type FilaConteo, type Perfil } from "../api";

export default function Conteo({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [texto, setTexto] = useState("");
  const [motivo, setMotivo] = useState("");
  const [filas, setFilas] = useState<FilaConteo[]>([]);
  const [contados, setContados] = useState<Record<number, string>>({});
  const [estados, setEstados] = useState<Record<number, string>>({});
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState<number | null>(null);
  const [cargando, setCargando] = useState(true);
  const [version, setVersion] = useState(0);

  const termino = texto.trim();

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    api
      .conteoHoja(termino.length >= 2 ? termino : undefined)
      .then((respuesta) => vigente && setFilas(respuesta.filas))
      .catch(() => vigente && setFilas([]))
      .finally(() => vigente && setCargando(false));
    return () => {
      vigente = false;
    };
  }, [termino, version]);

  function anotar(producto: number, valor: string) {
    setContados((previos) => ({ ...previos, [producto]: valor }));
  }

  async function registrar(fila: FilaConteo) {
    const valor = contados[fila.producto];
    if (valor === undefined || valor === "") return;
    setOcupado(fila.producto);
    setError(null);
    setMensaje(null);
    try {
      const resultado = await api.contar({
        producto: fila.producto,
        contado: Number(valor),
        // El numero que el operador tenia en pantalla: si el stock se movio, el server
        // rechaza en vez de inventar un ajuste con la diferencia de la carrera.
        esperado: fila.esperado,
        estado: estados[fila.producto] || undefined,
        motivo: motivo.trim() || undefined,
      });
      setMensaje(
        resultado.ajuste === 0
          ? `${fila.nombre}: coincide con ${resultado.contado}. No se escribió nada.`
          : `${fila.nombre}: el sistema decía ${resultado.esperado}, contaste ${resultado.contado} → ajuste ${resultado.ajuste > 0 ? "+" : ""}${resultado.ajuste}.`,
      );
      setContados((previos) => {
        const copia = { ...previos };
        delete copia[fila.producto];
        return copia;
      });
      setEstados((previos) => {
        const copia = { ...previos };
        delete copia[fila.producto];
        return copia;
      });
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(null);
      setVersion((n) => n + 1);
    }
  }

  return (
    <div className="contenedor estrecho">
      <nav className="barra">
        <a href="/deposito" className="link-fino">Depósito</a>
        <a href="/venta" className="link-fino">Cobrar</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>Conteo</h1>
        <p>
          Contá lo que hay y anotá el número. Si coincide con el sistema no se escribe nada; si
          no coincide, queda un ajuste con tu nombre y el motivo.
        </p>
      </header>

      <div className="formulario">
        <label>
          ¿Qué contás?
          <input
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="sillón, heladera, colchón…"
            autoComplete="off"
            inputMode="search"
          />
        </label>
        <label>
          Si falta algo, ¿por qué?
          <input
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            placeholder="se rompió, no llegó, se entregó de más…"
            autoComplete="off"
          />
        </label>
      </div>

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}

      {cargando ? (
        <p className="estado">Trayendo la lista…</p>
      ) : filas.length === 0 ? (
        <p className="estado">No hay artículos que coincidan.</p>
      ) : (
        <ul className="lista">
          {filas.map((fila) => (
            <li key={fila.producto} className="linea-venta">
              <div>
                <strong>{fila.nombre}</strong>
                <span>
                  {fila.id_visible} · sistema: {fila.esperado} (caja {fila.en_caja}, armado{" "}
                  {fila.listo})
                </span>
              </div>
              {fila.en_caja > 0 && fila.listo > 0 && (
                <select
                  value={estados[fila.producto] ?? ""}
                  onChange={(e) =>
                    setEstados((previos) => ({ ...previos, [fila.producto]: e.target.value }))
                  }
                  aria-label={`Qué contaste de ${fila.nombre}`}
                >
                  <option value="">caja o armado…</option>
                  <option value="en_caja">en caja</option>
                  <option value="listo">armado</option>
                </select>
              )}
              <input
                type="number"
                inputMode="numeric"
                min={0}
                value={contados[fila.producto] ?? ""}
                onChange={(e) => anotar(fila.producto, e.target.value)}
                aria-label={`Cantidad contada de ${fila.nombre}`}
                placeholder="conté"
              />
              <button
                className="link-fino"
                type="button"
                onClick={() => registrar(fila)}
                disabled={
                  ocupado === fila.producto ||
                  contados[fila.producto] === undefined ||
                  contados[fila.producto] === ""
                }
              >
                {ocupado === fila.producto ? "Anotando…" : "Anotar"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
