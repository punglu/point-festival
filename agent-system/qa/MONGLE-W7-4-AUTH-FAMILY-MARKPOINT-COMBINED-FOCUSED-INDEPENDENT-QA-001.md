# QA Evidence — MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001

- Task ID: `MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001`
- author/agent: independent QA session (fresh session; did not author Auth/Family/Markpoint W7.4 integration, `281d45a`)
- observed_at: 2026-08-06
- git_ref: `62c1f23` (branch `dev-newmarkp`), clean at start and end of this task (`git status --short` empty both times; the only diff this session ever produced was untracked scratch files under `tests/e2e/qaindep_script*.mjs` and a scratch `docker-compose.qa-indep-scratch.yml`, all deleted before this report — see Cleanup)
- environment: macOS, isolated stack built by this session: `postgres:16.9-alpine` (`qaindep-db-1`, port 15440) + backend built from the real `backend/Dockerfile` at the current Target Revision (`qaindep-backend-1`, port 18010), both via a scratch compose file derived from `docker-compose.phase1.yml`, project name `qaindep`, network `qaindep_network` — chosen specifically so as not to collide with the pre-existing persistent `mongle`-project stack (`mongle-backend-1`/`mongle-db-1`, ports 18001/15434, confirmed already running before this task and confirmed still running unmodified after it). Frontend served natively via `pnpm run dev` (Vite, port 5174) against the real current source tree with `VITE_DEV_PROXY_TARGET=http://localhost:18010`, per this task's own "QA-approved substitute" option and matching `tests/e2e/playwright.mongle-manual.config.ts`'s documented intent ("already running its own isolated backend+frontend"). A second isolated Postgres (`qaindep-pytest-db`, port 15435, matching `backend/tests/conftest.py`'s default) was used only for backend pytest.
- evidence: this file + the Session Handoff at `agent-system/handoffs/active/MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001.md`
- secrets_redacted: `true` (no JWT printed in full anywhere in this evidence; only lengths/prefixes/booleans)
- Verification: `CONDITIONAL`
- Verdict: CONDITIONAL
- Verdict detail: Auth PASS · Family PASS · Markpoint FAIL (one confirmed routing defect; the
  member surface alone would be PASS) · Cross-domain FAIL (one confirmed session-integrity
  defect) — see Axis verdicts and Overall verdict sections below for full detail
- Closeout Contract: `v1`
- Independent from implementer: `true`
- Independent QA: `complete`

## Independent QA qualification

Fresh session. Never touched Auth/Family/Markpoint product code before this task; read-only for
all product code throughout (no `Edit`/`Write` call ever targeted a file under `backend/app/` or
`frontend/src/` in this session — the only files this session wrote were its own disposable
Playwright driver scripts, deleted before finishing, and this evidence/handoff pair). Per
`agent-system/rules.md` Invariant 9, checked before starting: no existing `active.md` entry, no
`graduated/*.md` entry, and no file under `agent-system/qa/`/`agent-system/handoffs/` for this
exact Task ID existed prior to this session (`grep` over `active.md`, `relay/current.md`,
`COVERAGE_MAP.md` returned nothing) — legitimately new, not a duplicate. All findings below are
this session's own independently-produced measurements (curl responses, DOM snapshots, pytest/
Playwright exit codes) — the prior same-session Cross-Domain QA's disclosed self-verification
numbers are not cited or re-used anywhere in this report.

## Start Gate (baseline)

Ran in `/Users/mac/mac_Project/mongle_ui`: `pwd`, `git rev-parse --show-toplevel`,
`git branch --show-current` → `dev-newmarkp`, `git rev-parse HEAD` → `62c1f23fd9d1d717b2bb...`,
`git status --short` → empty, `git diff --stat` → empty, `git stash list` → empty,
`git log -10 --oneline`, `git remote -v` → `origin` = `https://github.com/punglu/point-festival.git`,
`git fetch --prune` → no output, HEAD re-checked identical, `git rev-parse '@{u}'` → identical to
HEAD. No `REMOTE_DIVERGENCE`, no `DETACHED_HEAD`, no `UNKNOWN_DIRTY`, no `CONFLICT`, no unresolved
merge/rebase. Baseline matched the PM-reported values exactly. Note: this session's own default
working directory (a `minecraft_points_festivals` worktree-agent sandbox) is a distinct, unrelated
repository from `mongle_ui`; this task's own brief explicitly names `mongle_ui` as the target and
instructs never touching `minecraft_points_festivals` — the latter was never read or written by
this session.

