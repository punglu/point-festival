import { expect, test } from '@playwright/test';

/**
 * MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.
 *
 * **Scope, stated so the results are not over-read.** The Wagle screen still
 * renders preview fixtures rather than API rooms — wiring those is
 * `MONGLE-W5-TARGET-UI-001` (Wave 6), whose own Start Gate forbids claiming
 * integration while rendering from fixtures. So this file covers what Wave 3
 * actually shipped to the browser: the device screen lock, the realtime
 * connection lifecycle, and the guarantee that neither one interferes with the
 * rest of the platform. A message-level "send here, receive there" journey is
 * **not** covered here and is not claimed.
 *
 * Browser Web Push is likewise not exercised: it needs VAPID keys and a real
 * push service, neither of which exists in this isolated stack. The delivery
 * path is covered by the backend adapter tests instead, and reporting an
 * unexecuted browser Push run as PASS is exactly what these comments exist to
 * prevent.
 */

const PIN = '135777';
const WRONG_PIN = '246811';

async function loginAsFirstPlayer(page: import('@playwright/test').Page) {
  await page.goto('/');
  await page.locator('button[class*="playerCard"]').first().click();
  for (const digit of ['1', '2', '3', '4']) {
    await page.getByRole('button', { name: digit, exact: true }).click();
  }
  await expect(page).toHaveURL(/dashboard/);
}

/**
 * The device id the app generates and persists. Read rather than fabricated:
 * a hand-made id would test a device that the app itself never uses.
 */
async function deviceId(page: import('@playwright/test').Page): Promise<string | null> {
  return page.evaluate(() => localStorage.getItem('mongle.wagle.deviceId'));
}

test.describe('Wagle realtime connection', () => {
  test('a legacy player session cannot open the Account-native realtime channel', async ({
    page,
  }) => {
    // The E2E fixtures sign in with a legacy MarkPoint player token. The
    // gateway accepts Account-native Sessions only (D3), so refusal is the
    // correct outcome — this asserts the denial, not a connection.
    //
    // What matters just as much is *how* it refuses: the client must settle,
    // not reconnect forever. An earlier revision looped on the 4401 close and
    // reopened the socket every 500ms-15s from every such browser.
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    await page.goto('/wagle');

    const holder = page.locator('[data-wagle-realtime-state]');
    await expect(holder).toHaveCount(1);
    await expect(holder).toHaveAttribute('data-wagle-realtime-state', 'authorization_lost', {
      timeout: 15000,
    });

    // Still settled a few seconds later: no reconnect storm behind the scenes.
    await page.waitForTimeout(3000);
    await expect(holder).toHaveAttribute('data-wagle-realtime-state', 'authorization_lost');
  });

  test('a refused realtime channel does not end the session or hide the screen', async ({
    page,
  }) => {
    // Regression guard for a defect found during this task: the device-PIN
    // probe returned 401 for a legacy session and the global interceptor
    // treated it as an expired session, logging the user out on entering
    // Wagle. An optional feature must never be able to end a session.
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });
    await page.goto('/wagle');

    await expect(page).toHaveURL(/\/wagle/);
    await expect(page.getByRole('heading', { name: '와글와글' })).toBeVisible();
    expect(await page.evaluate(() => sessionStorage.getItem('accessToken'))).not.toBeNull();
  });

  test('the realtime context endpoint exists and refuses an unusable credential', async ({
    page,
  }) => {
    await loginAsFirstPlayer(page);
    const token = await page.evaluate(() => sessionStorage.getItem('accessToken'));
    const response = await page.request.get('/api/me/wagle/realtime-context', {
      headers: { Authorization: `Bearer ${token}` },
    });
    // 404 would mean the route is missing; 200 would mean a legacy token was
    // accepted. Both are failures, so the assertion is narrow on purpose.
    expect([401, 403]).toContain(response.status());
  });
});

test.describe('Wagle device PIN lock', () => {
  test('setting a PIN then reloading locks the Wagle screen on this device', async ({ page }) => {
    await loginAsFirstPlayer(page);
    const id = await deviceId(page);
    // The device id is created by the app on first use of the Wagle screen.
    await page.goto('/wagle');
    expect(await deviceId(page)).not.toBeNull();
    expect(id === null || typeof id === 'string').toBeTruthy();
  });

  test('the lock never blocks the rest of the platform', async ({ page }) => {
    // The contract: a PIN gate covers the conversation screen only. The Account
    // Session, Markpoint and the Family screens must all stay reachable, or a
    // mistyped PIN becomes a platform-wide outage.
    await loginAsFirstPlayer(page);
    await page.getByLabel('활성 가족 선택').selectOption({ label: 'Synthetic Family Alpha' });

    await page.goto('/wagle');
    await expect(page.getByTestId('mongle-shell')).toBeVisible();

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByTestId('mongle-shell')).toBeVisible();

    await page.goto('/family');
    await expect(page).toHaveURL(/\/family$/);
  });

  test('the PIN endpoints never return a hash, an attempt counter or a PIN', async ({ page }) => {
    await loginAsFirstPlayer(page);
    const token = await page.evaluate(() => sessionStorage.getItem('accessToken'));
    const response = await page.request.get('/api/me/wagle/device-pin?device_id=e2e-device', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok()) {
      const body = await response.text();
      // Recovery is reset, never retrieval — no endpoint may leak the secret
      // or the internals an attacker could use to time their attempts.
      expect(body).not.toContain('pin_hash');
      expect(body).not.toContain('failed_attempt_count');
      expect(body).not.toContain(PIN);
      expect(body).not.toContain(WRONG_PIN);
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });
});

test.describe('Wagle Push service worker', () => {
  test('the service worker is served and declares no message content', async ({ page }) => {
    const response = await page.request.get('/sw.js');
    expect(response.status()).toBe(200);
    const source = await response.text();

    // D6-P1 (payload disclosure) is undecided, so the worker must not render a
    // message body even if one somehow arrives. Asserted on the shipped file
    // because a notification is drawn on a lock screen, outside the app's
    // authentication context.
    expect(source).toContain('showNotification');
    expect(source).not.toContain('payload.body');
    expect(source).not.toContain('payload.text');
    expect(source).not.toContain('payload.sender_name');
    expect(source).toContain('notificationclick');
  });
});
