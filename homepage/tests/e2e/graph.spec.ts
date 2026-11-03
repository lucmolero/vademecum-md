import { expect, test, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

async function diagnostics(page: Page) {
  return page.evaluate(async () => {
    const script = document.querySelector<HTMLScriptElement>('script[data-graph-app]')!;
    return (await import(script.src)).getGraphDiagnostics();
  });
}

for (const device of [
  { name: 'desktop', viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 },
  { name: 'mobile', viewport: { width: 390, height: 844 }, deviceScaleFactor: 3 },
]) {
  test.describe(`official graph ${device.name}`, () => {
    test.use({ viewport: device.viewport, deviceScaleFactor: device.deviceScaleFactor, isMobile: device.name === 'mobile', hasTouch: device.name === 'mobile' });
    test('sharp rendering, keyboard search, contextual selection, resize and idle GPU', async ({ page }) => {
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto('/graph/viewer/index.html?home-hero=1');
      await page.evaluate(() => window.postMessage({ type: 'vademecum-graph-visibility', visible: true }, location.origin));
      await expect.poll(async () => (await diagnostics(page)).ready).toBe(true);
      expect(await diagnostics(page)).toMatchObject({ nodes: 1729, links: 1695, pixelRatio: device.deviceScaleFactor, draggingEnabled: true, arrowHeads: 1695 });
      const initial = await diagnostics(page);
      expect(initial.camera.z).toBeGreaterThan(initial.bounds.z[1]);
      // Reduced motion must stop drawing once the initial scene has settled.
      await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
      const still = (await diagnostics(page)).frame;
      await page.waitForTimeout(180);
      expect((await diagnostics(page)).frame).toBe(still);

      const input = page.getByRole('combobox');
      await input.fill('constituição');
      await expect(input).toHaveAttribute('aria-expanded', 'true');
      await input.press('ArrowDown');
      await expect(input).toHaveAttribute('aria-activedescendant', 'graph-option-0');
      await input.press('Enter');
      await expect.poll(async () => (await diagnostics(page)).selectedId).toBe('br-federal-constituicao-1988');
      await expect(page.getByRole('link', { name: /^Abrir no leitor do VadeMecum MD/ })).toHaveAttribute('target', '_top');
      await expect(page.locator('#details')).toBeVisible();
      await page.getByRole('button', { name: 'Mudar para tema claro' }).click();
      await expect(page.locator('body')).toHaveAttribute('data-theme', 'light');
      expect((await diagnostics(page)).selectedId).toBe('br-federal-constituicao-1988');
      await page.setViewportSize({ width: device.viewport.width, height: device.viewport.height - 160 });
      await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      const accessibility = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      expect(accessibility.violations.map(item => ({ id: item.id, targets: item.nodes.map(node => node.target) }))).toEqual([]);
      const nodePosition = () => page.evaluate(async () => (await import(document.querySelector<HTMLScriptElement>('script[data-graph-app]')!.src)).getNodePosition('br-federal-constituicao-1988'));
      const before = await nodePosition();
      if (device.name === 'mobile') {
        const touch = await page.context().newCDPSession(page);
        await touch.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: before.screenX, y: before.screenY }] });
        for (let step = 1; step <= 10; step++) {
          await touch.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: before.screenX + step * 4, y: before.screenY + step * 2 }] });
        }
        await touch.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
        await touch.detach();
      } else {
        await page.mouse.move(before.screenX, before.screenY);
        await expect(page.locator('.graph-tooltip')).toBeVisible();
        await page.mouse.down();
        await page.mouse.move(before.screenX + 50, before.screenY + 25, { steps: 10 });
        await page.mouse.up();
      }
      await expect.poll(async () => {
        const after = await nodePosition();
        return Math.hypot(after.x - before.x, after.y - before.y, after.z - before.z);
      }).toBeGreaterThan(1);
      await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
      const restingAfterDrag = (await diagnostics(page)).frame;
      await page.waitForTimeout(180);
      expect((await diagnostics(page)).frame).toBe(restingAfterDrag);
      await page.getByRole('button', { name: 'Fechar detalhes', exact: true }).click();
      await expect(page.locator('#details')).toBeHidden();
      await expect.poll(async () => (await diagnostics(page)).selectedId).toBe(null);
      await page.getByRole('button', { name: 'Reenquadrar o grafo' }).click();
      await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
      expect(errors).toEqual([]);
    });
  });
}

test('rotation can pause and resume, and hidden embeds stop drawing', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.goto('/graph/viewer/index.html?home-hero=1');
  await page.evaluate(() => window.postMessage({ type: 'vademecum-graph-visibility', visible: true }, location.origin));
  await expect.poll(async () => (await diagnostics(page)).ready).toBe(true);
  await page.getByRole('button', { name: 'Pausar rotação' }).click();
  await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
  await page.getByRole('button', { name: 'Ativar rotação' }).click();
  await expect.poll(async () => (await diagnostics(page)).rendering).toBe(true);
  await page.evaluate(() => window.postMessage({ type: 'vademecum-graph-visibility', visible: false }, location.origin));
  await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
  const frame = (await diagnostics(page)).frame;
  await page.waitForTimeout(180);
  expect((await diagnostics(page)).frame).toBe(frame);
});

test('search reports empty results and recovers after an index failure', async ({ page }) => {
  let failures = 1;
  await page.route('**/search-index.json.gz*', route => failures-- > 0 ? route.abort() : route.continue());
  await page.goto('/graph/viewer/index.html?home-hero=1');
  const input = page.getByRole('combobox');
  await input.fill('constituição');
  await expect(page.locator('#search-status')).toContainText('Não foi possível buscar');
  await input.fill('inexistente-xyz-123');
  await expect(page.locator('.search-empty')).toBeVisible();
  await input.fill('constituição');
  await expect(page.getByRole('option').first()).toBeVisible();
  await input.press('ArrowUp');
  await expect(input).toHaveAttribute('aria-activedescendant', /graph-option-\d+/);
  await input.press('Escape');
  await expect(input).toHaveAttribute('aria-expanded', 'false');
  await expect(input).toBeFocused();
});

test('WebGL context restoration retains the graph and returns to idle rendering', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/graph/viewer/index.html?home-hero=1');
  await page.evaluate(() => window.postMessage({ type: 'vademecum-graph-visibility', visible: true }, location.origin));
  await expect.poll(async () => (await diagnostics(page)).ready).toBe(true);
  const available = await page.evaluate(() => new Promise<boolean>(resolve => {
    const canvas = document.querySelector<HTMLCanvasElement>('#network canvas')!;
    const extension = canvas.getContext('webgl2')?.getExtension('WEBGL_lose_context');
    if (!extension) return resolve(false);
    canvas.addEventListener('webglcontextlost', () => resolve(true), { once: true });
    extension.loseContext();
    setTimeout(() => extension.restoreContext(), 700);
  }));
  expect(available).toBe(true);
  await expect(page.locator('#graph-status')).toContainText('Restaurando');
  await expect.poll(async () => (await diagnostics(page)).contextAvailable).toBe(true);
  await expect(page.locator('#graph-status')).toBeHidden();
  await expect.poll(async () => (await diagnostics(page)).rendering).toBe(false);
  expect(await diagnostics(page)).toMatchObject({ nodes: 1729, links: 1695, arrowHeads: 1695 });
  expect((await diagnostics(page)).calls).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});
