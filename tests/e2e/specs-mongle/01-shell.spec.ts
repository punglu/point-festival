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

test.describe('Mongle platform shell', () => {
  test('keeps the legacy dashboard inside the Mongle shell and allows a Family switch', async ({ page }, testInfo) => {
    await loginAsFirstPlayer(page);
    await expect(page.getByTestId('mongle-shell')).toBeVisible();
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
      // The Mongle mobile navigation is covered on the non-legacy Doran route.
      await expect(familySelect).toHaveValue(/\d+/);
    }
    await expect(page).toHaveURL(/dashboard/);
  });

  test('presents Doran as an honest unavailable service entry point', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    await page.goto('/wagle');
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();
  });

  test('renders the responsive navigation landmark', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.goto('/wagle');
    await expect(page.getByRole('navigation', { name: /몽글 (서비스 탐색|모바일 탐색)/ })).toHaveCount(1);
  });

  test('does not turn a direct Family URL into a permission grant', async ({ page }) => {
    // Player 4 is linked only as a MarkPoint participant in Alpha.  Use the
    // existing legacy login API so this stays independent of card ordering.
    await loginAsLegacyPlayer(page, 4);
    await page.goto('/family');
    await expect(page.getByRole('heading', { name: '권한이 없어요' })).toBeVisible();
  });

  test('renders the reviewed mapping-needed state without creating an Account', async ({ page }) => {
    await page.route('**/api/account-context', async (route) => {
      await route.fulfill({ status: 403, contentType: 'application/json', body: JSON.stringify({ detail: '계정 매핑이 필요합니다' }) });
    });
    await loginAsFirstPlayer(page);
    await expect(page.getByText('계정 연결이 필요해요')).toBeVisible();
  });

  test('shows a safe not-found page instead of a blank screen for an unregistered path', async ({ page }) => {
    await page.goto('/this-path-does-not-exist');
    await expect(page.getByRole('heading', { name: '페이지를 찾을 수 없어요' })).toBeVisible();
    await expect(page.getByRole('link', { name: '몽글로 돌아가기' })).toBeVisible();
  });
});

// MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001

async function activeFamilyKeys(page: import('@playwright/test').Page) {
  return page.evaluate(() => {
    const entries: { key: string; value: string }[] = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (key && (key.startsWith('mongle.activeFamily.') || key.startsWith('naran.activeFamily.'))) {
        entries.push({ key, value: localStorage.getItem(key) ?? '' });
      }
    }
    return entries;
  });
}

test.describe('Canonical route migration', () => {
  test('canonical /wagle and /family render directly, refresh preserved, no console error', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });

    // Note: on wide (≥701px) viewports, DoranLanding auto-selects the first
    // room and appends `?room=...` — pre-existing behavior, unrelated to this
    // migration. Assert on pathname only, not the full URL, for this reason.
    await page.goto('/wagle');
    await page.waitForURL((url) => url.pathname === '/wagle');
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();
    await page.reload();
    await page.waitForURL((url) => url.pathname === '/wagle');
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();

    await page.goto('/family');
    await expect(page).toHaveURL(/\/family$/);
    await page.reload();
    await expect(page).toHaveURL(/\/family$/);

    expect(errors).toEqual([]);
  });

  test('internal Dock/nav clicks produce canonical URLs, never /naran/*', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop', 'desktop nav landmark carries the same links as mobile Dock');
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    await page.getByRole('link', { name: '와글와글' }).click();
    await page.waitForURL((url) => url.pathname === '/wagle');
    await page.getByRole('link', { name: '가족' }).click();
    await expect(page).toHaveURL(/\/family$/);
  });

  test('legacy /naran/doran and /naran/family redirect once, preserving query and hash, no Back-loop', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });

    // DoranLanding has its own PRE-EXISTING desktop-only (>=701px) behavior:
    // it auto-selects the first room and rewrites the query string to
    // `?room=...` on first normal-state load, replacing whatever query string
    // it received (this is unrelated to and unaffected by this migration —
    // verified to reproduce identically whether /wagle is reached directly or
    // via the legacy redirect). On narrow (<701px) viewports this auto-select
    // never fires, so query/hash preservation is asserted exactly there.
    const isNarrowViewport = (page.viewportSize()?.width ?? 0) < 701;

    await page.goto('/naran/doran?source=legacy#latest');
    if (isNarrowViewport) {
      await expect(page).toHaveURL(/\/wagle\?source=legacy#latest$/);
    } else {
      await page.waitForURL((url) => url.pathname === '/wagle');
    }
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();

    // /family has no equivalent auto-effect, so query/hash preservation holds
    // on every viewport.
    await page.goto('/naran/family?tab=members#top');
    await expect(page).toHaveURL(/\/family\?tab=members#top$/);

    // Back-loop check: land on dashboard, go to a legacy URL (replace-redirected),
    // then Back must return to dashboard, not bounce between the legacy/canonical pair.
    await page.goto('/dashboard');
    await page.goto('/naran/doran');
    await page.waitForURL((url) => url.pathname === '/wagle');
    await page.goBack();
    await expect(page).toHaveURL(/\/dashboard$/);
  });

  test('legacy routes do not fall through to the 404 catch-all', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.goto('/naran/doran');
    await expect(page.getByRole('heading', { name: '페이지를 찾을 수 없어요' })).toHaveCount(0);
    await page.goto('/naran/family');
    await expect(page.getByRole('heading', { name: '페이지를 찾을 수 없어요' })).toHaveCount(0);
  });
});