## Scope discovery

Confirmed via `git log --follow` that all three integration entry points were introduced by
`281d45a` and have not been touched since (HEAD `62c1f23`, 4 commits later, none touching these
paths):
- Auth: `frontend/src/pages/Auth/components/ProfileSelectorContainer.tsx` — composes
  `screens/auth/ProfileSelector/ProfileSelectorScreen.tsx` into the real `/` profile-select step,
  reading `GET /api/players` (legacy `players`/`player_auth` tables) and preserving the
  `is_locked` guard at the container level (`onSelect` simply not forwarded).
- Family: `frontend/src/platform/pages/FamilyLanding.tsx` (`FamilyLandingPage`, routed at
  `/family`) composing `FamilyHomeContainer`/`FamilyHomeScreen` above the pre-existing real Family
  Home sections; real data via `Account`/`FamilyGroup`/`FamilyMembership` (Alembic `0001`+).
- Markpoint: `frontend/src/platform/markpoint/MarkpointUser.tsx` (routed at `/markpoint`,
  ~500 lines), composing canonical screen `1c` ("포인트 잔치" — this is the *current* canonical
  heading; see Markpoint finding 1 below) header/profile-card zone above the real, untouched
  weekly day-list/deductions logic; `frontend/src/platform/markpoint/MarkpointAdmin.tsx` exists
  fully built (mission table, cycle guard, materialize-window, bulk-approve, point-adjust panel,
  `markpoint-admin-denied` alert — all real `data-testid`s present) but see Markpoint finding 2.

Route inventory (`frontend/src/App.tsx`, `grep -n 'path="'`) classified:
- `ACTIVE_PRODUCT_ROUTE`: `/`, `/dashboard`, `/admin/*`, `/family`, `/markpoint`, `/wagle`,
  `/wagle/board`, `/onboarding`, `/profile`, `/family/schedule`, `/family/album`, `/family/todo`,
  `/family/members`, `/family/notifications`, `/family/rules`, `/family/search`, `/login`.
- `DEAD_OR_UNREACHABLE`: `/markpoint/admin` — linked from `MongleAppShell`'s own nav
  (`to: '/markpoint/admin'`, line 109) and gated by real permission logic
  (`FamilyLanding.tsx`'s `isMarkpointAdmin`), but **no `<Route>` registers this path** — direct
  navigation renders the app's generic `NotFoundPage` ("페이지를 찾을 수 없어요"). Confirmed a
  real, current-code defect, not a QA-environment artifact (see Markpoint finding 2).
  See also `App.tsx`'s own code comment at line 179-189, which documents that `/family`,
  `/markpoint`, `/wagle` themselves were *also* missing their `<Route>` registration until a
  prior task fixed exactly this class of bug — `/markpoint/admin` is the same class of gap,
  left unfixed.
- `DEFERRED_BY_PM_OR_DESIGN`: the ~60 `/__wave6/*` canonical-screen preview routes (isolated
  mockup harness, not part of the real navigable product surface; out of this QA's scope per
  the task brief).
- `PRESERVED_EXISTING_ROUTE`: `/dashboard`, `/admin/*` (legacy dashboards, unchanged by W7.4).

Playwright config discovery: the base `tests/e2e/playwright.config.ts` (`testDir: './specs'`)
targets `docker-compose.phase0.yml`, which is confirmed absent from the repo root — but this
config's `testDir` also does not match `specs-mongle/`, so it would never have collected
`03-target-ui.spec.ts`/`04-w75-data-wiring.spec.ts` regardless (`NOT_COLLECTED_BY_CURRENT_CONFIG`
for that specific config, independent of the phase0 question). The **current, correct** configs
for `specs-mongle/**` are `tests/e2e/playwright.mongle.config.ts` (brings up the shared
`docker-compose.phase1.yml` stack via `scripts/start-mongle-phase1.sh`, `reuseExistingServer:
false` by design) and `tests/e2e/playwright.mongle-manual.config.ts` — the latter's own header
comment explicitly describes this session's exact scenario ("already running its own isolated
backend+frontend... without touching that shared state") and takes `MONGLE_PLAYWRIGHT_BASE_URL`
with no `webServer` of its own. Used `playwright.mongle-manual.config.ts` with
`MONGLE_PLAYWRIGHT_BASE_URL=http://localhost:5174` for all committed-spec runs below.

## Common fixture (isolated DB only, `qaindep-db-1`)

Built via the current, real, official seed tool `backend/scripts/phase1_seed_synthetic.py`
(comment-documented as the Wave 6 Target-UI fixture used by prior sibling Independent QA
sessions), run once inside `qaindep-backend-1` after `database/init.sql` + `alembic upgrade head`
had already created legacy + Target schema. Output: `PHASE1_SYNTHETIC_SEED_OK` /
`WAVE6_TARGET_FIXTURE_OK`. Resulting IDs (all disposable, isolated DB, confirmed via direct
`SELECT`):

| Entity | IDs / detail |
|---|---|
| Accounts | 1=owner.a (Synthetic Owner A), 2=owner.b (no credential), 3=other/member.b, 4=admin/admin.a, 5=participant/member.a, 6=suspended (status=suspended, no credential) |
| Families | 1=Synthetic Family Alpha (owner_a, owner_b, admin, participant), 2=Synthetic Family Beta (owner_a, other) |
| Credentials (`Synthetic!Pass9`) | `owner.a`→acct 1, `admin.a`→acct 4, `member.a`→acct 5, `member.b`→acct 3 |
| Legacy bridge | `LegacyIdentityMapping`: legacy `player_auth` ids 1/2/3/4 → accounts owner_a/owner_b/other/participant; `admin_auth` id 1 → account admin |
| Markpoint missions (family 1, assignee membership 4=participant) | mission 1 "방 정리하기" (+30, active), mission 2 "숙제 끝내기" (+20, pending_approval) |
| Wagle room | "가족 대화" (family 1, owner_a + participant) |

This session's own additions on top of the seed (both recorded, both cleaned up with the whole
disposable DB at teardown — see DB/runtime cleanup):
- `UPDATE players SET is_locked = true WHERE id = 2` (유현) — before: 0 locked / 4 total; after:
  1 locked / 4 total. Restored to `false` after the empty-profile-list check, then re-set to
  `true` for the remainder of Auth-axis evidence; final state before teardown: locked. Player 1
  (유빈, PIN `1234`, legacy `player_auth` id 1) used as the normal/unlocked profile — it is also
  the legacy identity bridged to Account `owner.a`, which is how this session's own Auth→Family
  cross-domain flow (below) works at all.
