import { test, expect } from '@playwright/test';

test.describe('Mission Flow', () => {
  test.beforeEach(async ({ page }) => {
    // 첫 번째 플레이어로 로그인
    await page.goto('/');
    const playerCards = page.locator('button[class*="playerCard"]');
    await playerCards.first().click();
    for (const digit of ['1', '2', '3', '4']) {
      await page.getByRole('button', { name: digit, exact: true }).click();
    }
    await expect(page).toHaveURL(/dashboard/, { timeout: 5000 });
  });

  test('대시보드에서 미션 목록이 표시된다', async ({ page }) => {
    const missionList = page.locator('[class*="missionList"]');
    await expect(missionList).toBeVisible({ timeout: 10000 });

    // 샘플 미션 카드 또는 빈 상태 메시지 중 하나가 반드시 표시되어야 함
    const hasMissions = await missionList.locator('[class*="card"]').count();
    const hasEmptyMsg = await missionList.locator('[class*="emptyMsg"]').count();
    expect(hasMissions + hasEmptyMsg).toBeGreaterThan(0);
  });

  test('미션 제안 버튼이 표시된다', async ({ page }) => {
    const proposalBtn = page.locator('button', { hasText: /미션|제안/ }).first();
    await expect(proposalBtn).toBeVisible({ timeout: 10000 });
  });
});
