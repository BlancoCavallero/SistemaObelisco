import LogoObelisco from "../components/LogoObelisco";

export default function Inicio() {
  return (
    <main className="inicio">
      <div className="inicio-marca">
        <LogoObelisco className="obelisco" />
        <h1 className="inicio-nombre">Obelisco</h1>
        <p className="inicio-bajada">Muebles, electrodomésticos, blanquería y todo para la casa.</p>
        <p className="inicio-lugar">Tres Lomas · Provincia de Buenos Aires</p>
      </div>

      <nav className="inicio-acciones" aria-label="Acciones">
        <a className="boton-principal" href="/catalogo">Ver el catálogo</a>
        <a className="boton-secundario" href="/recepcion">Personal</a>
      </nav>
    </main>
  );
}
