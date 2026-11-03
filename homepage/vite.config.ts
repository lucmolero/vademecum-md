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

function libraryMiddleware(allowSourcePreview: boolean) {
  return (request: import('node:http').IncomingMessage, response: import('node:http').ServerResponse, next: (error?: Error) => void) => {
    const pathname = new URL(request.url || '/', 'http://localhost').pathname;
    const previewAlias = pathname === '/biblioteca-demo' || pathname.startsWith('/biblioteca-demo/');
    const libraryRoute = pathname === '/biblioteca' || pathname.startsWith('/biblioteca/');
    if ((!previewAlias || !allowSourcePreview) && !libraryRoute) return next();
    if (!['GET', 'HEAD'].includes(request.method || 'GET')) return next();

    let relativePath: string;
    try {
      const routePrefix = previewAlias && allowSourcePreview ? '/biblioteca-demo' : '/biblioteca';
      relativePath = decodeURIComponent(pathname.slice(routePrefix.length)).replace(/^[/\\]+/, '');
    } catch {
      response.statusCode = 400;
      return response.end('Bad request');
    }
    const sourceFile = resolve(librarySource, relativePath || 'index.html');
    let file = previewAlias && allowSourcePreview && existsSync(sourceFile)
      ? sourceFile
      : resolve(libraryDist, relativePath || 'index.html');
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
    if (previewAlias && allowSourcePreview && file === resolve(librarySource, 'index.html')) {
      const html = readFileSync(file, 'utf8')
        .replace(/<meta[^>]+http-equiv=["']Content-Security-Policy["'][^>]*>/i, '');
      response.setHeader('Content-Length', Buffer.byteLength(html));
      return response.end(html);
    }
    return createReadStream(file).pipe(response);
  };
}

function serveBuiltLibraryInDev() {
  return {
    name: 'serve-built-vademecum-library',
    configureServer(server: import('vite').ViteDevServer) {
      server.middlewares.use(libraryMiddleware(true));
    },
    configurePreviewServer(server: import('vite').PreviewServer) {
      // `vite preview` serves homepage/dist only; Pages composes the library
      // separately. Serve the sibling library build locally at the same route.
      server.middlewares.use(libraryMiddleware(false));
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