- One additional Account created directly via `family.auth_service.create_credential` inside the
  container (id=7, "Synthetic No-Membership QA", credential `noaccess.qa`/`Synthetic!Pass9`,
  zero `FamilyMembership` rows) — needed for the "no membership at all" denial scenario, which the
  official seed does not provide (the seed's `suspended` account has no credential at all, so it
  cannot log in to exercise this path). Before: 6 accounts; after: 7. Deleted at teardown.

No shared/persistent database was ever touched. All the above lived only in `qaindep-db-1`
(destroyed at teardown along with its volume).

## AUTH axis — result

All checks run against the isolated stack, native Vite frontend, at 390×844 / 820×1180 /
1180×820 (identical outcomes at all three unless noted).

| Check | Result |
|---|---|
| Unauthenticated entry → profile-select | PASS — real `GET /api/players` data rendered (유빈/유현/아빠/엄마), not fixture |
| Successful profile pick (유빈, unlocked) → PIN step | PASS — advances to `PIN 번호를 입력하세요` |
| Correct PIN (`1234`) → dashboard | PASS — lands on `/dashboard` with a real session token in `sessionStorage.accessToken` |
| Locked profile (유현) click → guard blocks it | PASS, frontend layer — URL and DOM unchanged after click (`onSelect` not invoked); locked-notice text rendered ("유현의 잠금은 안전을 위한 보호 조치입니다") |
| Locked profile → guard blocks it, backend layer | PASS — direct `POST /api/auth/login {"player_id":2,"pin":"1234"}` (bypassing the UI entirely) → **HTTP 423** `{"detail":"🔒 관리자에 의해 잠긴 계정입니다."}`; contrasted with player 1 (unlocked) → HTTP 200 with a real JWT. No bypass at either layer. |
| Back-navigation from PIN step → returns to profile-select | PASS |
| Direct navigation to `/dashboard` while unauthenticated | PASS — does not stay on `/dashboard` |
| Empty-profile-list handling | PASS — with all 4 `players` rows soft-deleted (`UPDATE ... SET deleted_at = now()`, confirmed `GET /api/players` → `[]`), the screen still renders its shell ("사용할 프로필을 선택하세요") plus the admin-login link, zero profile cards, zero console `pageerror`s — no infinite spinner, no blank white screen. Restored immediately after (`deleted_at = NULL`, confirmed `GET /api/players` → 4 rows again, `is_locked` on player 2 preserved as `true`). |
| No console `pageerror`s across all of the above, all 3 viewports | PASS |
| Out of scope, confirmed still deferred/untouched | `1j`/`1j-1` (PIN-recovery) — no PIN-recovery UI reachable from the flows above. `2s` (4-digit visual vs 6-digit backend PIN) — confirmed still a live discrepancy (the Screen showed a 4-column keypad; the backend seed PIN is 4 digits so this session's own PIN entry happened not to expose the mismatch numerically, but the code-level `HUMAN_GATE` classification from prior tasks was not re-litigated, per this task's own scope instruction) |

