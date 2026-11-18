export type Categoria = { id: number; nombre: string };
export type Tipo = { id: number; nombre: string; categoria: number };
export type Color = { valor: string; etiqueta: string };

export type Producto = {
  id: number;
  id_visible: string;
  nombre: string;
  categoria: string;
  tipo: string;
  color: string;
  medidas: string;
  stock: number;
  precio_venta: string | null;
  imagen: string | null;
};

export type Catalogo = { categorias: { nombre: string; total: number }[]; productos: Producto[] };
export type Perfil = { id: number; username: string; nombre: string; rol: string };
export type Movimiento = { id: number; producto: number; cantidad: number; tipo: string };

function csrf(): string {
  const par = document.cookie
    .split("; ")
    .find((fila) => fila.startsWith("csrftoken="));
  return par ? decodeURIComponent(par.split("=")[1]) : "";
}

async function pedir<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const respuesta = await fetch(ruta, {
    ...opciones,
    headers: { Accept: "application/json", ...(opciones.headers ?? {}) },
    credentials: "same-origin",
  });
  if (respuesta.status === 204) return undefined as T;
  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const detalle = cuerpo?.detail ?? `Error ${respuesta.status}`;
    throw new Error(detalle);
  }
  return cuerpo as T;
}

export function enviar<T>(ruta: string, datos: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
    body: JSON.stringify(datos),
  });
}

export const traer = pedir;

export const api = {
  me: () => pedir<Perfil>("/api/auth/me/"),
  login: (username: string, password: string) =>
    enviar<Perfil>("/api/auth/login/", { username, password }),
  logout: () => enviar<void>("/api/auth/logout/", {}),
  categorias: () => pedir<Categoria[]>("/api/categorias/"),
  tipos: (categoria?: number) =>
    pedir<Tipo[]>(`/api/tipos/${categoria ? `?categoria=${categoria}` : ""}`),
  colores: () => pedir<Color[]>("/api/colores/"),
  catalogo: (categoria?: string) =>
    pedir<Catalogo>(`/api/catalogo/${categoria ? `?categoria=${encodeURIComponent(categoria)}` : ""}`),
  buscar: (filtros: Record<string, string | number>) => {
    const query = new URLSearchParams(
      Object.entries(filtros)
        .filter(([, v]) => v !== "" && v !== undefined && v !== null)
        .map(([k, v]) => [k, String(v)]),
    );
    return pedir<Producto[]>(`/api/productos/buscar/?${query}`);
  },
  crearProducto: (datos: Record<string, unknown>) => enviar<Producto>("/api/productos/", datos),
  clientes: () => pedir<{ id: number; nombre: string; ciudad: string; habilitado_cuenta_corriente: boolean }[]>("/api/clientes/"),
  vender: (datos: Record<string, unknown>) => enviar<{ id: number; total: string; detalle: { nombre: string; cantidad: number; subtotal: string }[] }>("/api/ventas/", datos),
  movimiento: (datos: Record<string, unknown>) => enviar<Movimiento>("/api/movimientos/", datos),
};
