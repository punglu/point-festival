import { test, expect } from '@playwright/test';

test.describe('Player Login', () => {
  test('캐릭터 선택 화면이 표시된다', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[class*="playerCard"], [class*="PlayerCard"]')).toBeVisible({ timeout: 10000 });
  });

  test('PIN 입력 후 대시보드로 이동', async ({ page }) => {
    await page.goto('/');
    const playerCards = page.locator('[class*="playerCard"], [class*="PlayerCard"]');
    await playerCards.first().click();
    await page.locator('input[type="text"]').first().fill('1');
    await page.locator('input[type="text"]').nth(1).fill('2');
    await page.locator('input[type="text"]').nth(2).fill('3');
    await page.locator('input[type="text"]').nth(3).fill('4');
    await expect(page).toHaveURL(/dashboard/, { timeout: 5000 });
  });
});
