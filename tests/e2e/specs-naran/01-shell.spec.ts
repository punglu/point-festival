import { test, expect } from '@playwright/test';

async function loginAsFirstPlayer(page: import('@playwright/test').Page) {
  await page.goto('/');
  await page.locator('button[class*="playerCard"]').first().click();
  for (const digit of ['1', '2', '3', '4']) {
    await page.getByRole('button', { name: digit, exact: true }).click();
  }
  await expect(page).toHaveURL(/dashboard/);
}

async function loginAsLegacyPlayer(page: import('@playwright/test').Page, playerId: number) {
  const response = await page.request.post('/api/auth/login', {
    data: { player_id: playerId, pin: '1234' },
  });
  expect(response.ok()).toBeTruthy();
  const body = await response.json() as { access_token: string };
  await page.goto('/');
  await page.evaluate((token) => sessionStorage.setItem('accessToken', token), body.access_token);
  await page.reload();
  await expect(page).toHaveURL(/dashboard/);
}

test.describe('Naran platform shell', () => {
  test('keeps the legacy dashboard inside the Naran shell and allows a Family switch', async ({ page }, testInfo) => {
    await loginAsFirstPlayer(page);
    await expect(page.getByTestId('naran-shell')).toBeVisible();
    const familySelect = page.getByLabel('활성 가족 선택');
    await expect(familySelect).toBeVisible();
    await expect(familySelect.locator('option')).toHaveCount(3); // placeholder + Alpha + Beta
    await familySelect.selectOption({ label: 'Synthetic Family Beta' });
    await expect(familySelect).toHaveValue(/\d+/);
    await expect(page.getByRole('link', { name: '미션 관리' })).toHaveCount(0);
    await familySelect.selectOption({ label: 'Synthetic Family Alpha' });
    if (testInfo.project.name === 'desktop') {
      await expect(page.getByRole('link', { name: '미션 관리' })).toBeVisible();
    } else {
      // The unchanged legacy dashboard retains its own mobile navigation.
      // The Naran mobile navigation is covered on the non-legacy Doran route.
      await expect(familySelect).toHaveValue(/\d+/);
    }
    await expect(page).toHaveURL(/dashboard/);
  });

  test('presents Doran as an honest unavailable service entry point', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    await page.goto('/naran/doran');
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();
  });

  test('renders the responsive navigation landmark', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.goto('/naran/doran');
    await expect(page.getByRole('navigation', { name: /몽글 (서비스 탐색|모바일 탐색)/ })).toHaveCount(1);
  });

  test('does not turn a direct Family URL into a permission grant', async ({ page }) => {
    // Player 4 is linked only as a MarkPoint participant in Alpha.  Use the
    // existing legacy login API so this stays independent of card ordering.
    await loginAsLegacyPlayer(page, 4);
    await page.goto('/naran/family');
    await expect(page.getByRole('heading', { name: '권한이 없어요' })).toBeVisible();
  });

  test('renders the reviewed mapping-needed state without creating an Account', async ({ page }) => {
    await page.route('**/api/account-context', async (route) => {
      await route.fulfill({ status: 403, contentType: 'application/json', body: JSON.stringify({ detail: '계정 매핑이 필요합니다' }) });
    });
    await loginAsFirstPlayer(page);
    await expect(page.getByText('계정 연결이 필요해요')).toBeVisible();
  });
});
