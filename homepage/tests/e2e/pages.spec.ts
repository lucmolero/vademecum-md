import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const wcagTags = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'];

async function expectNoHorizontalOverflow(page: import('@playwright/test').Page) {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content, JSON.stringify(dimensions)).toBeLessThanOrEqual(dimensions.viewport + 1);
}

async function expectWcag(page: import('@playwright/test').Page, scope: string) {
  const results = await new AxeBuilder({ page }).include(scope).withTags(wcagTags).analyze();
  expect(results.violations, JSON.stringify(results.violations.map(({ id, impact, nodes }) => ({
    id,
    impact,
    targets: nodes.map(node => node.target),
  })), null, 2)).toEqual([]);
}

test('homepage, official library and reader work at desktop and mobile widths', async ({ page }) => {
  test.setTimeout(90_000);
  const frontendErrors: string[] = [];
  page.on('pageerror', error => frontendErrors.push(error.message));
  await page.route('http://127.0.0.1:8770/viewer/**', route => route.fulfill({
    status: 200,
    contentType: 'text/html',
    body: '<!doctype html><html lang="pt-BR"><body><main aria-label="Grafo de citações"></main></body></html>',
  }));

  await page.goto('/');
  await expect(page).toHaveTitle(/vademecum\.md/i);
  await expect(page.locator('main#conteudo')).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip-link')).toBeFocused();
  await expectNoHorizontalOverflow(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await expectNoHorizontalOverflow(page);
  await expectWcag(page, '#inicio');

  await page.setViewportSize({ width: 1280, height: 900 });
  await page.locator('header a[href="./biblioteca/"]:visible').click();
  await expect(page).toHaveURL(/\/biblioteca\/$/);
  await expect(page.locator('.shelf-book-open').first()).toBeVisible();
  const catalog = await page.evaluate(async () => {
    const response = await fetch('catalog.json');
    const documents = await response.json();
    return { status: response.status, documents };
  });
  expect(catalog.status).toBe(200);
  expect(catalog.documents).toHaveLength(375);
  expect(catalog.documents.every((document: { collection: string }) => document.collection === 'vademecum')).toBe(true);
  await expectWcag(page, '#library');
  await expectNoHorizontalOverflow(page);

  for (const view of ['statistics', 'notes', 'settings', 'info']) {
    await page.locator(`[data-view="${view}"]`).click();
    await expect(page.locator('.shelf-content h1').first()).toBeVisible();
    if (view === 'statistics') await expect(page.locator('.shelf-content .shelf-subtitle')).toContainText('no acervo');
    await expectNoHorizontalOverflow(page);
    await expectWcag(page, '#library');
  }
  await page.locator('[data-view="books"]').click();
  await page.locator('[data-action="theme"]').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expectWcag(page, '#library');
  await page.locator('[data-action="theme"]').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');

  await page.locator('[data-view="search-all"]').click();
  await page.getByRole('searchbox', { name: 'Buscar no texto de todos os documentos' }).fill('princípios');
  await expect(page.locator('.shelf-full-result').first()).toBeVisible({ timeout: 30_000 });
  await expect(page.locator('.shelf-full-result').first()).toContainText('princípios', { ignoreCase: true });

  await page.locator('[data-view="books"]').click();
  await page.locator('article[data-book-id="br-federal-constituicao-1988"] > .shelf-book-open').click();
  await expect(page).toHaveURL(/documento=br-federal-constituicao-1988/);
  await expect(page.getByRole('heading', { name: 'PREÂMBULO', exact: true })).toBeVisible();
  await page.goto('/biblioteca/#documento=br-federal-constituicao-1988&artigo=art-1o');
  await expect(page).toHaveURL(/artigo=art-1o/);
  await expect(page.locator('.document-content #art-1o')).toBeVisible();
  await expectWcag(page, '#reading');

  await page.setViewportSize({ width: 360, height: 780 });
  await expectNoHorizontalOverflow(page);
  await expectWcag(page, '#reading');

  await page.goto('/biblioteca/');
  await expect(page.locator('.shelf-book-open').first()).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await expectWcag(page, '#library');
  for (const view of ['statistics', 'notes', 'settings', 'info']) {
    await page.locator(`[data-view="${view}"]`).click();
    await expect(page.locator('.shelf-content h1').first()).toBeVisible();
    await expectNoHorizontalOverflow(page);
    await expectWcag(page, '#library');
  }

  await page.goto('/#assistente');
  await expect(page.locator('[data-slot="home-ai"]')).toBeVisible();
  await expect(page.locator('.live-preview-stage')).toBeVisible({ timeout: 20_000 });
  await expect(page.locator('.live-library-panel .shelf-shell')).toBeVisible();
  await expect(page.locator('.live-reader-panel #viewport')).toBeVisible();
  await page.getByRole('tablist', { name: 'Demonstrações para humanos e agentes' }).getByRole('tab', { name: 'Para agentes' }).click();
  await expect(page.getByRole('tab', { name: 'Princípios' })).toBeVisible();
  await expectWcag(page, '#assistente');

  expect(frontendErrors).toEqual([]);
});