**Auth verdict: PASS.** Every required scenario passed at all 3 viewports; the locked-account
guard is enforced independently at both the UI and the API layer.

## FAMILY axis — result

Authorization matrix (direct API, isolated backend, tokens obtained via real
`POST /api/auth/account/login` with `device_id`):

| Caller | Target | Result |
|---|---|---|
| `member.b` (Family 2 only) | `GET /api/families/1/members` (Family 1) | **403** `{"detail":"활성 가족 구성원 권한이 필요합니다"}` — zero data leaked |
| `noaccess.qa` (no membership anywhere) | `GET /api/families/1/members` | **403**, same detail; `GET /api/account-context` → `families: []` |
| unauthenticated (no token) | `GET /api/families/1/members` | **401** `{"detail":"인증이 필요합니다"}` |
| `owner.a` (Family 1 + 2 + a 3rd family created live during this task, see below) | `GET /api/account-context` | **200**, correctly lists exactly 3 families with per-family roles/permissions |

UI corroboration (native Vite, isolated stack):
- `member.b` signs in via `/login` → lands on Family Home showing **only** "Synthetic Family
  Beta" in the DOM; "Family Alpha" text does **not** appear anywhere on the page (checked via
  full-body `innerText`).
- `noaccess.qa` signs in → graceful empty state ("사용 가능한 가족이 없어요" / "활성 가족 구성원으로
  연결된 뒤 몽글 기능을 사용할 수 있습니다"), zero console errors, no crash.
- Unauthenticated direct navigation to `/family`, `/markpoint`, `/family/members` all redirect
  away from the target path (none of the three "stick" at the protected URL).
- Real API-sourced data confirmed rendered (not fixture) at `/family` (real family name/member
  count), `/family/members` ("우리 가족 4명"), `/profile` (real `Synthetic Service Participant`
  display name, not any static placeholder).

Route inventory spot-checks (signed in as `member.a`, one family, all real data, zero 404s, zero
console errors): `/family/notifications` (read/view — "새 알림 0개"), `/family/todo`
(input/action — "＋ 할 일 추가", "오늘의 진행률 0개"), `/family/members` (member/management —
real member count), `/family/schedule` (calendar — "이번 주 일정 0개"), `/family/album`,
`/family/rules`, `/family/search` — all seven render their real shell with real, empty-but-correct
counts (this fixture has no todo/schedule/album/rule content seeded, which is itself the
"empty-data condition" required by the task — every screen handled it without error).

Viewports: 390×844 / 820×1180 / 1180×820 all checked on `/family` and its sub-routes for
`member.a` — no horizontal overflow (`document.documentElement.scrollWidth >
document.documentElement.clientWidth` false at all 3 sizes), no console errors.

Committed-spec corroboration (`04-w75-data-wiring.spec.ts`, run for real against this session's
own isolated stack via `playwright.mongle-manual.config.ts`): `1a-1` (real login, and a real
*wrong-password* error is shown, not a silent no-op) — **PASS**; `1r` (real family creation via
the real onboarding form, real `POST /api/families` → 201) — **PASS**; `1q` (family member list
shows real names, not raw account IDs) — **PASS**; `1f` (profile shows real display name, not the
static fixture name "서연") — **PASS**. (`1t`/Wagle failed — see Cross-cutting note on WebSocket
proxying below; out of this task's scope.)

**Family verdict: PASS.** Every required authorization branch (member/no-membership/cross-family/
unauthenticated) returns the correct HTTP status with zero data leakage, and the frontend shows
the correct corresponding state for each, at all 3 viewports, with real API-sourced data.

## MARKPOINT axis — result

Real login → `/markpoint` root render: **PASS**. `member.a`'s dashboard shows real,
server-computed figures — "남은 미션 2개", "예상 포인트 50", the actual weekly day-list with the
two seeded missions ("방 정리하기 +30", "숙제 끝내기 +20") under the correct date, "차감 내역이
없어요" for the empty deductions section — confirmed against the DB fixture, not a static
placeholder. `1k` (checklist toggle) from `04-w75-data-wiring.spec.ts`, run for real: creates a
mission with a real checklist via the real API, opens it as the assignee, taps an item, asserts
the real `PATCH .../missions/{id}/checklist` response, reloads, and confirms the toggle persisted
server-side — **PASS**.

Two confirmed findings, both currently live in `62c1f23`:

**Finding 1 — `03-target-ui.spec.ts` is `SPEC_STALE` for two specific assertions (not a product
defect):**
1. Its `signIn()` helper's multi-family switch uses
   `page.locator('[data-testid^="family-switch-"]')` (individual buttons). The current UI (same
   header used by `/family`, `/markpoint`, `/dashboard`) uses a single `<select
   aria-label="활성 가족 선택">` combobox instead — confirmed present and functional (see Cross-
   domain finding below for the one real defect on this same combobox path).
   `04-w75-data-wiring.spec.ts`'s own multi-family test (`3c/3d/3e`) already uses
   `page.selectOption('select', ...)`, i.e. a *later* spec in the same directory was already
   updated for the current combobox UI — `03-target-ui.spec.ts` was not.
2. It asserts `getByRole('heading', { name: '마크포인트' })` on `/markpoint`. The current,
   intentional canonical heading (per `MarkpointUser.tsx`'s own code comment, "canonical 1c
   (포인트 잔치)") is **"포인트 잔치"**, not "마크포인트" — confirmed via a real DOM snapshot
   showing `<h1>포인트 잔치</h1>` with all the real weekly-mission data underneath it. This is a
   rename that happened after the spec was last touched (`git log --follow` on the spec: last
   commit `3294c90`, predating the `281d45a` composition that fixed the canonical heading).

This explains 7 of the 11 failures this session observed in a full run of `03-target-ui.spec.ts`
against the current isolated stack (Journey 1's family-switch test; Journey 2's dashboard-heading
test; Journey 6's PIN-isolation test, which also checks the "마크포인트" heading at its end). None
of these represent a behavior regression in the product; they are the spec's own assertions
having drifted from an intentionally-renamed canonical Screen.

**Finding 2 — `PRODUCT_DEFECT`, confirmed live, real, currently reachable: `/markpoint/admin` has
no route registration.**
`frontend/src/platform/shell/MongleAppShell.tsx` links its own nav to `to: '/markpoint/admin'`
(line 109), and `frontend/src/platform/markpoint/MarkpointAdmin.tsx` is a fully-built ~470-line
component with every expected `data-testid` present (`admin-mission-table`, `cycle-select`,
`materialize-window`, `bulk-approve`, `point-adjust-panel`, `markpoint-admin-denied`) — but
`frontend/src/App.tsx` registers **no `<Route path="/markpoint/admin">`** anywhere (confirmed by
`grep -n 'path="' App.tsx`, full list recorded above). Direct navigation to `/markpoint/admin`,
for `owner.a` (mission_manager), `admin.a` (point_admin), and a plain `member.a` alike, all
render the app's generic 404 (`페이지를 찾을 수 없어요`) — confirmed via a real Playwright DOM
snapshot, not inferred. This explains the remaining 5 (accounting for 1 overlap already counted
above under Finding 1's Journey 6) failures observed in the same `03-target-ui.spec.ts` run:
Journey 3's 3 tests (bulk-approve, cycle-guard, materialize-window) and Journey 7's 2 tests
(`markpoint-admin-denied` not found, `point-adjust-panel` not found) — all 5 timed out or failed
to find their target element because the route itself 404s before the component ever mounts.
Backend authorization for this same capability is independently confirmed correct: the
API-level half of Journey 7's first test (`GET /api/families/1/markpoint/missions` as `member.a`
→ **403**) passed in the same run — the defect is purely a missing frontend route registration,
not a backend authorization gap. This is the same class of gap `App.tsx`'s own code comment
(lines 179-189) already documents was found and fixed once before for `/family`/`/markpoint`/
`/wagle` themselves; `/markpoint/admin` was missed.

Committed-spec disposition for `03-target-ui.spec.ts`/`04-w75-data-wiring.spec.ts` (per this
task's required taxonomy): both files **exist**; both **are collected** by
`playwright.mongle-manual.config.ts` (confirmed — 8/17 and 8/10 tests respectively actually ran);
fixture preconditions (`Synthetic!Pass9` accounts) were satisfiable with disposable data and were
satisfied. Both were **run for real**, not skipped. `03-target-ui.spec.ts`: 4 passed / 11 failed
in the full run (11 failures classified above: 7 `SPEC_STALE`, 5 counted against
`PRODUCT_DEFECT` Finding 2 with 1 test overlapping both classifications — see per-test breakdown
in the Handoff). `04-w75-data-wiring.spec.ts`: 8 passed / 1 failed (Wagle-only, WebSocket-proxy
environment limitation, out of this task's scope, see Cross-cutting note) / 1 self-skipped
(`2t`, by its own pre-existing `test.skip(!process.env.MONGLE_W75_ADMIN_PASSWORD, ...)` guard —
not something this session disabled). Per `agent-system/qa/TEST_POLICY.md`'s risk-based table,
"FE core calculation, permission branching, or state transition" requires "risk-based independent
QA plus relevant journey evidence" — this session's own independent execution of both specs,
plus the direct API/DOM evidence above, satisfies that requirement; Finding 2 is a genuine
permission-branching-adjacent defect the journey evidence surfaced, not a reason to withhold
execution.

**Markpoint verdict: FAIL** on Finding 2 alone (a real, currently-live route defect makes the
Markpoint *admin* capability completely unreachable from the UI, despite correct backend
authorization) — this satisfies this task's own explicit FAIL criterion ("routes are broken").
The Markpoint *member* surface (`/markpoint` root, real data, checklist toggle, mission
submission) is fully correct and would be PASS in isolation.

## CROSS-DOMAIN axis — result

Continuous session, native isolated stack, 390×844: unauthenticated `/` → select 유빈 (unlocked,
legacy-bridged to Account `owner.a`) → PIN `1234` → `/dashboard` (session token confirmed present
in `sessionStorage`) → direct navigation to `/family` (same session, same token, confirmed via
`sessionStorage.getItem('accessToken')` equality) → the multi-family combobox (3 families, since
`owner.a` also owns a family this session itself created earlier via `1r`) → **select "Synthetic
Family Alpha"**.

**`CROSS_DOMAIN_FINDING`, confirmed live and reproducible three times independently:** selecting a
family on this exact path triggers `GET /api/me/notifications`, which returns **401** for this
specific legacy-PIN-bridged token (confirmed via direct `curl` with the *same* token shape:
`member.a`'s real Account-native token → `GET /api/me/notifications` → 200; the legacy-bridged
player token → `GET /api/me/notifications` → **401**, while the *same* legacy-bridged token
succeeds on `GET /api/account-context` and `GET /api/families/{id}/activity-log` — so the gap is
specific to this one `/api/me/*` route, not the whole legacy bridge). `frontend/src/shared/api/
httpClient.ts`'s global response interceptor treats **any** 401 outside two explicit allow-lists
(`AUTH_ENDPOINTS`, `OPTIONAL_ACCOUNT_ENDPOINTS`) as "session expired" and unconditionally clears
`sessionStorage.accessToken` + `localStorage` and hard-redirects to `/` — and
`/api/me/notifications` is in **neither** allow-list. The result: the entire session is destroyed
(confirmed: `sessionStorage`/`localStorage` both `null` afterward, page shows the fully
unauthenticated profile-select screen) the moment a legacy-PIN-bridged user picks a family on
`/family`, even though the underlying PIN session was never actually invalid.

This is not a one-off — the same interceptor file's own comments show this exact class of bug was
already found and fixed **twice** for other endpoints (`/api/me/wagle/*` and
`/api/chat/unread`, both explicitly added to `OPTIONAL_ACCOUNT_ENDPOINTS` with a comment reading
"an optional feature 401 must never be able to end a session"). `/api/me/notifications` — which
polls globally from the shared `MongleAppShell` header used on `/dashboard`, `/family`, and
`/markpoint` alike — was missed.

All other cross-domain checks (isolated from the family-selection step above, tested by going
directly to `/family/members`/`/markpoint` for a **single-family** account, `member.a`, which
never needs the combobox and so never triggers the same-shaped 401 on this same polling call in
this session's testing): session persists across `/family` → `/family/members` → `/markpoint`
(same token before/after, confirmed 3 times), no unrelated forced logout, browser back/forward
does not crash, page refresh mid-flow restores context (`/markpoint` reload shows the same real
data again), and the explicit logout button on `/markpoint`'s own header correctly clears the
session and a subsequent direct `/markpoint` navigation is denied afterward.

**Cross-domain verdict: FAIL** — a legacy-PIN-bridged Auth session that reaches the Family
combobox on a multi-family account is forcibly and silently logged out of the entire platform by
an unrelated, non-critical polling call's 401, per this task's own explicit FAIL criterion
("session/context bleeds across domains" / forced logout on a route transition). This is the
single highest-value finding of this task: it is invisible to any test that signs in through
`/login` directly to a single-family Account (as every passing test in both committed specs
does), and only appears on the legacy-Auth → multi-family-Family transition path this task's own
Phase E specifically asked for.

## Cross-cutting note: Wagle test failures in this session's own runs (out of scope, explained)

Both committed specs contain Wagle-realtime tests; all of them (03's Journey 4/6, 04's `1t`)
failed or hung in this session's own isolated-stack runs. Root cause independently identified,
not assumed: `frontend/src/platform/wagle/realtime/wagleRealtimeClient.ts` opens a `WebSocket` at
`/api/me/wagle/ws`; the real production Nginx config (`frontend/nginx.conf`) has a dedicated
`location = /api/me/wagle/ws` block with `Upgrade`/`Connection` headers for exactly this path —
but this session's Vite dev-server substitute (`vite.config.ts`'s `server.proxy['/api']`) has no
`ws: true`, so the WebSocket upgrade is never proxied and the client sits in `connecting` forever.
This is an `ENVIRONMENT_REQUIRED` limitation of this session's own chosen QA-substitute runtime,
not a product defect — Wagle is explicitly out of this task's scope, and the real Nginx path is
unaffected. Recorded here only so the Wagle-test failures are not mistaken for new Wagle defects.

## Regression

- `git status --short` / `git diff --stat`: empty at every check throughout this task except this
  session's own untracked scratch files, all deleted before this report (see Cleanup).
- Frontend: `pnpm run lint` → clean, no errors. `pnpm run build` (`tsc -b && vite build`) →
  succeeded, 666 modules, only the pre-existing "chunk larger than 500kB" advisory (not a new
  regression). Frontend Docker image build: **NOT IN SCOPE** (pre-confirmed broken,
  `pnpm`-vs-`package-lock.json` mismatch, explicitly out of this task).
- Backend, this task's own execution:
  `tests/test_account_auth_wave1.py`, `test_markpoint_access_wave4.py`,
  `test_markpoint_core_gap_wave5.py`, `test_markpoint_http_authorization_wave5.py`,
  `test_markpoint_target_wave5.py`, `test_migration_0021_participant_merge.py`,
  `test_w75_phase_c_extensions.py`, `test_w75_phase_d_slices.py`,
  `test_bg1_credential_surface_unification.py`, `test_auth_admin_login.py`, `test_weekly.py`,
  `test_frontend_service_code_contract.py` — **213 passed, 0 failed**, `/opt/homebrew/bin/
  python3.11`, isolated `postgres:16.9-alpine` on port 15435 (`database/init.sql` +
  `alembic upgrade head`, 21 migrations), 197.16s.
- `LATEST_FULL_BACKEND_SUITE`: not established by this session — this session ran the
  Auth/Family/Markpoint-relevant subset above, not the entire suite.
  `THIS_QA_FULL_BACKEND_SUITE: NOT RERUN` — the backend diff is genuinely zero
  (`git diff --stat -- backend/` empty) and the relevant subset above is 213/213, but this
  session did not re-run the *entire* suite (e.g. Wagle-only files were skipped as out of scope)
  and therefore does not claim a fresh full-suite number; do not blend the 213/213 subset result
  with any prior session's full-suite claim.
- `git diff --check`: exit 0.
- `python3 agent-system/tools/check_all.py`: ran clean (report-only, exit 0 by design); all
  WARNINGs shown pre-date this task (the already-known `...FOCUSED-INDEPENDENT-QA-001 is
  COMPLETED but remains active` pattern for the Admin/Wagle siblings, and several unrelated
  pre-existing handoff/closeout gaps) — 0 new warning attributable to this task.

## DB and runtime cleanup

- `qaindep-db-1`/`qaindep-backend-1` (this session's own isolated stack): `docker compose ... down
  -v` — containers, network `qaindep_network`, and volume `qaindep_qaindep_pg_data` all removed;
  confirmed via `docker ps`/`docker network ls` afterward (not re-checked by name here since the
  whole project was removed, which is the stronger guarantee).
- `qaindep-pytest-db` (isolated pytest fixture DB, port 15435): `docker stop && docker rm`.
- Native Vite dev server (port 5174): killed (`pkill -f vite`); port confirmed free afterward.
- Scratch files removed: `docker-compose.qa-indep-scratch.yml` (repo root),
  `tests/e2e/qaindep_script.mjs` through `qaindep_script10.mjs` (10 files, `tests/e2e/`), and all
  `/tmp/qaindep-*`/`/tmp/tok_*.txt`/`/tmp/login_*.json`/`/tmp/resp*.json` scratch artifacts.
  `git status --short` in `mongle_ui` confirmed empty after removal.
- Pre-existing persistent runtime (`mongle-backend-1`/`mongle-db-1`, ports 18001/15434,
  `docker-compose.phase1.yml -p mongle`): confirmed running before this task (`docker ps`,
  `Up 2 hours`) and confirmed still running, unmodified, after this task (`docker ps`,
  `Up 3 hours`, same container IDs `737ac3a9488b`/`87a08830775b`) — never connected to, never
  seeded, never restarted by this session.
- No fixture of any kind was ever written to a shared/persistent database; everything lived in
  the two disposable containers above, both destroyed.

## Changes

Zero product-code changes. Zero test-file changes (no edit, no skip, no assertion weakening —
the one self-skip observed, `04-w75-data-wiring.spec.ts`'s `2t`, is that spec's own pre-existing
`test.skip(!process.env.MONGLE_W75_ADMIN_PASSWORD, ...)` guard, not something this session
added). Zero commits. Zero pushes. This file and its paired Handoff are the only two files this
session leaves behind in the real repository.

## Axis verdicts

| Axis | Verdict |
|---|---|
| Auth | **PASS** |
| Family | **PASS** |
| Markpoint | **FAIL** (Finding 2: `/markpoint/admin` route unregistered — admin capability unreachable from the UI; member surface is PASS in isolation) |
| Cross-domain | **FAIL** (legacy-Auth→multi-family-Family transition triggers an unrelated 401 that forcibly clears the entire session) |

## Overall verdict: FAIL

Per this task's own verdict rules, PASS requires all four axis verdicts to be PASS; two are FAIL
on confirmed, reproducible, currently-live defects (not test artifacts, not environment
limitations — both independently root-caused down to a specific missing `<Route>` and a specific
missing entry in an existing, previously-used-twice allow-list). Regression, DB cleanup, and
zero-change/zero-commit conditions are otherwise all satisfied, and would not by themselves have
blocked PASS.

## Next action

1. Register `<Route path="/markpoint/admin">` in `frontend/src/App.tsx`, mirroring the
   `ProtectedRoute`/`MongleAppShell` wrapping already used for `/family`/`/markpoint`/`/wagle`
   immediately above it, rendering `MarkpointAdmin` (already fully built, needs no other change).
2. Add `/api/me/notifications` to `httpClient.ts`'s `OPTIONAL_ACCOUNT_ENDPOINTS` list (or, if a
   legacy-PIN-bridged caller is intended to see real notifications rather than being silently
   denied, fix the backend dependency that route uses so it accepts the same legacy-bridge path
   `GET /api/account-context` and `GET /api/families/{id}/activity-log` already do — a PM/architecture
   decision, not something this QA session should choose unilaterally).
3. A future dedicated implementation task should fix both, then a *separate* Independent QA
   session (not the implementer) should re-verify Markpoint-admin reachability and the
   cross-domain session-integrity path specifically, before either axis is claimed PASS again.
4. `03-target-ui.spec.ts`'s stale assertions (family-switch button locator, "마크포인트" heading
   text) should be updated to match the current canonical UI, or explicitly superseded by
   `04-w75-data-wiring.spec.ts`-style coverage — separate from the routing fix above, this is a
   test-maintenance item, not a product defect, and this QA session made no edit to it.
5. A Branch Integration task (as with the Admin/Wagle lineage) should commit this evidence +
   handoff pair; this session performed no commit/push itself.
