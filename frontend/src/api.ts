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
export type FilaConteo = {
  producto: number;
  id_visible: string;
  nombre: string;
  esperado: number;
  en_caja: number;
  listo: number;
  vendidas_sin_entregar: number;
};
export type VentaPendiente = {
  id: number;
  fecha: string;
  cliente: string;
  ciudad: string;
  lineas: { producto: number; nombre: string; cantidad: number }[];
};

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
    const detalle = cuerpo?.detail ?? primerError(cuerpo) ?? `Error ${respuesta.status}`;
    throw new Error(detalle);
  }
  return cuerpo as T;
}

// Un 400 de validacion trae {campo: "mensaje"}: mostrarlo, no un "Error 400" mudo.
function primerError(cuerpo: unknown): string | null {
  if (!cuerpo || typeof cuerpo !== "object") return null;
  for (const valor of Object.values(cuerpo as Record<string, unknown>)) {
    if (typeof valor === "string") return valor;
    if (Array.isArray(valor) && typeof valor[0] === "string") return valor[0];
  }
  return null;
}

export function enviar<T>(ruta: string, datos: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
    body: JSON.stringify(datos),
  });
}

// PATCH para actualizaciones parciales: la ruta de detalle acepta patch, no post.
export function parchear<T>(ruta: string, datos: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: "PATCH",
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
  productos: () => pedir<Producto[]>("/api/productos/"),
  faltantes: () => pedir<Producto[]>("/api/precios/faltantes/"),
  cargarPrecios: (vigente_desde: string, valores: { producto: number; valor: string }[]) =>
    enviar<{ creados: number }>("/api/precios/", { vigente_desde, valores }),
  stock: () =>
    pedir<
      { producto: number; id_visible: string; nombre: string; total: number; en_caja: number; listo: number }[]
    >("/api/stock/"),
  stockUbicaciones: (almacen?: number) =>
    pedir<{
      almacenes: { id: number | null; codigo: string; nombre: string; total: number }[];
      filas: {
        producto: number;
        id_visible: string;
        nombre: string;
        estado: string;
        posicion: number | null;
        etiqueta: string;
        cantidad: number;
      }[];
    }>(`/api/stock/ubicaciones/${almacen ? `?almacen=${almacen}` : ""}`),
  posiciones: () => pedir<{ id: number; etiqueta: string; almacen: number }[]>("/api/posiciones/"),
  armar: (producto: number, cantidad: number) =>
    enviar<{ referencia: string; armado: number }>("/api/movimientos/armar/", { producto, cantidad }),
  transferir: (datos: { producto: number; cantidad: number; desde: number; hasta: number }) =>
    enviar<{ referencia: string; transferido: number }>("/api/movimientos/transferir/", datos),
  producto: (id: number) => pedir<Producto>(`/api/productos/${id}/`),
  movimientosDe: (id: number) =>
    pedir<{
      producto: { id: number; id_visible: string; nombre: string };
      total: number;
      movimientos: {
        id: number;
        fecha: string;
        tipo: string;
        cantidad: number;
        estado: string;
        motivo: string;
        referencia: string;
        usuario: string;
        saldo_acumulado: number;
      }[];
    }>(`/api/productos/${id}/movimientos/`),
  preciosDe: (id: number) =>
    pedir<{ valor: string; vigente_desde: string }[]>(`/api/productos/${id}/precios/`),
  clientes: () =>
    pedir<
      { id: number; nombre: string; ciudad: string; habilitado_cuenta_corriente: boolean }[]
    >("/api/clientes/"),
  crearCliente: (datos: {
    nombre: string;
    ciudad: string;
    direccion?: string;
    telefono?: string;
    habilitado_cuenta_corriente: boolean;
  }) => enviar<{ id: number }>("/api/clientes/", datos),
  cuentaDe: (id: number) =>
    pedir<{
      cliente: { id: number; nombre: string; ciudad: string };
      saldo: string;
      vencido: string;
      movimientos: {
        id: number;
        tipo: string;
        monto: string;
        vencimiento: string | null;
        motivo: string;
        fecha: string;
      }[];
    }>(`/api/clientes/${id}/cuenta/`),
  registrarPago: (id: number, monto: string, motivo = "") =>
    enviar<{ saldo: string }>(`/api/clientes/${id}/cuenta/pagos/`, { monto, motivo }),
  proveedores: () =>
    pedir<
      {
        id: number;
        nombre: string;
        canal: string;
        contacto: string;
        telefono: string;
        email: string;
        notas: string;
      }[]
    >("/api/proveedores/"),
  canalesDeProveedor: () => pedir<{ valor: string; etiqueta: string }[]>("/api/proveedores/canales/"),
  crearProveedor: (datos: {
    nombre: string;
    canal: string;
    contacto?: string;
    telefono?: string;
    email?: string;
    notas?: string;
  }) => enviar<{ id: number }>("/api/proveedores/", datos),
  desactivarProveedor: (id: number) =>
    parchear<{ id: number }>(`/api/proveedores/${id}/`, { activo: false }),
  morosos: () =>
    pedir<{ cliente: { id: number; nombre: string; ciudad: string }; vencido: string }[]>(
      "/api/clientes/morosos/",
    ),
  vender: (datos: Record<string, unknown>) => enviar<{ id: number; total: string; detalle: { nombre: string; cantidad: number; subtotal: string }[] }>("/api/ventas/", datos),
  movimiento: (datos: Record<string, unknown>) => enviar<Movimiento>("/api/movimientos/", datos),
  conteoHoja: (q?: string) =>
    pedir<{ filas: FilaConteo[] }>(`/api/conteo/${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  contar: (datos: {
    producto: number;
    contado: number;
    esperado: number;
    estado?: string;
    motivo?: string;
  }) =>
    enviar<{
      esperado: number;
      contado: number;
      ajuste: number;
      // Un renglon por estado tocado: un faltante sale de varias pilas a la vez.
      ajustes: { estado: string; cantidad: number; movimiento: number }[];
    }>("/api/conteo/", datos),
  ventasPendientes: () => pedir<{ ventas: VentaPendiente[] }>("/api/ventas/pendientes/"),
  entregarVenta: (id: number) =>
    enviar<{ venta: number; lineas: number }>(`/api/ventas/${id}/entregar/`, {}),
};
