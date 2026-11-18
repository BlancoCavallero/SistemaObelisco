import { useState } from "react";
import { api, type Perfil } from "../api";

export default function Login({ onEntrar }: { onEntrar: (perfil: Perfil) => void }) {
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function entrar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      onEntrar(await api.login(usuario.trim(), clave));
    } catch (causa) {
      setError((causa as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="contenedor estrecho">
      <header className="cabecera">
        <h1>Entrar</h1>
        <p>Para cargar mercadería necesitás tu usuario.</p>
      </header>
      <form className="formulario" onSubmit={entrar}>
        <label>
          Usuario
          <input
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            autoComplete="username"
            autoCapitalize="none"
            required
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={clave}
            onChange={(e) => setClave(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="principal" type="submit" disabled={enviando}>
          {enviando ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}
