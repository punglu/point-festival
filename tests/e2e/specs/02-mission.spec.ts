import { test, expect } from '@playwright/test';

test.describe('Mission Flow', () => {
  test.beforeEach(async ({ page }) => {
    // 첫 번째 플레이어로 로그인
    await page.goto('/');
    const playerCards = page.locator('[class*="playerCard"], [class*="PlayerCard"]');
    await playerCards.first().click();
    await page.locator('input[type="text"]').first().fill('1');
    await page.locator('input[type="text"]').nth(1).fill('2');
    await page.locator('input[type="text"]').nth(2).fill('3');
    await page.locator('input[type="text"]').nth(3).fill('4');
    await expect(page).toHaveURL(/dashboard/, { timeout: 5000 });
  });

  test('대시보드에서 미션 목록이 표시된다', async ({ page }) => {
    const missionList = page.locator('[data-testid="mission-list"]');
    await expect(missionList).toBeVisible({ timeout: 10000 });

    // 샘플 미션 카드 또는 빈 상태 메시지 중 하나가 반드시 표시되어야 함
    const hasMissions = await page.locator('[data-testid="mission-list"] [class*="missionCard"]').count();
    const hasEmptyMsg = await page.locator('[data-testid="mission-list"] [class*="emptyMsg"]').count();
    expect(hasMissions + hasEmptyMsg).toBeGreaterThan(0);
  });

  test('미션 제안 버튼이 표시된다', async ({ page }) => {
    const proposalBtn = page.locator('button', { hasText: /미션|제안/ }).first();
    await expect(proposalBtn).toBeVisible({ timeout: 10000 });
  });
});
