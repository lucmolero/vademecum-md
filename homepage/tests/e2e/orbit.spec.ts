import { expect, test } from '@playwright/test';

for (const width of [1440, 390]) {
  test(`orbit loads all nine working previews and retains their state at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    const errors: string[] = [];
    const documents: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
      if (request.isNavigationRequest() && request.url().includes('preview=')) documents.push(request.url());
      expect(request.url()).not.toMatch(/\/(catalog|search-index)\.json/);
    });
    await page.route('**/graph/viewer/index.html?home-hero=1', route => route.fulfill({ contentType: 'text/html', body: '<html></html>' }));
    await page.goto('/');
    const orbit = page.locator('#recursos');
    await orbit.waitFor({ state: 'attached' });
    await expect(page.locator('[data-slot=home-intro]')).toHaveCount(0);
    // Preload before the orbit enters the viewport, not after a card rotates forward.
    await orbit.evaluate(section => window.scrollTo(0, section.getBoundingClientRect().top + scrollY - innerHeight - 250));
    await expect(orbit.locator('iframe')).toHaveCount(9);
    await expect(orbit.locator('[data-preview-state=ready]')).toHaveCount(9);
    const frame = (title: string) => page.frameLocator(`iframe[title="Prévia interativa: ${title}"]`);
    await expect(frame('Acervo').locator('.shelf-book-open').first()).toBeAttached();
    await expect(frame('Busca integral').locator('.shelf-full-result').first()).toContainText('igualdade');
    await expect(frame('Sumário do leitor').locator('#toc button').first()).toBeAttached();
    await expect(frame('Marcadores').locator('.mark-button')).toContainText('Art. 5º');
    await expect(frame('Anotações').locator('.note-card')).toContainText('Revisar os princípios');
    await expect(frame('Citação').locator('#copy-citation')).toBeAttached();
    await expect(frame('Procedência').locator('#source-details')).toContainText('Conteúdo demonstrativo');
    await expect(frame('Aparência').locator('#appearance')).not.toHaveAttribute('hidden');
    await expect(frame('Retomar leitura').locator('.document-content')).toContainText('Princípios');
    await orbit.evaluate(section => window.scrollTo(0, section.getBoundingClientRect().top + scrollY + section.clientHeight - innerHeight));
    if (width < 768) {
      const next = page.getByRole('button', { name: 'Próxima prévia' });
      await expect(orbit.locator('[inert]').filter({ has: next })).toHaveCount(0);
      for (let index = 0; index < 7; index++) {
        const button = await next.boundingBox();
        expect(button).not.toBeNull();
        await page.mouse.click(button!.x + button!.width / 2, button!.y + button!.height / 2);
        await expect(orbit.locator('[aria-live]')).toContainText(`${String(index + 2).padStart(2, '0')} / 09`);
      }
    }
    // The scroll spring transforms the iframe itself; wait for its final pose.
    await expect.poll(() => page.locator('iframe[title="Prévia interativa: Aparência"]').evaluate(frame => frame.closest('[data-slot=orbit-card]')!.parentElement!.style.transform)).toMatch(width < 768 ? /^translate\(0px, 68px\)$/ : /^translate\([^)]*\)$/);
    const viewportCenter = await orbit.evaluate(section => {
      const bounds = section.getBoundingClientRect();
      return bounds.x + bounds.width / 2;
    });
    await expect.poll(async () => {
      const bounds = await page.locator('iframe[title="Prévia interativa: Aparência"]').boundingBox();
      return bounds ? Math.abs(bounds.x + bounds.width / 2 - viewportCenter) : Infinity;
    }).toBeLessThan(1);
    const themeButton = await frame('Aparência').locator('button[data-theme=dark]').boundingBox();
    expect(themeButton).not.toBeNull();
    expect(themeButton!.x).toBeGreaterThanOrEqual(0);
    expect(themeButton!.x + themeButton!.width).toBeLessThanOrEqual(width);
    expect(themeButton!.y).toBeGreaterThanOrEqual(0);
    expect(themeButton!.y + themeButton!.height).toBeLessThanOrEqual(900);
    const scrollBeforeClick = await page.evaluate(() => scrollY);
    // Locator auto-scroll can move the sticky stage; exercise a real on-screen click.
    await page.mouse.click(themeButton!.x + themeButton!.width / 2, themeButton!.y + themeButton!.height / 2);
    await expect(frame('Aparência').locator('html')).toHaveAttribute('data-theme', 'dark');
    expect(await page.evaluate(() => scrollY)).toBeCloseTo(scrollBeforeClick, 0);
    await page.evaluate(() => window.scrollTo(0, 0));
    await orbit.evaluate(section => window.scrollTo(0, section.getBoundingClientRect().top + scrollY + section.clientHeight - innerHeight));
    await expect(frame('Aparência').locator('html')).toHaveAttribute('data-theme', 'dark');
    expect(documents).toHaveLength(9);
    expect(errors).toEqual([]);
    expect(await page.evaluate(() => Object.keys(localStorage).filter(key => key.startsWith('biblioteca:')))).toEqual([]);
  });
}

test('a failed preview offers retry and recovers without reloading the homepage', async ({ page }) => {
  await page.route('**/biblioteca-demo/?preview=catalog**', route => route.fulfill({ contentType: 'text/html', body: '<html></html>' }));
  await page.goto('/#recursos');
  const catalog = page.locator('[data-slot=orbit-card]').filter({ hasText: /^Acervo/ });
  const retry = catalog.getByRole('button', { name: 'Tentar novamente' });
  await expect(retry).toBeVisible({ timeout: 20000 });
  await page.unroute('**/biblioteca-demo/?preview=catalog**');
  await retry.click();
  await expect(catalog.locator('[data-preview-state=ready]')).toHaveCount(1);
  await expect(catalog.locator('.library-mini-preview-loading')).toHaveCount(0);
});
