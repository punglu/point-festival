import { test, expect } from '@playwright/test';

test.describe('Player Login', () => {
  test('캐릭터 선택 화면이 표시된다', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('button[class*="playerCard"]').first()).toBeVisible({ timeout: 10000 });
  });

  test('PIN 입력 후 대시보드로 이동', async ({ page }) => {
    await page.goto('/');
    const playerCards = page.locator('button[class*="playerCard"]');
    await playerCards.first().click();
    for (const digit of ['1', '2', '3', '4']) {
      await page.getByRole('button', { name: digit, exact: true }).click();
    }
    await expect(page).toHaveURL(/dashboard/, { timeout: 5000 });
  });
});
