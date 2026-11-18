import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En produccion el build lo sirve Django desde /static/ (mismo origen, sin CORS).
// En desarrollo el base tiene que ser "/", o el servidor de Vite responde 302 a
// /static/ y las rutas del SPA dan 404.
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === "build" ? "/static/" : "/",
  build: { outDir: "dist", assetsDir: "assets" },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/media": "http://localhost:8000",
    },
  },
}));
