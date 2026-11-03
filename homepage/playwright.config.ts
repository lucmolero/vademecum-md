import { defineConfig } from '@playwright/test';

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
    baseURL: 'http://127.0.0.1:8787',
    viewport: { width: 1440, height: 900 },
    reducedMotion: 'reduce',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev -- --port 8787',
    url: 'http://127.0.0.1:8787/',
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
