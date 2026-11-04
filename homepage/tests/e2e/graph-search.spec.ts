import { readFileSync } from 'node:fs';
import { expect, test } from '@playwright/test';

test.use({
  viewport: { width: 390, height: 844 },
  hasTouch: true,
  reducedMotion: 'no-preference',
});

test('search result touch activates the controller callback', async ({ page }) => {
  await page.route('**/graph/viewer/index.html?home-hero=1', async route => {
    const html = readFileSync('public/graph/viewer/index.html', 'utf8');
    await route.fulfill({ contentType: 'text/html', body: html.replace(new RegExp('<script[^>]*>.*?</script>', 'gis'), '') });
  });
  await page.goto('/graph/viewer/index.html?home-hero=1');
  await page.evaluate(async () => {
    const toolbar = document.querySelector('.graph-toolbar')!;
    document.body.replaceChildren(toolbar);
    const input = document.querySelector<HTMLInputElement>('#search')!;
    const list = document.querySelector('#suggestions')!;
    const status = document.querySelector('#search-status')!;
    const controllerUrl = new URL('./search-controller.js?v=graph-search-4', location.href).href;
    const { createSearchController } = await import(controllerUrl);
    createSearchController({
      input, list, status,
      load: async () => {
        const index = await fetch('/graph/data/search-index.json.gz?v=audit-1');
        if (index.headers.get('content-encoding')?.includes('gzip')) return index.json();
        return new Response(index.body!.pipeThrough(new DecompressionStream('gzip'))).json();
      },
      select: (id: string) => { document.body.dataset.selectedId = id; },
    });
  });
  for (const [query, id] of [
    ['14.133', 'br-federal-lei_ordinaria-14133-2021'],
    ['constituição', 'br-federal-constituicao-1988'],
  ]) {
    await page.getByRole('combobox').tap({ timeout: 3000 });
    await page.getByRole('combobox').fill(query);
    await page.getByRole('option').first().tap({ timeout: 3000 });
    await expect(page.locator('body')).toHaveAttribute('data-selected-id', id);
    await expect(page.getByRole('combobox')).toHaveAttribute('aria-expanded', 'false');
  }
});
