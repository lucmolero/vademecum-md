import { createReadStream, existsSync, readFileSync, statSync } from 'node:fs';
import { extname, resolve, sep } from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath, URL } from 'node:url';

const libraryDist = resolve(fileURLToPath(new URL('../biblioteca/dist/', import.meta.url)));
const librarySource = resolve(fileURLToPath(new URL('../biblioteca/src/', import.meta.url)));
const mimeTypes: Record<string, string> = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp',
  '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.ico': 'image/x-icon',
};

function serveBuiltLibraryInDev() {
  return {
    name: 'serve-built-vademecum-library',
    configureServer(server: import('vite').ViteDevServer) {
      server.middlewares.use((request, response, next) => {
        const pathname = new URL(request.url || '/', 'http://localhost').pathname;
        const previewAlias = pathname === '/biblioteca-demo' || pathname.startsWith('/biblioteca-demo/');
        const libraryRoute = pathname === '/biblioteca' || pathname.startsWith('/biblioteca/');
        if (!previewAlias && !libraryRoute) return next();
        if (!['GET', 'HEAD'].includes(request.method || 'GET')) return next();

        let relativePath: string;
        try {
          const routePrefix = previewAlias ? '/biblioteca-demo' : '/biblioteca';
          relativePath = decodeURIComponent(pathname.slice(routePrefix.length)).replace(/^[/\\]+/, '');
        } catch {
          response.statusCode = 400;
          return response.end('Bad request');
        }
        const sourceFile = resolve(librarySource, relativePath || 'index.html');
        let file = previewAlias && existsSync(sourceFile) ? sourceFile : resolve(libraryDist, relativePath || 'index.html');
        const allowedPath = file === librarySource || file.startsWith(`${librarySource}${sep}`)
          || file === libraryDist || file.startsWith(`${libraryDist}${sep}`);
        if (!allowedPath) {
          response.statusCode = 403;
          return response.end('Forbidden');
        }
        if (existsSync(file) && statSync(file).isDirectory()) file = resolve(file, 'index.html');
        if (!existsSync(file) || !statSync(file).isFile()) {
          response.statusCode = 404;
          return response.end('Biblioteca não compilada. Execute npm run build no projeto biblioteca.');
        }
        response.statusCode = 200;
        response.setHeader('Content-Type', mimeTypes[extname(file).toLowerCase()] || 'application/octet-stream');
        response.setHeader('Cache-Control', 'no-cache');
        if (request.method === 'HEAD') return response.end();
        if (previewAlias && file === resolve(librarySource, 'index.html')) {
          const publishedLibrary = 'https://lucmolero.github.io/vademecum-md/biblioteca/';
          const html = readFileSync(file, 'utf8')
            .replace(/<meta[^>]+http-equiv=["']Content-Security-Policy["'][^>]*>/i, '')
            .replace(/href=["']\.\/(style|library|glass|home-visual)\.css["']/g, (_match, stylesheet: string) => `href="${publishedLibrary}${stylesheet}.css"`);
          response.setHeader('Content-Length', Buffer.byteLength(html));
          return response.end(html);
        }
        return createReadStream(file).pipe(response);
      });
    },
  };
}

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss(), serveBuiltLibraryInDev()],
  server: { fs: { allow: [resolve(fileURLToPath(new URL('../../', import.meta.url)))] } },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      cn: fileURLToPath(new URL('./src/cn.ts', import.meta.url)),
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
});
