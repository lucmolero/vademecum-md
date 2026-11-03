import { expect, test } from '@playwright/test';

for (const viewport of [{ width: 360, height: 780 }, { width: 844, height: 390 }, { width: 1440, height: 900 }]) {
  test(`reader overlays fit and close correctly at ${viewport.width}×${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('/biblioteca/#documento=br-federal-constituicao-1988&artigo=art-1o');
    await expect(page.locator('.document-content #art-1o')).toBeVisible();
    await page.locator('#appearance-toggle').click();
    const appearance = page.locator('#appearance');
    await expect(appearance).toBeVisible();
    const bounds = await appearance.boundingBox();
    expect(bounds!.y).toBeGreaterThanOrEqual(0);
    expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport.height);
    await page.locator('#motion').scrollIntoViewIfNeeded();
    await expect(page.locator('#motion')).toBeInViewport();
    await page.keyboard.press('Escape');
    await expect(appearance).toBeHidden();
    await expect(page.locator('#appearance-toggle')).toBeFocused();

    await page.locator('#show-source').click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.locator('#source-details')).toContainText('Consolidada na fonte oficial');
    await expect(page.locator('#source-details')).toContainText('Verificação aprovada');
    const links = page.locator('#source-details a');
    expect(await links.count()).toBeGreaterThan(1);
    const first = await links.nth(0).boundingBox();
    const second = await links.nth(1).boundingBox();
    expect(second!.y > first!.y || second!.x >= first!.x + first!.width + 8).toBe(true);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).toBeHidden();

    await page.locator('#reader-back-library:visible, #back-library:visible').first().click();
    await page.locator('[data-action="sort"]').click();
    await page.getByRole('menuitem', { name: 'Nova pasta', exact: true }).scrollIntoViewIfNeeded();
    await expect(page.getByRole('menuitem', { name: 'Nova pasta', exact: true })).toBeInViewport();
    await page.keyboard.press('Escape');
    await expect(page.locator('.shelf-sort-menu')).toBeHidden();
  });
}

test('copied citation distinguishes the source date from the collection cutoff', async ({ page }) => {
  await page.goto('/biblioteca/#documento=br-federal-constituicao-1988&artigo=art-1o');
  await expect(page.locator('.document-content #art-1o')).toBeVisible();
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', { value: {
      writeText: async (text: string) => { document.body.dataset.copiedCitation = text; },
    } });
  });
  await page.locator('#copy-citation').click();
  await expect(page.locator('body')).toHaveAttribute('data-copied-citation', /Data da fonte: 2026-10-21\. Corte do acervo: 2026-10-21\./);
  await expect(page.locator('body')).not.toHaveAttribute('data-copied-citation', /Consulta em/);
});

test('mobile navigation closes after choosing a section and Escape restores focus', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  await page.goto('/#skill');
  const trigger = page.getByRole('button', { name: 'Abrir navegação' });
  await trigger.click();
  await expect(page.getByRole('menu')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(trigger).toBeFocused();
  await trigger.click();
  const menuBox = await page.getByRole('menu').boundingBox();
  expect(menuBox).not.toBeNull();
  expect(menuBox!.x).toBeGreaterThanOrEqual(0);
  expect(menuBox!.x + menuBox!.width).toBeLessThanOrEqual(360);
  await page.getByRole('menuitem', { name: 'Recursos', exact: true }).click();
  await expect(page).toHaveURL(/#recursos$/);
  await expect(page.getByRole('menu')).toBeHidden();
});
