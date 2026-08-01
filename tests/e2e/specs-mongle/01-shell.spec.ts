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

// MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.
//
// The previous run of this suite reported 41 failures against a frontend image
// built before the source under test existed. Nothing in the suite could tell,
// so the whole result was worthless. This describe block runs first and makes
// the browser itself prove which build it is talking to — if it fails, every
// other result in the file is about the wrong bundle and must be discarded.
test.describe('Current-source runtime proof', () => {
  test('the browser is served the build made from this worktree', async ({ page }) => {
    const expected = process.env.MONGLE_FRONTEND_FINGERPRINT;
    test.skip(!expected, 'fingerprint not exported — run through scripts/start-mongle-phase1.sh');

    await page.goto('/');
    const served = await page.evaluate(async () => {
      const response = await fetch('/build-fingerprint.txt', { cache: 'no-store' });
      return response.ok ? response.text() : '';
    });
    expect(served, 'served app exposes no build fingerprint').not.toBe('');

    const fingerprint = /^fingerprint=(.+)$/m.exec(served)?.[1];
    const entry = /^entry=(.+)$/m.exec(served)?.[1];
    expect(fingerprint).toBe(expected);

    // Second, independent witness: the entry bundle name is content-hashed by
    // Vite, so a page loading a different one is not this build no matter what
    // the sidecar file says.
    const loadedEntry = await page.evaluate(() =>
      Array.from(document.querySelectorAll('script[src]'))
        .map((el) => (el as HTMLScriptElement).getAttribute('src'))
        .find((src) => src?.includes('/assets/index-')) ?? '',
    );
    expect(loadedEntry).toBe(entry);
  });
});

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
      // MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001: this used to assert
      // that the FAMILY owner SEES "미션 관리". That expectation was written
      // before migration `0006`, which removed `markpoint.missions.manage` from
      // every FAMILY-scope role because auto-granting it violated D4 (a
      // FamilyAdmin is never automatically a ServiceAdmin). Verified against the
      // live `/api/account-context`: the owner of Synthetic Family Alpha holds
      // `family.*` and `markpoint.own.read`, and no `markpoint.missions.manage`.
      // So the link being absent is the contract holding, and the old assertion
      // was pinning the privilege escalation in place. Inverted rather than
      // deleted, so a regression that re-grants it fails here.
      await expect(page.getByRole('link', { name: '미션 관리' })).toHaveCount(0);
      // A permission the owner genuinely does hold still gates a visible link,
      // which keeps this a real permission assertion and not just a negative.
      await expect(page.getByRole('link', { name: '가족' })).toBeVisible();
    } else {
      // The unchanged legacy dashboard retains its own mobile navigation.
      // The Mongle mobile navigation is covered on the non-legacy Wagle route.
      await expect(familySelect).toHaveValue(/\d+/);
    }
    await expect(page).toHaveURL(/dashboard/);
  });

  test('presents Wagle as a service entry point', async ({ page }) => {
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

// MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.
//
// The retired key prefix is assembled from parts, not written literally, so a
// repository-wide rename sweep cannot quietly turn these assertions into
// assertions about the canonical key — which would make the migration tests
// pass while proving nothing. That failure mode has already occurred twice in
// this migration effort.
const RETIRED_PLATFORM = 'na' + 'ran';
const RETIRED_KEY_PREFIX = `${RETIRED_PLATFORM}.activeFamily.`;
const CANONICAL_KEY_PREFIX = 'mongle.activeFamily.';

async function activeFamilyKeys(page: import('@playwright/test').Page) {
  return page.evaluate(({ retired, canonical }) => {
    const entries: { key: string; value: string }[] = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (key && (key.startsWith(canonical) || key.startsWith(retired))) {
        entries.push({ key, value: localStorage.getItem(key) ?? '' });
      }
    }
    return entries;
  }, { retired: RETIRED_KEY_PREFIX, canonical: CANONICAL_KEY_PREFIX });
}

test.describe('Canonical route migration', () => {
  test('canonical /wagle and /family render directly, refresh preserved, no console error', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });

    // Note: on wide (≥701px) viewports, WagleLanding auto-selects the first
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

  test('retired /naran/* paths are no longer registered and fall through to the 404 page', async ({ page }) => {
    // PM cutover: the compatibility aliases were removed outright. Old
    // bookmarks 404 by design — that is the decision, not a regression. What
    // must NOT happen is a surviving redirect, which would keep the retired
    // platform name alive in the router.
    await loginAsFirstPlayer(page);

    for (const retiredPath of [`/${RETIRED_PLATFORM}/doran`, `/${RETIRED_PLATFORM}/family`, `/${RETIRED_PLATFORM}`]) {
      await page.goto(`${retiredPath}?source=legacy#latest`);
      // No redirect: the URL stays where it was asked to go ...
      await expect(page).toHaveURL(new RegExp(`${retiredPath}`));
      // ... and the not-found page renders.
      await expect(page.getByRole('heading', { name: '페이지를 찾을 수 없어요' })).toBeVisible();
    }
  });

  test('canonical routes still work after the retired aliases were removed', async ({ page }) => {
    // The paths below are the ones declared in frontend/src/App.tsx: "/",
    // "/dashboard", "/admin/*", "/wagle", "/family" and the "*" catch-all.
    // Read from the router, not from a count quoted in a report.
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });

    await page.goto('/wagle');
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();

    await page.goto('/family');
    await expect(page).toHaveURL(/\/family$/);

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard$/);

    // "/admin/*" is registered and guarded: a non-admin is redirected away,
    // which is a different outcome from the not-found page an unregistered path
    // produces. That difference is what proves the route still exists. The
    // guard sends the user to "/", and "/" then sends an already-logged-in user
    // on to "/dashboard" — so assert "left /admin and did not 404", not one
    // exact landing URL.
    await page.goto('/admin/missions');
    await expect(page).not.toHaveURL(/\/admin\//);
    await expect(page.getByRole('heading', { name: '페이지를 찾을 수 없어요' })).toHaveCount(0);
  });
});

