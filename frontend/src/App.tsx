import { useEffect, useState } from "react";
import { api, type Perfil } from "./api";
import CatalogoPagina from "./pages/Catalogo";
import Login from "./pages/Login";
import Cuentas from "./pages/Cuentas";
import Deposito from "./pages/Deposito";
import Inicio from "./pages/Inicio";
import Precios from "./pages/Precios";
import Recepcion from "./pages/Recepcion";
import Venta from "./pages/Venta";

function rutaActual(): string {
  return window.location.pathname.replace(/\/+$/, "") || "/";
}

export default function App() {
  const [ruta, setRuta] = useState(rutaActual);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [verificando, setVerificando] = useState(true);

  useEffect(() => {
    const alCambiar = () => setRuta(rutaActual());
    window.addEventListener("popstate", alCambiar);
    return () => window.removeEventListener("popstate", alCambiar);
  }, []);

  useEffect(() => {
    api.me()
      .then(setPerfil)
      .catch(() => setPerfil(null))
      .finally(() => setVerificando(false));
  }, []);

  async function salir() {
    await api.logout().catch(() => undefined);
    setPerfil(null);
  }

  if (ruta.startsWith("/cuentas")) {
    if (verificando) return <p className="contenedor estrecho estado">Verificando sesión…</p>;
    if (!perfil) return <Login onEntrar={setPerfil} />;
    return <Cuentas perfil={perfil} onSalir={salir} />;
  }

  if (ruta.startsWith("/deposito")) {
    if (verificando) return <p className="contenedor estrecho estado">Verificando sesión…</p>;
    if (!perfil) return <Login onEntrar={setPerfil} />;
    return <Deposito perfil={perfil} onSalir={salir} />;
  }

  if (ruta.startsWith("/precios")) {
    if (verificando) return <p className="contenedor estrecho estado">Verificando sesión…</p>;
    if (!perfil) return <Login onEntrar={setPerfil} />;
    return <Precios perfil={perfil} onSalir={salir} />;
  }

  if (ruta.startsWith("/venta")) {
    if (verificando) return <p className="contenedor estrecho estado">Verificando sesión…</p>;
    if (!perfil) return <Login onEntrar={setPerfil} />;
    return <Venta perfil={perfil} onSalir={salir} />;
  }

  if (ruta.startsWith("/recepcion")) {
    if (verificando) return <p className="contenedor estrecho estado">Verificando sesión…</p>;
    if (!perfil) return <Login onEntrar={setPerfil} />;
    return <Recepcion perfil={perfil} onSalir={salir} />;
  }

  if (ruta.startsWith("/catalogo")) {
    return (
      <main>
        <CatalogoPagina />
        <p className="contenedor" style={{ paddingBottom: "2rem" }}>
          <a className="link-fino" href="/">Volver al inicio</a>
        </p>
      </main>
    );
  }

  return <Inicio />;
}
