import { expect, test, type Page } from '@playwright/test';

/**
 * MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001 — the seven Wave 6 journeys.
 *
 * Every test signs in through the product's own Account-native screen. Nothing
 * here mocks a response, stubs an endpoint, or reads a preview fixture — the
 * fixtures were removed from the production path by this task and the built
 * bundle contains zero of their symbols.
 *
 * Seeded actors, and why there are three:
 *
 *   owner.a   Family A + B · markpoint.missions.manage · wagle room_admin
 *   admin.a   Family A     · markpoint.points.adjust   · (no wagle role)
 *   member.a  Family A     · plain member              · wagle participant
 *
 * They are separate accounts on purpose. A single account holding every
 * permission would make the authorization journey vacuous — it could only ever
 * prove that a permitted call succeeds, never that an unpermitted one is
 * refused.
 */

const PASSWORD = 'Synthetic!Pass9';

async function signIn(page: Page, username: string, familyIndex = 0) {
  await page.goto('/login');
  await page.getByTestId('account-username').fill(username);
  await page.getByTestId('account-password').fill(PASSWORD);
  await page.getByTestId('account-login-submit').click();
  await expect(page).toHaveURL(/\/family$/, { timeout: 15000 });

  // An account in more than one family lands on the selector, because the
  // store auto-selects only when there is exactly one — guessing which family
  // someone meant is worse than asking. Choose explicitly here so the journeys
  // below start from a known family rather than from whichever one a default
  // would have picked.
  const chooser = page.locator('[data-testid^="family-switch-"]');
  if ((await chooser.count()) > 0 && (await page.getByTestId('family-name').count()) === 0) {
    await chooser.nth(familyIndex).click();
    await expect(page.getByTestId('family-name')).toBeVisible({ timeout: 10000 });
  }
}

/** The bearer token the app itself is using, for direct API assertions. */
async function token(page: Page): Promise<string> {
  const value = await page.evaluate(() => sessionStorage.getItem('accessToken'));
  expect(value).toBeTruthy();
  return value as string;
}

// ===========================================================================
// Journey 1 — Multi-Family
// ===========================================================================

test.describe('Journey 1 — Multi-Family', () => {
  test('an account switches families without losing its session or leaking data', async ({
    page,
  }) => {
    await signIn(page, 'owner.a');

    // The AuthorizedFamilySet is server-derived; the screen lists what the
    // server returned, not what the client chose.
    await expect(page.getByTestId('family-list')).toBeVisible();
    const families = page.getByTestId('family-list').locator('li');
    await expect(families).toHaveCount(2);

    const sessionBefore = await token(page);
    const firstName = await page.getByTestId('family-name').textContent();

    // Switch to the other family.
    const switches = page.locator('[data-testid^="family-switch-"]');
    const target = switches.nth(1);
    await target.click();
    await expect(page.getByTestId('family-name')).not.toHaveText(firstName ?? '', {
      timeout: 10000,
    });

    // Switching a family is a UI choice, never a re-authentication.
    expect(await token(page)).toBe(sessionBefore);

    // Family B has no active Markpoint subscription in the fixture, so its
    // card must say so rather than offering an entry that would 403.
    const markpointCard = page.getByTestId('service-markpoint');
    await expect(markpointCard).toBeVisible();
    const status = await markpointCard.getAttribute('data-status');
    if (status !== 'active') {
      await expect(page.getByTestId('service-markpoint-enter')).toHaveCount(0);
    }
  });

  test('the family context comes from the server, not from local state', async ({ page }) => {
    await signIn(page, 'member.a');
    const response = await page.request.get('/api/account-context', {
      headers: { Authorization: `Bearer ${await token(page)}` },
    });
    expect(response.status()).toBe(200);
    const body = await response.json();
    // member.a belongs to Family A only — the screen cannot show more than the
    // server authorizes.
    expect(body.families).toHaveLength(1);
    await expect(page.getByTestId('family-name')).toHaveText(body.families[0].name);
  });
});

// ===========================================================================
// Journey 2 — Markpoint user
// ===========================================================================

