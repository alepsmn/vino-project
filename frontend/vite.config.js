import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
    root: ".",
    build: {
        outDir: "../static/build",
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: resolve(__dirname, "js/main.js"),
                style: resolve(__dirname, "css/main.css"),
            },
            output: {
                entryFileNames: "assets/[name].js",
                assetFileNames: "assets/[name][extname]",
                chunkFileNames: "assets/[name].js"
            }
        }
    }
});
