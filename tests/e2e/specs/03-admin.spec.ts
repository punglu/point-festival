import { test, expect } from '@playwright/test';

test.describe('Admin Login', () => {
  test('관리자 로그인 버튼이 표시된다', async ({ page }) => {
    await page.goto('/');
    const adminBtn = page.locator('button', { hasText: /관리자/ });
    await expect(adminBtn).toBeVisible({ timeout: 10000 });
  });

  test('관리자 ID/PW 폼이 표시된다', async ({ page }) => {
    await page.goto('/');
    await page.locator('button', { hasText: /관리자/ }).click();
    await expect(page.locator('input[type="text"], input[placeholder*="아이디"]').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('관리자 로그인 후 /admin으로 이동', async ({ page }) => {
    await page.goto('/');
    await page.locator('button', { hasText: /관리자/ }).click();
    const idInput = page.locator('input[type="text"], input[placeholder*="아이디"]').first();
    await idInput.fill('dad');
    await page.locator('input[type="password"]').fill('admin1234');
    await page.locator('button[type="submit"], button', { hasText: /로그인/ }).last().click();
    await expect(page).toHaveURL(/admin/, { timeout: 5000 });
  });
});