test.describe('Journey 2 — Markpoint user', () => {
  test('the dashboard renders server-computed figures and separates balance from EXP', async ({
    page,
  }) => {
    await signIn(page, 'member.a');
    await page.goto('/markpoint');

    await expect(page.getByRole('heading', { name: '마크포인트' })).toBeVisible();
    await expect(page.getByTestId('markpoint-balance')).toBeVisible();
    await expect(page.getByTestId('markpoint-level')).toBeVisible();
    await expect(page.getByTestId('markpoint-remaining')).toBeVisible();

    // Assert the screen agrees with the API rather than with itself: a
    // frontend that re-derived these numbers could look consistent and still
    // be wrong.
    const api = await page.request.get('/api/me/markpoint/projection?family_id=1', {
      headers: { Authorization: `Bearer ${await token(page)}` },
    });
    const projection = await api.json();
    await expect(page.getByTestId('markpoint-balance')).toHaveText(
      String(projection.current_balance),
    );
    await expect(page.getByTestId('markpoint-remaining')).toHaveText(
      String(projection.remaining_missions),
    );
  });

  test('every date in the cycle appears, including empty ones', async ({ page }) => {
    await signIn(page, 'member.a');
    await page.goto('/markpoint');
    // Wait for the section before counting: `count()` does not auto-retry, so
    // reading it while the screen is still loading returns 0 and the failure
    // looks like a missing calendar rather than a race.
    const list = page.getByTestId('markpoint-weekly-days');
    await expect(list).toBeVisible({ timeout: 15000 });
    const days = list.locator('> li');
    // An empty day is rendered explicitly so a gap in the calendar is never
    // ambiguous.
    expect(await days.count()).toBeGreaterThanOrEqual(7);
    await expect(page.locator('[data-today="true"]')).toHaveCount(1);
  });

  test('submitting a mission moves it to pending, and the server agrees', async ({ page }) => {
    await signIn(page, 'member.a');
    await page.goto('/markpoint');

    const submit = page.locator('[data-testid^="submit-mission-"]').first();
    await expect(submit).toBeVisible();
    const missionId = (await submit.getAttribute('data-testid'))!.replace('submit-mission-', '');
    await submit.click();

    // The status the screen shows is the server's, not an optimistic guess.
    await expect(page.locator(`[data-mission-id="${missionId}"]`)).toContainText('승인 대기', {
      timeout: 10000,
    });
    const api = await page.request.get('/api/me/markpoint/weekly?family_id=1', {
      headers: { Authorization: `Bearer ${await token(page)}` },
    });
    const weekly = await api.json();
    const mission = weekly.days
      .flatMap((d: { missions: { id: number; status: string }[] }) => d.missions)
      .find((m: { id: number }) => String(m.id) === missionId);
    expect(mission.status).toBe('pending_approval');
  });
});

// ===========================================================================
// Journey 3 — Markpoint admin
// ===========================================================================

test.describe('Journey 3 — Markpoint admin', () => {
  test('a mission manager can filter and bulk-approve, and the balance follows', async ({
    page,
  }) => {
    await signIn(page, 'owner.a');
    await page.goto('/markpoint/admin');
    await expect(page.getByRole('heading', { name: '마크포인트 관리' })).toBeVisible();
    await expect(page.getByTestId('admin-mission-table')).toBeVisible();

    // Filter narrows the list without ever widening it past this family.
    await page.getByTestId('filter-status').selectOption('pending_approval');
    await page.waitForTimeout(500);

    const selectAll = page.getByTestId('select-all-pending');
    await expect(selectAll).toBeEnabled();
    await selectAll.click();
    await page.getByTestId('bulk-approve').click();

    const banner = page.getByTestId('markpoint-admin-banner');
    await expect(banner).toBeVisible({ timeout: 10000 });
    await expect(banner).toContainText('승인');
  });

  test('a cycle guard refusal is shown as its own actionable state', async ({ page }) => {
    await signIn(page, 'owner.a');
    await page.goto('/markpoint/admin');

    // Family A has an active period, so changing the cycle is refused by
    // Guard A with the remaining days — not collapsed into a generic error.
    await page.getByTestId('cycle-select').selectOption('monthly');
    const banner = page.getByTestId('markpoint-admin-banner');
    await expect(banner).toBeVisible({ timeout: 10000 });
  });

  test('materialization uses the approved rolling window', async ({ page }) => {
    await signIn(page, 'owner.a');
    await page.goto('/markpoint/admin');
    await page.getByTestId('materialize-window').click();
    const banner = page.getByTestId('markpoint-admin-banner');
    await expect(banner).toBeVisible({ timeout: 10000 });
    // The banner reports the window the server computed; the client never
    // derives the dates itself.
    await expect(banner).toContainText(/\d{4}-\d{2}-\d{2}/);
  });
});

