import { expect, test } from '@playwright/test';

test('mobile section link leaves graph controls unobstructed', async ({ page }) => {
  for (const width of [360, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto('/#inicio');
    const nextSection = page.locator('.graph-continue-link');
    const frame = page.frameLocator('.graph-hero-frame');
    await expect(frame.locator('#reset-view')).toBeVisible();
    const linkBounds = await nextSection.boundingBox();
    for (const id of ['rotation-toggle', 'reset-view']) {
      const controlBounds = await frame.locator(`#${id}`).boundingBox();
      const overlap = linkBounds!.x < controlBounds!.x + controlBounds!.width
        && linkBounds!.x + linkBounds!.width > controlBounds!.x
        && linkBounds!.y < controlBounds!.y + controlBounds!.height
        && linkBounds!.y + linkBounds!.height > controlBounds!.y;
      expect(overlap, `${width}px: ${id}`).toBe(false);
    }
    await nextSection.click();
    await expect(page).toHaveURL(/#skill$/);
  }
});
