import { expect, test, type Page } from '@playwright/test';

/**
 * MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001 — Phase B real-data-wiring
 * verification.
 *
 * Account-native tests sign in through the product's own real screen
 * (`/login`, `1a-1`), same convention as `03-target-ui.spec.ts`. That
 * screen's submit was itself intentionally parked since the A1 pass
 * (`event.preventDefault()` only, no real login call); this task wired it
 * to the real `POST /api/auth/account/login` (already-built-but-orphaned
 * `shared/api/accountAuthApi.ts`), which is both a W7.5 Matrix row
 * (`1a-1`) in its own right and the precondition for every other
 * Account-native test in this file being able to sign in through the real
 * UI rather than injecting a token.
 *
 * Covers the screens Phase B wired to real backend calls this pass:
 * `1r` (family creation), `1q` (family member list — the real gap
 * discovered while wiring it, `MembershipSummary.account_display_name`),
 * `2t` (admin notification send, legacy admin login). Phase C additions:
 * `1t` (Wagle room member list — the same display-name gap shape as `1q`,
 * this time on `ParticipantResponse`).
 *
 * `2s`/`1u` (Wagle device-PIN initial setup / change) were attempted
 * against the same disposable stack and **not** added here: the real
 * endpoint requires a 6-digit PIN, this frozen W7.3 canonical Screen has a
 * 4-dot/4-key design, and extending it would be a visual-baseline
 * redesign — reverted, reclassified `DESIGN_CONTRACT_MISMATCH`/
 * `HUMAN_GATE` in the W7.5 Matrix rather than wired against a UI it
 * cannot correctly serve. See the Matrix `2s`/`1u` rows and this task's
 * Report for detail.
 *
 * Phase C additions: `1f` (profile — real display name/level/points, not
 * the fixture), `1k` (mission checklist toggle — real
 * `PATCH .../missions/{id}/checklist`), `2g` (Wagle reply — real
 * `reply_to_message_id`, verified via a real quoted-preview render). `1s`
 * (mission reject) is not added here: its real fields
 * (`rejection_reason`/`reviewer_display_name`) are already covered by
 * `backend/tests/test_w75_phase_c_extensions.py` at the HTTP layer, and
 * this file's own Test Policy is to add the minimum test for an otherwise
 * unprotected flow, not to duplicate coverage that already exists.
 */

const PASSWORD = 'Synthetic!Pass9';

async function signIn(page: Page, username: string) {
  await page.goto('/login');
  await page.getByTestId('account-username').fill(username);
  await page.getByTestId('account-password').fill(PASSWORD);
  await page.getByTestId('account-login-submit').click();
  await expect(page).toHaveURL(/\/family$/, { timeout: 15000 });
}

test.describe('1a-1 — Account-native login', () => {
  test('a real account signs in and reaches /family', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    await signIn(page, 'member.a');
    expect(errors).toHaveLength(0);
    const tokenValue = await page.evaluate(() => sessionStorage.getItem('accessToken'));
    expect(tokenValue).toBeTruthy();
  });

  test('a wrong password shows a real error, not a silent no-op', async ({ page }) => {
    await page.goto('/login');
    await page.getByTestId('account-username').fill('member.a');
    await page.getByTestId('account-password').fill('WrongPassword!');
    await page.getByTestId('account-login-submit').click();
    await expect(page.getByRole('status')).toBeVisible({ timeout: 8000 });
    await expect(page).toHaveURL(/\/login$/);
  });
});