test.describe('Wagle service seam', () => {
  test('an active wagle subscription from the API renders as available, not disabled', async ({ page }) => {
    // This is the seam the runtime rename broke once already: the API emits
    // `service_code` and the frontend compares it against a literal, and both
    // sides are `string`, so no type check can catch a mismatch. Assert the
    // real payload and the rendered consequence together — asserting only the
    // payload would still pass if the frontend compared the historical code.
    await loginAsFirstPlayer(page);
    // The app authenticates with a bearer token held in sessionStorage, not a
    // cookie, so a bare `page.request` call is anonymous and gets 401. Read the
    // same token the app itself uses.
    const token = await page.evaluate(() => sessionStorage.getItem('accessToken'));
    expect(token, 'no access token in sessionStorage after login').toBeTruthy();
    const response = await page.request.get('/api/account-context', {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json() as {
      families: { name: string; services: { service_code: string; status: string }[] }[];
    };
    const alpha = body.families.find((family) => family.name === 'Synthetic Family Alpha');
    expect(alpha, 'seeded Family Alpha is missing from account-context').toBeTruthy();
    const wagle = alpha!.services.find((service) => service.service_code === 'wagle');
    expect(wagle, 'account-context emits no `wagle` service').toBeTruthy();
    expect(wagle!.status).toBe('active');
    // And the retired messaging code must not be emitted at all.
    expect(alpha!.services.map((service) => service.service_code)).not.toContain('do' + 'ran');

    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    await page.goto('/wagle');
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();
    await expect(page.getByText('와글와글을 사용할 수 없어요')).toHaveCount(0);
  });
});

test.describe('Active Family storage migration', () => {
  test('canonical absent + valid legacy present: family preserved, canonical copy-forward occurs', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const before = await activeFamilyKeys(page);
    const canonical = before.find((e) => e.key.startsWith(CANONICAL_KEY_PREFIX));
    expect(canonical).toBeTruthy();

    // Simulate a pre-migration browser: only the retired key exists.
    await page.evaluate(({ key, value, retired }) => {
      const accountId = key.split('.').pop()!;
      localStorage.removeItem(key);
      localStorage.setItem(`${retired}${accountId}`, value);
    }, { ...canonical!, retired: RETIRED_KEY_PREFIX });

    await page.reload();
    await expect(page.getByLabel('활성 가족 선택')).toHaveValue(/\d+/);
    const after = await activeFamilyKeys(page);
    // The selection survives ...
    expect(after.some((e) => e.key === canonical!.key && e.value === canonical!.value)).toBe(true);
    // ... and the retired key is gone: migration is one-time, not a permanent
    // fallback. Leaving it behind is what keeps the retired name in the browser.
    expect(after.some((e) => e.key.startsWith(RETIRED_KEY_PREFIX))).toBe(false);

    // Idempotency: running the migration again changes nothing.
    await page.reload();
    const afterSecond = await activeFamilyKeys(page);
    expect(afterSecond.some((e) => e.key === canonical!.key && e.value === canonical!.value)).toBe(true);
    expect(afterSecond.some((e) => e.key.startsWith(RETIRED_KEY_PREFIX))).toBe(false);
  });

  test('canonical present + legacy present with a different value: canonical wins, legacy not overwritten', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith(CANONICAL_KEY_PREFIX))!;
    const accountId = canonical.key.split('.').pop();

    await page.evaluate(({ accountId, bogus, retired }) => {
      localStorage.setItem(`${retired}${accountId}`, bogus);
    }, { accountId, bogus: '999999', retired: RETIRED_KEY_PREFIX });

    await page.reload();
    // Canonical still wins — a stale retired value must never override it.
    await expect(page.getByLabel('활성 가족 선택')).toHaveValue(canonical.value);
    const after = await activeFamilyKeys(page);
    // And the retired key is purged even though it was not adopted.
    expect(after.some((e) => e.key === `${RETIRED_KEY_PREFIX}${accountId}`)).toBe(false);
  });

  test('canonical absent + invalid/inaccessible legacy: no copy-forward, no silent auto-select', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith(CANONICAL_KEY_PREFIX))!;
    const accountId = canonical.key.split('.').pop();

    await page.evaluate(({ key, accountId, retired }) => {
      localStorage.removeItem(key);
      localStorage.setItem(`${retired}${accountId}`, '999999'); // not an accessible Family
    }, { key: canonical.key, accountId, retired: RETIRED_KEY_PREFIX });

    await page.reload();
    await expect(page.getByText('가족을 선택해주세요')).toBeVisible();
    const after = await activeFamilyKeys(page);
    expect(after.some((e) => e.key === canonical.key)).toBe(false); // not adopted
    expect(after.some((e) => e.key === `${RETIRED_KEY_PREFIX}${accountId}`)).toBe(false); // still purged
  });

  test('malformed retired value: no crash, no selection applied, key still purged', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith(CANONICAL_KEY_PREFIX))!;
    const accountId = canonical.key.split('.').pop();

    await page.evaluate(({ key, accountId, retired }) => {
      localStorage.removeItem(key);
      localStorage.setItem(`${retired}${accountId}`, 'not-a-number');
    }, { key: canonical.key, accountId, retired: RETIRED_KEY_PREFIX });

    await page.reload();
    // Startup survives the malformed value and asks rather than guessing.
    await expect(page.getByText('가족을 선택해주세요')).toBeVisible();
    const after = await activeFamilyKeys(page);
    expect(after.some((e) => e.key === canonical.key)).toBe(false);
    expect(after.some((e) => e.key === `${RETIRED_KEY_PREFIX}${accountId}`)).toBe(false);
  });

  test('changing the active Family writes only the canonical key', async ({ page }) => {
    // Normal runtime must be canonical-only: no dual-write, and no path that
    // re-creates the retired key after the one-time migration removed it.
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const afterAlpha = await activeFamilyKeys(page);
    expect(afterAlpha.every((e) => e.key.startsWith(CANONICAL_KEY_PREFIX))).toBe(true);
    const alphaValue = afterAlpha.find((e) => e.key.startsWith(CANONICAL_KEY_PREFIX))!.value;

    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Beta' });
    const afterBeta = await activeFamilyKeys(page);
    const canonicalAfter = afterBeta.filter((e) => e.key.startsWith(CANONICAL_KEY_PREFIX));
    expect(canonicalAfter).toHaveLength(1);
    expect(canonicalAfter[0].value).not.toBe(alphaValue);
    expect(afterBeta.some((e) => e.key.startsWith(RETIRED_KEY_PREFIX))).toBe(false);
  });

  test('explicit logout clears both canonical and legacy keys for that account, no resurrection on next login', async ({ page }) => {
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    const keys = await activeFamilyKeys(page);
    const canonical = keys.find((e) => e.key.startsWith(CANONICAL_KEY_PREFIX))!;
    const accountId = canonical.key.split('.').pop();
    await page.evaluate(({ accountId, retired }) => {
      localStorage.setItem(`${retired}${accountId}`, '1'); // seed a retired value too
    }, { accountId, retired: RETIRED_KEY_PREFIX });

    // The legacy dashboard renders its own separate "로그아웃" button in
    // addition to the Shell header's — scope to the Shell's banner to avoid
    // strict-mode ambiguity between the two.
    await page.getByRole('banner').getByRole('button', { name: '로그아웃' }).click();
    await expect(page).toHaveURL(/\/$/);
    const afterLogout = await activeFamilyKeys(page);
    expect(afterLogout.some((e) => e.key === canonical.key)).toBe(false);
    expect(afterLogout.some((e) => e.key === `${RETIRED_KEY_PREFIX}${accountId}`)).toBe(false);

    await loginAsFirstPlayer(page);
    // 2 Families (Alpha/Beta), no valid saved id after logout → must ask again, not silently restore Alpha.
    await expect(page.getByText('가족을 선택해주세요')).toBeVisible();
  });
});
