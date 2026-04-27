import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/tests/setup.js",
  },
  resolve: {
    alias: {
      quasar: fileURLToPath(
        new URL("./node_modules/quasar/dist/quasar.client.js", import.meta.url)
      ),
    },
  },
});