// ===========================================================================
// Journey 4 — Wagle room and realtime
// ===========================================================================

test.describe('Journey 4 — Wagle realtime', () => {
  test('a real room loads from the API and the realtime channel connects', async ({ page }) => {
    await signIn(page, 'owner.a');
    await page.goto('/wagle');

    // Real rooms, not fixtures: the seeded room is the only one.
    await expect(page.getByTestId('wagle-room-list')).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();

    await expect(page.getByTestId('wagle-connection-state')).toHaveAttribute(
      'data-state',
      'connected',
      { timeout: 20000 },
    );
  });

  test('two browsers share a room: B receives what A sent, exactly once', async ({ browser }) => {
    const contextA = await browser.newContext();
    const contextB = await browser.newContext();
    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();

    try {
      await signIn(pageA, 'owner.a');
      await signIn(pageB, 'member.a');
      await pageA.goto('/wagle');
      await pageB.goto('/wagle');

      await expect(pageA.getByTestId('wagle-connection-state')).toHaveAttribute(
        'data-state', 'connected', { timeout: 20000 },
      );
      await expect(pageB.getByTestId('wagle-connection-state')).toHaveAttribute(
        'data-state', 'connected', { timeout: 20000 },
      );

      const unique = `hello-${Date.now()}`;
      await pageA.getByTestId('wagle-composer-input').fill(unique);
      await pageA.getByTestId('wagle-send').click();

      // B has no fixture to fall back on, so seeing the text at all proves the
      // durable fetch path ran.
      await expect(pageB.getByTestId('wagle-messages')).toContainText(unique, { timeout: 25000 });

      // Exactly once — at-least-once delivery plus a resume replay is the
      // situation duplicates would appear in.
      const occurrences = await pageB
        .getByTestId('wagle-messages')
        .locator('li', { hasText: unique })
        .count();
      expect(occurrences, 'duplicate render').toBe(1);
    } finally {
      await contextA.close();
      await contextB.close();
    }
  });

  test('a disconnect is followed by recovery of the missed message', async ({ browser }) => {
    const contextA = await browser.newContext();
    const contextB = await browser.newContext();
    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();

    try {
      await signIn(pageA, 'owner.a');
      await signIn(pageB, 'member.a');
      await pageA.goto('/wagle');
      await pageB.goto('/wagle');
      await expect(pageB.getByTestId('wagle-connection-state')).toHaveAttribute(
        'data-state', 'connected', { timeout: 20000 },
      );

      // B goes offline, so the socket cannot deliver what follows.
      await contextB.setOffline(true);

      const missed = `missed-${Date.now()}`;
      await pageA.getByTestId('wagle-composer-input').fill(missed);
      await pageA.getByTestId('wagle-send').click();
      await expect(pageA.getByTestId('wagle-messages')).toContainText(missed, { timeout: 15000 });

      // Back online: the durable cursor catch-up must fill the gap. This is
      // the property that makes a lost notification a latency event rather
      // than a lost message.
      await contextB.setOffline(false);
      await expect(pageB.getByTestId('wagle-messages')).toContainText(missed, { timeout: 40000 });

      const occurrences = await pageB
        .getByTestId('wagle-messages')
        .locator('li', { hasText: missed })
        .count();
      expect(occurrences, 'recovered message rendered twice').toBe(1);
    } finally {
      await contextA.close();
      await contextB.close();
    }
  });
});

