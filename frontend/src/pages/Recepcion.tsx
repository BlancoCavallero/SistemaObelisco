import { useEffect, useMemo, useState } from "react";
import { api, type Categoria, type Color, type Perfil, type Producto, type Tipo } from "../api";

type Entrada = "entrada_compra" | "entrada_inventario_inicial";

export default function Recepcion({ perfil, onSalir }: { perfil: Perfil; onSalir: () => void }) {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [tipos, setTipos] = useState<Tipo[]>([]);
  const [colores, setColores] = useState<Color[]>([]);

  const [categoria, setCategoria] = useState<number | "">("");
  const [tipo, setTipo] = useState<number | "">("");
  const [color, setColor] = useState("");
  const [medidas, setMedidas] = useState({ alto_cm: "", ancho_cm: "", largo_cm: "" });

  const [parecidos, setParecidos] = useState<Producto[] | null>(null);
  const [elegido, setElegido] = useState<Producto | null>(null);
  const [cantidad, setCantidad] = useState("1");
  const [entrada, setEntrada] = useState<Entrada>("entrada_compra");

  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    api.categorias().then(setCategorias).catch(() => setCategorias([]));
    api.colores().then(setColores).catch(() => setColores([]));
  }, []);

  useEffect(() => {
    setTipo("");
    if (categoria === "") {
      setTipos([]);
      return;
    }
    api.tipos(categoria).then(setTipos).catch(() => setTipos([]));
  }, [categoria]);

  const completo = useMemo(
    () => tipo !== "" && color !== "" && medidas.alto_cm && medidas.ancho_cm && medidas.largo_cm,
    [tipo, color, medidas],
  );

  async function buscar() {
    setOcupado(true);
    setError(null);
    setMensaje(null);
    setElegido(null);
    try {
      const encontrados = await api.buscar({
        tipo: tipo as number,
        color,
        alto_cm: Number(medidas.alto_cm),
        ancho_cm: Number(medidas.ancho_cm),
        largo_cm: Number(medidas.largo_cm),
      });
      setParecidos(encontrados);
      if (encontrados.length === 1) setElegido(encontrados[0]);
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  async function registrar() {
    setOcupado(true);
    setError(null);
    setMensaje(null);

    try {
      let producto = elegido;
      if (!producto) {
        producto = await api.crearProducto({
          tipo,
          color,
          alto_cm: Number(medidas.alto_cm),
          ancho_cm: Number(medidas.ancho_cm),
          largo_cm: Number(medidas.largo_cm),
          modelo: "",
        });
      }

      await api.movimiento({ producto: producto.id, cantidad: Number(cantidad), tipo: entrada });
      setMensaje(`Entraron ${cantidad}. ${producto.nombre} quedó actualizado.`);
      setParecidos(null);
      setElegido(null);
      setCantidad("1");
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  return (
    <div className="contenedor estrecho">
      <nav className="barra">
        <a href="/" className="link-fino">Ver catálogo</a>
        <a href="/conteo" className="link-fino">Contar</a>
        <span>{perfil.nombre}</span>
        <button className="link-fino" onClick={onSalir}>Salir</button>
      </nav>

      <header className="cabecera">
        <h1>¿Qué llegó?</h1>
        <p>Buscá primero: si el artículo ya existe, se suma cantidad en lugar de crear otro.</p>
      </header>

      <section className="formulario" aria-label="Datos del artículo">
        <label>
          Categoría
          <select value={categoria} onChange={(e) => setCategoria(e.target.value ? Number(e.target.value) : "")}>
            <option value="">Elegí…</option>
            {categorias.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </label>

        <label>
          Tipo de artículo
          <select value={tipo} onChange={(e) => setTipo(e.target.value ? Number(e.target.value) : "")} disabled={!tipos.length}>
            <option value="">{tipos.length ? "Elegí…" : "Primero la categoría"}</option>
            {tipos.map((t) => (
              <option key={t.id} value={t.id}>{t.nombre}</option>
            ))}
          </select>
        </label>

        <label>
          Color
          <select value={color} onChange={(e) => setColor(e.target.value)}>
            <option value="">Elegí…</option>
            {colores.map((c) => (
              <option key={c.valor} value={c.valor}>{c.etiqueta}</option>
            ))}
          </select>
        </label>

        <fieldset className="medidas">
          <legend>Medidas en cm</legend>
          {(["alto_cm", "ancho_cm", "largo_cm"] as const).map((campo) => (
            <label key={campo}>
              {campo === "alto_cm" ? "Alto" : campo === "ancho_cm" ? "Ancho" : "Largo"}
              <input
                type="number"
                inputMode="numeric"
                min={1}
                value={medidas[campo]}
                onChange={(e) => setMedidas({ ...medidas, [campo]: e.target.value })}
              />
            </label>
          ))}
        </fieldset>

        <button className="secundario" type="button" onClick={buscar} disabled={!completo || ocupado}>
          Buscar
        </button>
      </section>

      {parecidos !== null && (
        <section className="resultado" aria-live="polite">
          {parecidos.length > 0 ? (
            <>
              <h2>{parecidos.length === 1 ? "Ya existe" : "Parecidos"}</h2>
              <ul className="lista">
                {parecidos.map((p) => (
                  <li key={p.id}>
                    <button
                      type="button"
                      className={elegido?.id === p.id ? "opcion activa" : "opcion"}
                      onClick={() => setElegido(p)}
                    >
                      <strong>{p.nombre}</strong>
                      <span>{p.id_visible}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p>No existe todavía. Se va a crear uno nuevo.</p>
          )}
        </section>
      )}

      {parecidos !== null && (
        <section className="formulario" aria-label="Registrar la entrada">
          <label>
            Cantidad
            <input
              type="number"
              inputMode="numeric"
              min={1}
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
            />
          </label>
          <label>
            ¿De dónde viene?
            <select value={entrada} onChange={(e) => setEntrada(e.target.value as Entrada)}>
              <option value="entrada_compra">Compra a un proveedor</option>
              <option value="entrada_inventario_inicial">Mercadería que ya estaba</option>
            </select>
          </label>
          <button className="principal" type="button" onClick={registrar} disabled={ocupado || !cantidad}>
            {ocupado ? "Registrando…" : elegido ? "Sumar a este artículo" : "Crear y registrar"}
          </button>
        </section>
      )}

      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </div>
  );
}