test.describe('Active Family storage migration', () => {
  test('canonical absent + valid legacy present: family preserved, canonical copy-forward occurs', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const before = await activeFamilyKeys(page);
    const canonical = before.find((e) => e.key.startsWith('mongle.activeFamily.'));
    expect(canonical).toBeTruthy();

    // Simulate a pre-migration browser: only the legacy key exists.
    await page.evaluate(({ key, value }) => {
      const accountId = key.split('.').pop()!;
      localStorage.removeItem(key);
      localStorage.setItem(`naran.activeFamily.${accountId}`, value);
    }, canonical!);

    await page.reload();
    await expect(page.getByLabel('활성 가족 선택')).toHaveValue(/\d+/);
    const after = await activeFamilyKeys(page);
    expect(after.some((e) => e.key === canonical!.key && e.value === canonical!.value)).toBe(true);
    expect(after.some((e) => e.key.startsWith('naran.activeFamily.'))).toBe(true); // legacy retained, not deleted
  });

  test('canonical present + legacy present with a different value: canonical wins, legacy not overwritten', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith('mongle.activeFamily.'))!;
    const accountId = canonical.key.split('.').pop();

    await page.evaluate(({ accountId, bogus }) => {
      localStorage.setItem(`naran.activeFamily.${accountId}`, bogus);
    }, { accountId, bogus: '999999' });

    await page.reload();
    // Still resolves to the canonical (Alpha) selection, not the bogus legacy value.
    await expect(page.getByLabel('활성 가족 선택')).toHaveValue(canonical.value);
    const after = await activeFamilyKeys(page);
    const legacyAfter = after.find((e) => e.key === `naran.activeFamily.${accountId}`);
    expect(legacyAfter?.value).toBe('999999'); // untouched by canonical read path
  });

  test('canonical absent + invalid/inaccessible legacy: no copy-forward, no silent auto-select', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith('mongle.activeFamily.'))!;
    const accountId = canonical.key.split('.').pop();

    await page.evaluate(({ key, accountId }) => {
      localStorage.removeItem(key);
      localStorage.setItem(`naran.activeFamily.${accountId}`, '999999'); // not an accessible Family
    }, { key: canonical.key, accountId });

    await page.reload();
    await expect(page.getByText('가족을 선택해주세요')).toBeVisible();
    const after = await activeFamilyKeys(page);
    expect(after.some((e) => e.key === canonical.key)).toBe(false); // no canonical key created from invalid legacy
  });

  test('explicit logout clears both canonical and legacy keys for that account, no resurrection on next login', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith('mongle.activeFamily.'))!;
    const accountId = canonical.key.split('.').pop();
    await page.evaluate(({ accountId }) => {
      localStorage.setItem(`naran.activeFamily.${accountId}`, '1'); // seed a legacy value too
    }, { accountId });

    // The legacy dashboard renders its own separate "로그아웃" button in
    // addition to the Shell header's — scope to the Shell's banner to avoid
    // strict-mode ambiguity between the two.
    await page.getByRole('banner').getByRole('button', { name: '로그아웃' }).click();
    await expect(page).toHaveURL(/\/$/);
    const afterLogout = await activeFamilyKeys(page);
    expect(afterLogout.some((e) => e.key === canonical.key)).toBe(false);
    expect(afterLogout.some((e) => e.key === `naran.activeFamily.${accountId}`)).toBe(false);

    await loginAsFirstPlayer(page);
    // 2 Families (Alpha/Beta), no valid saved id after logout → must ask again, not silently restore Alpha.
    await expect(page.getByText('가족을 선택해주세요')).toBeVisible();
  });
});
