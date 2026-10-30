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
  const frontendErrors: string[] = [];
  page.on('pageerror', error => frontendErrors.push(error.message));

  await page.goto('/');
  await expect(page).toHaveTitle(/Vademecum/);
  await expect(page.locator('main#conteudo')).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip-link')).toBeFocused();
  await expectNoHorizontalOverflow(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await expectNoHorizontalOverflow(page);
  await expectWcag(page, '#inicio');

  await page.locator('a[href*="biblioteca/"]:visible').first().click();
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

  await page.locator('article[data-book-id="br-federal-constituicao-1988"] > .shelf-book-open').click();
  await expect(page).toHaveURL(/documento=br-federal-constituicao-1988/);
  await expect(page.getByRole('heading', { name: 'PREÂMBULO', exact: true })).toBeVisible();
  await page.goto('/biblioteca/#documento=br-federal-constituicao-1988&artigo=art-1o');
  await expect(page).toHaveURL(/artigo=art-1o/);
  await expect(page.locator('.document-content #art-1o')).toBeVisible();
  await expectWcag(page, '#reading');

  await page.setViewportSize({ width: 360, height: 780 });
  await expectNoHorizontalOverflow(page);
  expect(frontendErrors).toEqual([]);
});
