// defineConfig comes from vitest/config, not vite. vitest/config re-exports
// vite's defineConfig with the `test` key added to the type. Importing it from
// "vite" instead makes tsc reject the `test` block, which is how the type-check
// hole first announced itself in this example.
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
