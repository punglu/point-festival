import { test, expect } from '@playwright/test';

test.describe('통합 플로우', () => {
  test('플레이어 로그인 → 대시보드 → 로그아웃 → 홈 복귀', async ({ page }) => {
    // 로그인
    await page.goto('/');
    await expect(page.locator('[class*="playerCard"], [class*="PlayerCard"]')).toBeVisible({ timeout: 10000 });
    await page.locator('[class*="playerCard"], [class*="PlayerCard"]').first().click();
    await page.locator('input[type="text"]').first().fill('1');
    await page.locator('input[type="text"]').nth(1).fill('2');
    await page.locator('input[type="text"]').nth(2).fill('3');
    await page.locator('input[type="text"]').nth(3).fill('4');
    await expect(page).toHaveURL(/dashboard/, { timeout: 5000 });

    // 로그아웃
    const logoutBtn = page.locator('button', { hasText: /로그아웃|나가기/ });
    if (await logoutBtn.isVisible()) {
      await logoutBtn.click();
      await expect(page).toHaveURL('/', { timeout: 3000 });
    }
  });

  test('관리자 로그인 → /admin 접근 성공', async ({ page }) => {
    await page.goto('/');
    await page.locator('button', { hasText: /관리자/ }).click();
    const idInput = page.locator('input[type="text"], input[placeholder*="아이디"]').first();
    await idInput.fill('dad');
    await page.locator('input[type="password"]').fill('admin1234');
    await page.locator('button[type="submit"], button', { hasText: /로그인/ }).last().click();
    await expect(page).toHaveURL(/admin/, { timeout: 5000 });

    // Admin 대시보드 요소 확인
    await expect(page.locator('[class*="adminNav"], [class*="AdminNav"]')).toBeVisible({ timeout: 5000 });
  });
});