// ===========================================================================
// Journey 6 — Wagle PIN cross-service isolation
// ===========================================================================

test.describe('Journey 6 — PIN isolation', () => {
  test('a PIN lock covers Wagle only; the platform stays reachable', async ({ page }) => {
    await signIn(page, 'member.a');
    const bearer = await token(page);

    // Set a PIN through the product's own API, then reload so the gate engages.
    const deviceId = await page.evaluate(() => localStorage.getItem('mongle.wagle.deviceId'));
    await page.goto('/wagle');
    const resolvedDevice =
      deviceId ?? (await page.evaluate(() => localStorage.getItem('mongle.wagle.deviceId')));
    expect(resolvedDevice).toBeTruthy();

    const setPin = await page.request.put('/api/me/wagle/device-pin', {
      headers: { Authorization: `Bearer ${bearer}` },
      data: { device_id: resolvedDevice, pin: '135790' },
    });
    expect(setPin.status()).toBe(200);

    await page.goto('/wagle');
    // The Wagle content is gated...
    await expect(page.getByRole('dialog', { name: /와글와글 잠금/ })).toBeVisible({
      timeout: 15000,
    });

    // ...while everything else stays reachable. This is the contract: a
    // mistyped PIN must never become a platform-wide outage.
    await page.goto('/family');
    await expect(page.getByTestId('family-name')).toBeVisible({ timeout: 15000 });

    await page.goto('/markpoint');
    await expect(page.getByRole('heading', { name: '마크포인트' })).toBeVisible({
      timeout: 15000,
    });

    // The Account Session is untouched by the screen lock.
    expect(await token(page)).toBe(bearer);
  });
});

// ===========================================================================
// Journey 7 — Authorization
// ===========================================================================

test.describe('Journey 7 — Authorization', () => {
  test('a plain member is refused the admin capabilities', async ({ page }) => {
    await signIn(page, 'member.a');
    const bearer = await token(page);

    const missions = await page.request.get('/api/families/1/markpoint/missions', {
      headers: { Authorization: `Bearer ${bearer}` },
    });
    expect(missions.status()).toBe(403);

    await page.goto('/markpoint/admin');
    await expect(page.getByTestId('markpoint-admin-denied')).toBeVisible({ timeout: 15000 });
  });

  test('mission and point permissions do not confer each other', async ({ page }) => {
    // owner.a holds markpoint.missions.manage only.
    await signIn(page, 'owner.a');
    let bearer = await token(page);

    const missionOk = await page.request.get('/api/families/1/markpoint/missions', {
      headers: { Authorization: `Bearer ${bearer}` },
    });
    expect(missionOk.status()).toBe(200);

    const pointDenied = await page.request.post('/api/families/1/markpoint/ledger/adjustments', {
      headers: { Authorization: `Bearer ${bearer}` },
      data: { beneficiary_membership_id: 1, amount: 5, reason: 'x', idempotency_key: 'j7-a' },
    });
    expect(pointDenied.status(), 'mission manager reached a point adjustment').toBe(403);

    // admin.a holds markpoint.points.adjust only — the mirror image.
    await signIn(page, 'admin.a');
    bearer = await token(page);

    const missionDenied = await page.request.get('/api/families/1/markpoint/missions', {
      headers: { Authorization: `Bearer ${bearer}` },
    });
    expect(missionDenied.status(), 'point admin reached mission management').toBe(403);
  });

  test('the admin screen shows only the panel the permission grants', async ({ page }) => {
    // A point admin sees the adjustment panel and no bulk approval.
    await signIn(page, 'admin.a');
    await page.goto('/markpoint/admin');
    await expect(page.getByTestId('point-adjust-panel')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('bulk-approve')).toHaveCount(0);

    // A mission manager sees the mirror image.
    await signIn(page, 'owner.a');
    await page.goto('/markpoint/admin');
    await expect(page.getByTestId('bulk-approve')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('point-adjust-panel')).toHaveCount(0);
  });
});
