import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  publicDir: false,
  server: {
    host: "0.0.0.0",
    port: 5173,
    fs: { deny: ["**/.git/**", "**/.env*", "**/*.{crt,pem}", "**/public/data/**"] },
    proxy: { "/api": process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000" },
  },
  build: {
    outDir: "dist",
  },
});
