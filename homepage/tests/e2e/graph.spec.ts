import { expect, test, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('phone requesting desktop homepage', () => {
  test.use({
    viewport: { width: 980, height: 900 },
    screen: { width: 390, height: 844 },
    hasTouch: true,
    deviceScaleFactor: 3,
    reducedMotion: 'no-preference',
  });

  test('skill deep link defers the graph and touch devices start rotating when visible', async ({ page }) => {
    test.setTimeout(90_000);
    const graphRequests: string[] = [];
    let obsoleteModuleRequested = false;
    await page.route('**/graph-core.js', route => {
      obsoleteModuleRequested = true;
      return route.fulfill({ contentType: 'text/javascript', body: 'export {}' });
    });
    page.on('request', request => {
      if (request.isNavigationRequest() && request.url().includes('/graph/viewer/')) graphRequests.push(request.url());
    });
    await page.goto('/#skill');
    await expect(page.locator('#skill')).toBeInViewport({ ratio: .5 });
    const hero = page.locator('.graph-hero-frame');
    await expect(hero).not.toHaveAttribute('src');
    await page.getByRole('button', { name: 'Ativar tema escuro', exact: true }).click();
    await expect(page.locator('html')).toHaveClass(/dark/);
    expect(graphRequests).toEqual([]);
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect(hero).toHaveAttribute('src', /graph\/viewer/);
    const frame = page.frameLocator('.graph-hero-frame');
    await expect.poll(() => frame.locator('body').evaluate(async () => {
      const app = await import(document.querySelector<HTMLScriptElement>('script[data-graph-app]')!.src);
      return app.getGraphDiagnostics().ready;
    }), { timeout: 30_000 }).toBe(true);
    expect(await frame.locator('body').evaluate(() =>
      matchMedia('(prefers-reduced-motion: reduce)').matches,
    )).toBe(false);
    const activity = () => frame.locator('body').evaluate(async () => {
      const app = await import(document.querySelector<HTMLScriptElement>('script[data-graph-app]')!.src);
      return app.getGraphDiagnostics();
    });
    // Software WebGL can occupy the CI main thread while the first frame compiles.
    await expect.poll(async () => (await activity()).rotating, { timeout: 30_000 }).toBe(true);
    expect(await activity()).toMatchObject({ nodes: 1729, links: 1695, arrowHeads: 1695 });
    await expect(hero).toHaveCSS('transform', 'none');
    await frame.getByRole('button', { name: 'Pausar rotação' }).tap();
    await expect.poll(async () => (await activity()).rendering).toBe(false);
    const before = (await activity()).frame;
    await page.waitForTimeout(200);
    expect((await activity()).frame).toBe(before);
    expect(graphRequests).toHaveLength(1);
    expect(obsoleteModuleRequested).toBe(false);
  });
});

test.describe('phone GPU budget with a desktop layout', () => {
  test.use({
    viewport: { width: 980, height: 2120 },
    screen: { width: 390, height: 844 },
    hasTouch: true,
    deviceScaleFactor: 3,
  });

  test('fits the physical screen from the first WebGL allocation', async ({ page }) => {
    test.setTimeout(90_000);
    await page.addInitScript(() => {
      const canvases = new WeakSet<HTMLCanvasElement>();
      const getContext = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, ...args: any[]) {
        if (String(args[0]).startsWith('webgl')) canvases.add(this);
        return (getContext as any).apply(this, args);
      } as typeof getContext;
      const budget = screen.width * screen.height * devicePixelRatio ** 2;
      for (const axis of ['width', 'height'] as const) {
        const descriptor = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, axis)!;
        Object.defineProperty(HTMLCanvasElement.prototype, axis, {
          ...descriptor,
          set(value: number) {
            const pixels = axis === 'width' ? value * this.height : value * this.width;
            if (canvases.has(this) && pixels > budget * 1.01) {
              throw new RangeError(`Phone GPU canvas budget exceeded: ${pixels} > ${budget}`);
            }
            descriptor.set!.call(this, value);
          },
        });
      }
    });
    await page.goto('/graph/viewer/index.html');
    await expect.poll(async () => (await diagnostics(page)).ready, { timeout: 60_000 }).toBe(true);
    const graph = await diagnostics(page);
    expect(graph.canvas![0] * graph.canvas![1]).toBeLessThanOrEqual(390 * 844 * 9 * 1.01);
    expect(graph).toMatchObject({ nodes: 1729, links: 1695, arrowHeads: 1695 });
    await page.getByRole('combobox').click();
    await page.getByRole('combobox').fill('14.133');
    await page.getByRole('option').first().tap();
    await expect(page.locator('#details')).toBeVisible();
    await expect(page.locator('#graph-status')).toBeHidden();
  });
});

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
