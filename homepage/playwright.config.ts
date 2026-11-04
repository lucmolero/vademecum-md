import { defineConfig } from '@playwright/test';

const port = Number(process.env.PLAYWRIGHT_PORT || 8787);
if (!Number.isInteger(port) || port < 1024 || port > 65535) {
  throw new Error('PLAYWRIGHT_PORT must be an integer from 1024 to 65535');
}

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  // WebGL and axe share a software GPU in CI; serialize complete journeys.
  workers: 1,
  reporter: 'list',
  timeout: 45_000,
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    {
      name: 'webkit',
      // Node dragging uses Chromium's native touch protocol in graph.spec.ts.
      testIgnore: '**/graph.spec.ts',
      use: { browserName: 'webkit' },
    },
  ],
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    viewport: { width: 1440, height: 900 },
    reducedMotion: 'reduce',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: `npm run dev -- --port ${port} --strictPort`,
    url: `http://127.0.0.1:${port}/`,
    // A shared machine can have an older checkout on this port.
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
