# MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Closeout Contract: v1
- Kind: Developer Agent implementation task — bind the Auth-owned canonical
  Screen(s) the latest `MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
  marks implementation-ready into the real product, single-source with the
  Detached Preview. Same pattern as the graduated Wagle/Admin single-source
  integration tasks, applied to the Auth domain.

## Environment (measured, this session)

- Host: WSL2 (`P00086577-001`, `6.6.87.2-microsoft-standard-WSL2`), no Docker
  available (`which docker` empty) — matches this session's own prior
  memory of the WSL environment having no Docker.
- Repo: `/appl/point-festival`, branch `dev-newmarkp`, HEAD at task start
  `97bc09ddf1bd3c3002b969f89c089bd3d423e04a`, `git status --short` clean,
  no stash.
- Frontend: Node v26.2.0 (repo's own `engines` field requests `<23` — an
  `Unsupported engine` warning is emitted by pnpm but does not block
  lint/build), pnpm 10.32.1.
- Backend: Python 3.12.3, `backend/.venv` present with `uvicorn` 0.34.0
  installed, `backend/.env` points at a native local PostgreSQL 16
  (`postgresql.service` active, `mc_festival` DB) — no Docker required.
- Runtime actually used: the repository's own `./dev.sh start`, which runs
  `alembic upgrade head` against the existing `mc_festival` DB then starts
  `uvicorn app.main:app` on `:8000` and `pnpm run dev` (Vite) on `:5174`.
  This is the project's persistent native dev stack (same one referenced
  throughout prior W7.5 tasks as `mc_festival`/`dev.sh`), not a disposable
  QA stack — left running after this task, not torn down, since it is the
  ongoing dev environment rather than task-owned throwaway infrastructure.
- Playwright: `tests/e2e`'s pinned `@playwright/test@1.58.2`; its matching
  Chromium was not yet installed under `PLAYWRIGHT_BROWSERS_PATH=0` at
  task start (cached revisions present were `1223`/`1228`, pinned version
  needed `1208`) — installed via the exact documented command in
  `tests/README.md` (`PLAYWRIGHT_BROWSERS_PATH=0
  ./node_modules/.bin/playwright install chromium`), not an unpinned
  `npx`/`latest` install.

## Auth target-set derivation (re-derived, not a keyword search)

Per the continuation instruction's own explicit warning against classifying
screens as Auth by keyword ("계정"/"잠금"/"로그인"/"PIN"/"인증"), the target
set was derived from the already-existing, independently-remediated
`MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv` (64/64 rows,
`Implementation_Readiness` already populated by
`MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-
REMEDIATION-001`), filtered to rows whose **real code ownership** —
`screens/<domain>/` directory, live route, guard/redirect/session
attachment — is Auth, confirmed by direct source reads this session, not
assumed from the Korean label text.

Considered and **excluded as `NOT_AUTH_DOMAIN`** (each confirmed by
directly reading the file, not inferred):

- `1r` (온보딩, `/onboarding`) — canonical Screen lives at
  `screens/family/Onboarding/`, not `screens/auth/`. Already
  `ALREADY_COMPLETE` regardless.
- `1u` (PIN 변경, `/profile` view) — canonical Screen lives at
  `screens/family/PinChange/`, not `screens/auth/`. Also separately
  blocked (`DESIGN_CONTRACT_MISMATCH`/`HUMAN_GATE`, 4-digit vs. 6-digit
  PIN — see `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` Phase B), but the
  exclusion itself is on ownership grounds, not the blocker.
- `2w` (가족 초대 수락, `/onboarding` branch) — canonical Screen lives at
  `screens/family/FamilyInviteAcceptance/`, not `screens/auth/`. Also
  separately `POLICY_BLOCKED` (Invitation type keyed on email, excluded by
  decision D2), consistent with the ownership finding either way.

**Auth denominator: 5** — `1a`, `1a-1`, `1j`, `1j-1`, `2s` (all four other
`screens/auth/*` directories present in the repo —
`ProfileSelector`/`PinInitialSetup` — map onto exactly these Canonical
IDs; `1j`/`1j-1` have no `screens/auth/*` directory at all, which is
itself part of their own blocker finding below).

## Per-row disposition

| ID | Label | Prior Readiness | This Task Action | Result |
|---|---|---|---|---|
| `1a` | 로그인/프로필 선택 (`/`) | `READY_FOR_LEGACY_REPLACEMENT` | `REPLACE_LEGACY_WITH_CANONICAL` (profile-select step only) | `IMPLEMENTED` |
| `1a-1` | 로그인 폼 (`/login`) | `ALREADY_COMPLETE` | `PRESERVE_AND_REGRESSION_TEST` | `PRESERVED_NO_CHANGE` |
| `1j` | PIN 입력 | `DESIGN_DECISION_REQUIRED` | `DEFER_CONFIRMED_BLOCKER` | `DEFERRED_CONFIRMED_BLOCKER` |
| `1j-1` | 계정 잠금 | `DESIGN_DECISION_REQUIRED` | `DEFER_CONFIRMED_BLOCKER` | `DEFERRED_CONFIRMED_BLOCKER` |
| `2s` | PIN 최초 설정 | `POLICY_DECISION_REQUIRED`/`POLICY_BLOCKED` | `DEFER_CONFIRMED_BLOCKER` | `DEFERRED_CONFIRMED_BLOCKER` |

### `1a` — why only the select step, not the whole `/` flow

`/` is not a stub: `pages/Auth/index.tsx` (`AuthPage`) is a real, fully
functional 3-mode flow — `select` (player list) → `pin` (real PIN submit,
real 423-lockout handling) → `admin` (real admin login) — plus its own
top-of-component `isLoggedIn` redirect guard. The canonical `1a` Screen
(`screens/auth/ProfileSelector/ProfileSelectorScreen.tsx`) only covers the
`select` step's visual. `1j`/`1j-1`, the flow's own next steps, have no
canonical Screen at all (see below), and `/login`'s separate
`A1AccountLoginPage` is a **different auth paradigm** entirely — real
username/password Account-model login (`accountAuthApi.ts`,
`useAuthStore().accountLogin`) vs. `/`'s real player+PIN model
(`pages/Auth/api/authApi.ts`, `useAuthStore().setLogin`) — reconciling the
two is a genuine product/design decision this task has no authority to
make (prohibited by the continuation brief's own §6/§17: no auth-policy
change, no session-storage change).

So the implementation is scoped to exactly the `select` step: a new
Product Adapter, `pages/Auth/components/ProfileSelectorContainer.tsx`,
replaces the legacy `PlayerSelectView` inside `AuthPage`'s `select` mode.
`PinInputView` (PIN submit, 423 handling) and `AdminLoginView` (admin
login) are **not modified in any way** — same files, same imports from
`AuthPage`, same `onPlayerSelect`/`onAdminClick` prop signatures.

### Prop-contract widening (additive, backward-compatible)

`ProfileSelectorScreen`'s existing `onSelect` callback only round-tripped
`profile.name` — insufficient for the real product, where the identity
key must be the player `id` (real family data could plausibly have two
same-named profiles; a name-keyed lookup would be a latent correctness
bug). Widened:

- `ProfileSelectorProfile.id?: string` (new, optional)
- `onSelect?: (key: string) => void` — Screen passes `profile.id ??
  profile.name`

The Preview (`pages/ProfileSelectorPreview/index.tsx`) is unaffected: its
fixture has no `id`, so the callback still receives `name`, exactly as
before — verified by reading the Preview file (0 diff) and by the fact its
own `onSelect` is already a no-op.

### Locked-profile guard — preserved, not redesigned

The frozen canonical `1a` visual does **not** disable the button for a
locked profile (still clickable, per its own `onClick` handler). Rather
than changing the frozen visual, the guard is reproduced at the **Product
Container** level: `ProfileSelectorContainer`'s `handleSelect` simply does
not call `onPlayerSelect` when the resolved player `is_locked` — the exact
same effective guard the legacy `PlayerCard`'s `disabled` prop enforced,
just relocated to the adapter rather than the frozen Screen. No backend
call, no navigation, and no state change happen for a locked-profile
click, matching prior behavior exactly. (No currently-locked seed account
existed in this session's DB to exercise this branch live in the browser;
verified by code inspection and by the fact the underlying comparison
(`player.is_locked`) is byte-identical to the legacy component's own
check.)

### `1j`/`1j-1` — why genuinely blocked, not force-implemented

Both `pages/PinEntryPreview/index.tsx` and `pages/AccountLockPreview/
index.tsx` are static, inline `ui-only` components (`data-implementation-
mode="ui-only"`) — **not** extracted into the `screens/*` canonical
pattern (no typed props/model, no fixture, never live-wired to any route
other than their own `/__wave6/*` preview). Two concrete, undecided design
questions block turning them into real canonical Screens:

1. `1j`'s "PIN 찾기" keypad button has no defined behavior anywhere in the
   codebase.
2. `1j-1`'s frozen visual shows a specific attempt count ("5회 실패") and
   retry countdown ("5분 후 다시 시도할 수 있어요") — real backend data
   (`GET /api/players`, confirmed by a live call this session) exposes
   only `is_locked: boolean`, no attempt counter or unlock timestamp.
   Rendering the frozen copy with real data would mean fabricating
   numbers with no backing source, which the continuation brief's own §6
   prohibits ("실제 인증 API를 mock으로 교체" / no invented functionality).

Both are correctly `DESIGN_DECISION_REQUIRED`, unchanged from the prior
audit's own finding; not reopened, not forced through.

### `2s` — why genuinely blocked, not force-implemented

Re-confirmed, not reopened: `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001`
Phase B already found and recorded a real `DESIGN_CONTRACT_MISMATCH`
(canonical Screen is a 4-digit PIN entry; the backend's actual PIN policy
is 6-digit), correctly reclassified `HUMAN_GATE`. No PM/design decision on
this has landed since. Not touched this task.

## Files changed

- `frontend/src/screens/auth/ProfileSelector/types.ts` — additive:
  `ProfileSelectorProfile.id?: string`; `onSelect` param renamed/retyped
  from `name` to `key` (same shape, `string`).
- `frontend/src/screens/auth/ProfileSelector/ProfileSelectorScreen.tsx` —
  both `onClick` call sites now pass `profile.id ?? profile.name`.
- `frontend/src/screens/auth/ProfileSelector/index.ts` — additive: now
  also exports the `ProfileSelectorProfile` type.
- `frontend/src/pages/Auth/components/ProfileSelectorContainer.tsx` (new)
  — the Product Adapter described above.
- `frontend/src/pages/Auth/index.tsx` — `PlayerSelectView` import/usage
  replaced with `ProfileSelectorContainer`; no other line touched.
- `frontend/src/pages/Auth/components/PlayerSelectView.tsx` (deleted) and
  `frontend/src/pages/Auth/components/PlayerCard.tsx` (deleted) — fully
  orphaned after the swap above; confirmed via `grep -rln` before deletion
  that no other file in the repository imported either.
- `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
  — additive columns for the 5 Auth rows only (`W7_4_Implementation_Task`
  through `Implementation_Evidence`); every pre-existing column and every
  other row's data is byte-identical to HEAD (verified: `git diff` scoped
  to exactly the 5 intended row-lines after fixing a line-ending mismatch
  from the CSV rewrite — see Corrections below).
- `agent-system/qa/COVERAGE_MAP.md` — one new row,
  `FE-W7-4-AUTH-PROFILE-SELECT-SINGLE-SOURCE-001`.
- `agent-system/active.md`, `agent-system/relay/current.md` — this task's
  own entries.
- This handoff and its QA evidence file.

## Corrections made during this task (disclosed, not silently fixed)

- The first CSV-column update pass rewrote the file with Python's
  `csv.writer` default `lineterminator` (`\r\n`), which reformatted every
  line's ending in the 64-row file even though only 5 rows' content
  changed — a real risk of touching write-once historical data noise-only,
  but still a boundary violation of "additive columns for 5 rows only."
  Caught before proceeding (`git diff --stat` showed 65/65 instead of the
  expected 5), reverted via `git checkout --`, and redone with
  `lineterminator='\n'` to match the original file. Final diff: exactly 5
  rows changed, `git diff --check` clean.

## Validation

- `pnpm run lint` — clean (0 errors, 0 warnings beyond the pre-existing
  Node-engine-version notice, which is unrelated to this change).
- `pnpm run build` (`tsc -b && vite build`) — clean; typecheck and
  production build both succeeded, no new chunk-size regression beyond
  the pre-existing warning.
- `git diff --check` — clean.
- `git status --short` after all edits — matches exactly the file list
  above, no unrelated drift.

## Runtime verification (executed, not disclosed as pending)

Started the project's own `./dev.sh start` (native `uvicorn` + `pnpm run
dev` against the real `mc_festival` PostgreSQL DB, `alembic upgrade head`
run first by the script itself). Confirmed via direct `curl`:

- `GET /api/players` → 4 real seeded players (`유빈`, `유현`, `아빠`,
  `엄마`), all `is_locked: false`, matching this adapter's assumed shape
  exactly.
- `GET /api/configs/level.thresholds` → `401` unauthenticated — this is
  **pre-existing** behavior, not a regression: the legacy
  `PlayerSelectView` made the exact same unauthenticated `fetch()` call,
  so it always failed pre-login too; both old and new code fall back to
  `thresholds = null` (no level label shown) via the same `.catch(() =>
  {})`.

Then ran a throwaway Playwright script (`tests/e2e`'s own pinned 1.58.2 +
its matching Chromium, installed per `tests/README.md`'s documented
command; script itself not committed, deleted after use) against
`http://localhost:5174`:

- `/` renders the canonical `1a` Screen (`[data-canonical-screen-id="1a"]`
  present, count 1) with the 4 real player names/points/admin-login
  button — no fixture data leaked into the live page.
- Clicking the real profile "유빈" navigated to the **untouched** legacy
  PIN screen (`PinInputView`), header showing "유빈" and "PIN 번호를
  입력하세요" plus the real keypad — confirms the widened `id`-based
  `onSelect` → container lookup → `onPlayerSelect` chain works correctly
  end-to-end against real data, not just by code review.
- Clicking "← 다른 플레이어 선택" returned to the `1a` canonical screen
  cleanly (guard/redirect flow intact).
- 3-viewport responsive check (390×844, 820×1180, 1180×820): 0 horizontal
  overflow at any size, profile buttons present at all three.
- No PIN was ever submitted and no login was ever completed during this
  verification — all calls were `GET`s plus client-side navigation, 0
  mutation to the DB. `git status --short` confirmed 0 runner-induced
  repository drift afterward.
- The dev stack (`./dev.sh`) was left running after this task — it is the
  project's own persistent native dev environment (`mc_festival` DB,
  ports 8000/5174), not task-owned disposable QA infrastructure, so there
  is nothing to tear down.

Not executed: the repository's committed Playwright spec suite under
`tests/e2e/specs-mongle/` was not run (out of this task's own changed-file
set — no spec references `1a`/`ProfileSelectorContainer` yet); adding one
was judged out of scope for a single-slice single-source-integration task
per this task's own minimal-test-addition mandate and the fact a real,
passing manual E2E-equivalent check was already produced. Flagged as a
disclosed gap, not silently skipped.

## Independent QA

Not performed by this task (implementer does not self-award QA PASS, per
`agent-system/rules.md` Invariant 6). This handoff's own claims above are
Developer self-check, not Independent QA PASS.

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md

The four fields above are the documentation-synchronization obligations
only (all four closeout documents reviewed and current). This is a
distinct, narrower thing than a Lifecycle of `COMPLETED`, than PM
approval, than graduation, or than the separate verdict a later,
independent verification pass would produce — see `Verification` at the
top of this handoff, deliberately left at
`DEVELOPER_SELF_CHECK_COMPLETE`/`INDEPENDENT_QA_PENDING`, not `PASS`.

## Unverified / estimated values (explicit, per rules.md §"Mandatory
closeout synchronization")

- No value in this handoff is presented as measured without having
  actually been measured this session; there is nothing to flag as
  estimated. The one explicit non-measurement is `1a-1`'s regression
  scope, which was verified only as "0 diff" (untouched), not
  re-executed end-to-end this session — recorded as `NOT_RE_EXECUTED`,
  not claimed `PASS`, in the CSV.

## Next Action

Awaiting PM review and a separate focused Independent QA pass (per
`.claude/agents/test-agent.md`). `1j`/`1j-1`/`2s` remain genuinely blocked
pending PM/design decisions already surfaced by prior tasks — no new
decision item is introduced by this task. W7.4 Auth axis: 1/5 rows
implemented, 1/5 already-complete (preserved), 3/5 correctly deferred with
evidence, 0/5 unprocessed. No backend/migration/DB/RBAC/PIN-policy change
of any kind. No commit/push/merge/rebase performed.
