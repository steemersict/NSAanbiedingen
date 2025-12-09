import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  // In Tauri, the frontend is served from file:// URLs
  // So we need to output static files without any server
  output: "static",
  integrations: [react(), tailwind()],
  build: {
    format: "file",
  },
  // For development with Tauri dev server
  server: {
    port: 4321,
    strictPort: false,
  },
  vite: {
    build: {
      target: "esnext",
    },
  },
});
