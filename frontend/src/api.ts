export type Categoria = { nombre: string; total: number };

export type Producto = {
  id: number;
  id_visible: string;
  nombre: string;
  categoria: string;
  tipo: string;
  color: string;
  medidas: string;
  stock: number;
  imagen: string | null;
};

export type Catalogo = { categorias: Categoria[]; productos: Producto[] };

export async function traerCatalogo(categoria?: string): Promise<Catalogo> {
  const url = new URL("/api/catalogo/", window.location.origin);
  if (categoria) url.searchParams.set("categoria", categoria);

  const respuesta = await fetch(url, { headers: { Accept: "application/json" } });
  if (!respuesta.ok) {
    throw new Error(`No se pudo cargar el catálogo (${respuesta.status})`);
  }
  return (await respuesta.json()) as Catalogo;
}