test.describe('1r — family creation', () => {
  test('creating a family calls the real API and appears in the family list', async ({ page }) => {
    await signIn(page, 'owner.a');
    await page.goto('/onboarding');
    const familyName = `Playwright 검증 ${Date.now()}`;
    await page.locator('input').first().fill(familyName);

    const [response] = await Promise.all([
      page.waitForResponse((res) => res.url().endsWith('/api/families') && res.request().method() === 'POST'),
      page.getByRole('button', { name: /다음/ }).click(),
    ]);
    expect(response.status()).toBe(201);

    // Flow advances to the PIN step (canonical 2s) on success.
    await expect(page.locator('[data-canonical-screen-id="2s"]')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('1q — family member list', () => {
  test('member names are real, not raw account IDs', async ({ page }) => {
    await signIn(page, 'member.a');
    const [response] = await Promise.all([
      page.waitForResponse((res) => /\/api\/families\/\d+\/members$/.test(res.url()) && res.request().method() === 'GET'),
      page.goto('/family/members'),
    ]);
    expect(response.status()).toBe(200);
    const bodyText = await page.locator('body').innerText();
    expect(bodyText).toMatch(/Synthetic/);
  });
});

test.describe('1t — Wagle room member list', () => {
  test('room member names are real, not raw family_membership_ids', async ({ page }) => {
    // member.a belongs to exactly one family, so the store auto-selects it
    // (owner.a belongs to two and would land on the family-selector instead).
    await signIn(page, 'member.a');
    await page.goto('/wagle');
    await page.waitForTimeout(500);
    const [response] = await Promise.all([
      page.waitForResponse((res) => /\/wagle\/rooms\/[^/]+\/participants$/.test(res.url()) && res.request().method() === 'GET'),
      page.getByText('⚙', { exact: true }).click(),
    ]);
    expect(response.status()).toBe(200);
    const bodyText = await page.locator('body').innerText();
    expect(bodyText).toMatch(/Synthetic/);
  });
});

test.describe('1f — profile', () => {
  test('the profile screen shows a real display name and level, not the fixture', async ({ page }) => {
    await signIn(page, 'member.a');
    const [response] = await Promise.all([
      page.waitForResponse((res) => res.url().endsWith('/api/me') && res.request().method() === 'GET'),
      page.goto('/profile'),
    ]);
    expect(response.status()).toBe(200);
    const bodyText = await page.locator('body').innerText();
    // The fixture's name is "서연"; the seeded real Account is
    // "Synthetic Service Participant". Seeing the real name (and not the
    // fixture one) is the only way to tell this screen is actually wired.
    expect(bodyText).toMatch(/Synthetic Service Participant/);
    expect(bodyText).not.toContain('서연');
  });
});

test.describe('1k — mission checklist toggle', () => {
  test('tapping a checklist item calls the real endpoint and the change persists on reload', async ({ page }) => {
    // Setup via the real API directly, as the plain family owner — mission
    // *creation* is already covered by this task's backend tests; this
    // test's own job is the checklist *toggle* endpoint and its UI wiring.
    await signIn(page, 'owner.a');
    const ownerToken = await page.evaluate(() => sessionStorage.getItem('accessToken'));
    const authHeaders = { Authorization: `Bearer ${ownerToken}` };
    const context = await (await page.request.get('/api/account-context', { headers: authHeaders })).json();
    const familyId = context.families.find((f: { name: string }) => f.name === 'Synthetic Family Alpha').id;
    const members = await (await page.request.get(`/api/families/${familyId}/members`, { headers: authHeaders })).json();
    const assignee = members.find((m: { account_display_name: string }) => m.account_display_name === 'Synthetic Service Participant');
    const created = await page.request.post(`/api/families/${familyId}/markpoint/missions`, {
      headers: authHeaders,
      data: {
        assignee_membership_id: assignee.id,
        title: 'Playwright 체크리스트 미션',
        scheduled_for: new Date().toISOString().slice(0, 10),
        reward_amount: 5,
        checklist: ['Playwright 항목 A', 'Playwright 항목 B'],
      },
    });
    expect(created.ok()).toBeTruthy();
    const missionId = (await created.json()).id;

    // Act: the assignee (member.a) opens the mission and taps one item.
    await signIn(page, 'member.a');
    await page.goto('/markpoint');
    await page.getByTestId(`open-mission-detail-${missionId}`).click();
    await expect(page.getByTestId('markpoint-mission-detail-overlay')).toBeVisible();
    const [toggleResponse] = await Promise.all([
      page.waitForResponse(
        (res) => res.url().endsWith(`/markpoint/missions/${missionId}/checklist`) && res.request().method() === 'PATCH',
      ),
      page.getByText('Playwright 항목 A', { exact: true }).click(),
    ]);
    expect(toggleResponse.status()).toBe(200);
    expect((await toggleResponse.json()).checklist[0].done).toBe(true);

    // Assert: a fresh load shows the toggle persisted server-side, not just
    // in local component state.
    await page.reload();
    await page.getByTestId(`open-mission-detail-${missionId}`).click();
    await expect(page.getByTestId('markpoint-mission-detail-overlay')).toBeVisible();
    const firstCheck = page.getByText('Playwright 항목 A', { exact: true }).locator('..');
    await expect(firstCheck.locator('i')).toHaveText('✓');
  });
});

test.describe('2g — Wagle reply', () => {
  test('replying to a message sends a real reply_to_message_id and renders the quoted preview', async ({ page }) => {
    await signIn(page, 'member.a');
    await page.goto('/wagle');
    await page.waitForTimeout(500);

    const originalBody = `Playwright 원본 ${Date.now()}`;
    await page.getByTestId('wagle-composer-input').fill(originalBody);
    const [sendResponse] = await Promise.all([
      page.waitForResponse((res) => /\/wagle\/rooms\/[^/]+\/messages$/.test(res.url()) && res.request().method() === 'POST'),
      page.getByTestId('wagle-send').click(),
    ]);
    expect(sendResponse.status()).toBe(201);
    const originalId = (await sendResponse.json()).id;

    await page.getByTestId(`wagle-reply-${originalId}`).click();
    await expect(page.getByTestId('wagle-reply-overlay')).toBeVisible();
    await page.getByRole('button', { name: '전송' }).click();
    await expect(page.getByTestId('wagle-reply-overlay')).toHaveCount(0);
    await expect(page.getByTestId('wagle-reply-banner')).toBeVisible();

    const replyBody = `Playwright 답장 ${Date.now()}`;
    await page.getByTestId('wagle-composer-input').fill(replyBody);
    const [replyResponse] = await Promise.all([
      page.waitForResponse((res) => /\/wagle\/rooms\/[^/]+\/messages$/.test(res.url()) && res.request().method() === 'POST'),
      page.getByTestId('wagle-send').click(),
    ]);
    expect(replyResponse.status()).toBe(201);
    expect((await replyResponse.json()).reply_to_message_id).toBe(originalId);

    await expect(page.getByTestId('wagle-reply-banner')).toHaveCount(0);
    const replyRow = page.locator(`li[data-message-id="${(await replyResponse.json()).id}"]`);
    await expect(replyRow.getByTestId(`wagle-reply-quote-${(await replyResponse.json()).id}`)).toContainText(originalBody);
  });
});

test.describe('2t — admin notification send', () => {
  async function adminSignIn(page: Page) {
    await page.goto('/');
    await page.getByLabel('관리자 로그인').click();
    await page.getByPlaceholder('아이디 입력').fill('dad');
    await page.getByPlaceholder('비밀번호 입력').fill(process.env.MONGLE_W75_ADMIN_PASSWORD ?? '');
    await page.getByRole('button', { name: '로그인' }).click();
    await expect(page).toHaveURL(/\/admin/, { timeout: 15000 });
  }

  test('sending a notification calls the real API and closes the form on success', async ({ page }) => {
    test.skip(
      !process.env.MONGLE_W75_ADMIN_PASSWORD,
      'Requires MONGLE_W75_ADMIN_PASSWORD for the seeded legacy admin account ("dad") — ' +
      'not stored in this repository per tests/README.md secret-handling rules. Set it in the ' +
      'local shell before running this spec to exercise the admin-login branch; the isolated ' +
      'backend+Playwright verification already run for this task (see QA evidence) used a ' +
      'throwaway synthetic credential created directly in a disposable DB for the same reason.',
    );
    await adminSignIn(page);
    await page.goto('/admin/notifications');
    await page.getByRole('button', { name: '알림 발송' }).click();
    const overlay = page.locator('[data-testid="admin-notification-send-overlay"]');
    await overlay.locator('input').fill('Playwright 검증 제목');
    await overlay.locator('textarea').fill('Playwright 검증 본문');
    const [response] = await Promise.all([
      page.waitForResponse((res) => res.url().endsWith('/api/admin/notifications') && res.request().method() === 'POST'),
      overlay.getByRole('button', { name: '알림 발송' }).click(),
    ]);
    expect(response.status()).toBe(201);
    await expect(overlay).toHaveCount(0);
  });
});

test.describe('3c/3d/3e — Wagle board reuse, comments, reactions', () => {
  // owner.a is the only seeded account with the Wagle `room_admin` role
  // (required to create the board Room) and belongs to two Families, so
  // the family selector must be resolved explicitly before /wagle/board —
  // unlike member.a (single Family, auto-selected) used elsewhere in this
  // file. A prior ad hoc verification of this exact flow was run and then
  // deleted; per the W7.5 scope-reconciliation pass this is now the
  // permanent, reproducible replacement for that evidence.
  test('a real board post renders, opens, and accepts a real comment; reactions rank it in Popular', async ({ page }) => {
    await signIn(page, 'owner.a');
    await page.selectOption('select', { label: 'Synthetic Family Alpha' });
    await page.goto('/wagle/board');
    // W7.5 Independent QA remediation: `WagleBoardPage.tsx`'s own mount
    // effect does the identical find-the-board-room-or-create-it sequence
    // this test's own script does below (`listRooms` -> `createRoom` if
    // none titled `__family_board__` exists yet). On a brand-new Family
    // with no board room, both this test's script and the app's own effect
    // can race to create one, producing two rooms with the same sentinel
    // title — `list_popular_posts`'s `WHERE title = ... .first()` lookup
    // then has no way to know which one actually has this test's post,
    // and can silently rank the wrong (empty) room. Waiting for the app's
    // own network activity to settle first means its effect's own
    // `listRooms`/`createRoom` has already run by the time this script
    // does its own lookup, so the script finds the app's real room instead
    // of creating a second one.
    await page.waitForLoadState('networkidle');

    const postTitle = `Playwright 게시글 ${Date.now()}`;
    // The board Room and its first post are created directly over the
    // already-real Wagle HTTP API (same endpoints `2g`'s reply-to and this
    // task's own board-reuse Slice call) — `3c`'s own frozen Screen has no
    // compose form to create a post from (`onWrite` is deliberately
    // unwired, see WagleBoardPage.tsx's own top comment), so seeding the
    // post this way is the only way to get one onto the board at all,
    // matching how `1r`'s onboarding-created family or `1t`'s seeded
    // participants are set up elsewhere in this file.
    const token = await page.evaluate(() => sessionStorage.getItem('accessToken'));
    const authHeaders = { Authorization: `Bearer ${token}` };
    const context = await (await page.request.get('/api/account-context', { headers: authHeaders })).json();
    const familyId = context.families.find((f: { name: string }) => f.name === 'Synthetic Family Alpha').id;
    const rooms = await (await page.request.get(`/api/families/${familyId}/wagle/rooms`, { headers: authHeaders })).json();
    let board = rooms.find((r: { title: string }) => r.title === '__family_board__');
    if (!board) {
      const created = await page.request.post(`/api/families/${familyId}/wagle/rooms`, {
        headers: authHeaders,
        data: { room_type: 'GROUP', title: '__family_board__' },
      });
      board = await created.json();
    }
    const posted = await page.request.post(`/api/families/${familyId}/wagle/rooms/${board.id}/messages`, {
      headers: authHeaders,
      data: { client_message_id: `board-${Date.now()}`, body: `[자유] ${postTitle}\n플레이라이트 검증` },
    });
    expect(posted.ok()).toBeTruthy();
    const postId = (await posted.json()).id;

    // 3c: the real post is visible after a reload of the board page.
    await page.reload();
    await expect(page.getByText(postTitle)).toBeVisible({ timeout: 10000 });

    // 3d: opening it and submitting a real comment through the Screen's
    // own input renders in the thread.
    await page.getByText(postTitle).click();
    const commentText = `Playwright 댓글 ${Date.now()}`;
    await page.getByPlaceholder('댓글을 입력하세요').fill(commentText);
    await page.getByRole('button', { name: '➤' }).click();
    await expect(page.getByText(commentText)).toBeVisible({ timeout: 10000 });

    // 3e: a real reaction (added directly over the API, since neither
    // frozen Screen has a like-button click target — see this task's own
    // PM Decision Package, GATE list) changes the ranked Popular result.
    await page.request.post(`/api/families/${familyId}/wagle/rooms/${board.id}/messages/${postId}/reactions`, { headers: authHeaders });
    // The post/comment view is local component state in WagleBoardPage
    // (`openPostMessageId`), not a routed URL, so returning to the board's
    // main list must go through the composer's own "←" control (onCancel)
    // rather than page.goBack(), which would navigate the browser away from
    // /wagle/board entirely.
    await page.getByRole('button', { name: '←' }).click();

    // W7.5 Independent QA remediation (F1 evidence gap): the Popular Posts
    // panel is an *overlay* rendered on top of the still-mounted board list
    // (`WagleBoardPage.tsx`'s `showPopular && <div data-testid="wagle-board-
    // popular-overlay">`) — the board list underneath is never unmounted and
    // already contains `postTitle` from the assertion at line ~302 above. A
    // page-wide `page.getByText(postTitle)` after opening this overlay would
    // therefore pass even if the ranking fetch itself 500s and the page
    // silently falls back to an empty list (`.catch(() => setPopularPosts
    // ([]))`) — exactly the false positive that let the interval-binding
    // 500 (fixed in `wagle/service.py`'s `list_popular_posts`) ship
    // undetected. Assert the real network response first, then scope every
    // subsequent assertion to the overlay's own `data-testid`, not the page.
    const [popularResponse] = await Promise.all([
      page.waitForResponse((res) => res.url().includes('/wagle/board/popular') && res.request().method() === 'GET'),
      page.getByRole('button', { name: '인기 게시글 보기' }).click(),
    ]);
    expect(popularResponse.status()).toBe(200);
    const popularPayload = await popularResponse.json();
    expect(popularPayload.some((p: { message_id: string }) => p.message_id === postId)).toBeTruthy();

    const popularOverlay = page.getByTestId('wagle-board-popular-overlay');
    await expect(popularOverlay).toBeVisible();
    await expect(popularOverlay.getByText(postTitle)).toBeVisible({ timeout: 10000 });
  });
});
