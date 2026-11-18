import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El build se sirve desde Django en el mismo origen: sin CORS y un solo despliegue.
export default defineConfig({
  plugins: [react()],
  base: "/static/",
  build: { outDir: "dist", assetsDir: "assets" },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/media": "http://localhost:8000",
    },
  },
});
