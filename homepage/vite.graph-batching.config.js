import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { defineConfig } from 'vite';

const entry = resolve(fileURLToPath(new URL('./src/graph-batching.js', import.meta.url)));

export default defineConfig({
  configFile: false,
  publicDir: false,
  build: {
    lib: {
      entry,
      formats: ['es'],
      fileName: () => 'graph-batching.js',
    },
    outDir: 'public/graph/viewer/vendor',
    emptyOutDir: false,
    minify: 'oxc',
    sourcemap: false,
  },
});
