import { expect, test } from '@playwright/test';

test.use({
  viewport: { width: 390, height: 844 },
  hasTouch: true,
  reducedMotion: 'no-preference',
});

test('touch search selects a norm and rotation starts on load', async ({ page }) => {
  await page.goto('/graph/viewer/index.html?home-hero=1');
  await page.evaluate(() => window.postMessage({
    type: 'vademecum-graph-visibility', visible: true,
  }, location.origin));
  const diagnostics = () => page.evaluate(async () => {
    const script = document.querySelector<HTMLScriptElement>('script[data-graph-app]')!;
    return (await import(script.src)).getGraphDiagnostics();
  });
  await expect.poll(async () => (await diagnostics()).ready).toBe(true);
  await expect(page.getByRole('button', { name: 'Pausar rotação' })).toHaveAttribute('aria-pressed', 'true');
  const initialCamera = (await diagnostics()).camera;
  await expect.poll(async () => {
    const camera = (await diagnostics()).camera;
    return Math.hypot(camera.x - initialCamera.x, camera.y - initialCamera.y, camera.z - initialCamera.z);
  }).toBeGreaterThan(.1);
  for (const [query, id] of [
    ['14.133', 'br-federal-lei_ordinaria-14133-2021'],
    ['constituição', 'br-federal-constituicao-1988'],
  ]) {
    await page.getByRole('combobox').tap();
    await page.getByRole('combobox').fill(query);
    await page.getByRole('option').first().tap();
    await expect.poll(async () => (await diagnostics()).selectedId).toBe(id);
    await expect(page.locator('#details')).toBeVisible();
    await page.getByRole('button', { name: 'Fechar detalhes', exact: true }).tap();
  }
});
