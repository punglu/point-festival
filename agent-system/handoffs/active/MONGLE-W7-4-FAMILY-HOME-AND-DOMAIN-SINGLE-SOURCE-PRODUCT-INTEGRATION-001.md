# MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Closeout Contract: v1
- Kind: Developer Agent implementation task — re-derive the Family domain's
  full canonical denominator from current code (not keyword search), give
  Family Home (`1b`) top priority, and single-source every implementation-
  ready Family screen into the real product. Same lineage as
  `MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`,
  `MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`, and this
  session's own `MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`.

## Environment (measured, this session, continuation of the Auth task above)

- WSL2, no Docker. Node v26.2.0 / pnpm 10.32.1. Python 3.12.3,
  `backend/.venv`, uvicorn 0.34.0, native PostgreSQL 16 (`mc_festival`).
- Runtime: the same `./dev.sh` stack already running from the prior Auth
  task this session (pid unchanged, not restarted) — backend `:8000`,
  frontend `:5174`.
- Branch `dev-newmarkp`, HEAD unchanged at `97bc09d…` throughout (no commit
  performed by this or the prior Auth task).
- `accounts`/`family_groups` and related tables were measured **empty (0
  rows)** in `mc_festival` at task start — confirmed by direct read-only
  `psql` query before any seeding.

## Family domain boundary (re-derived, not a keyword search)

Per this task's own instruction to classify by real code ownership (route/
import chain/render chain/context/API — not by scanning for "가족"), the
starting evidence was `find frontend/src/screens/family -maxdepth 1 -type
d`: **31 pre-existing** canonical Screen directories, each cross-checked
against the 64-row `MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
by its own `Canonical_Screen_ID`. Family Home (`1b`) had **no** such
directory — its own Preview (`FamilyHomePreview`) was a static `ui-only`
page never extracted into the `screens/*` pattern, the same shape the Auth
task found for `1j`/`1j-1`. Extracting it this task brings the total to
**32**.

**Excluded, `NOT_FAMILY_DOMAIN`** (confirmed by direct directory/file read,
not assumed): `1c`/`1k`/`1l`/`1s`/`2c`/`2h`/`2j` (Markpoint, `screens/
markpoint/*`); `1d`/`1t`/`2b`/`2g`/`3c`/`3d`/`3e` (Wagle, `screens/wagle/*`);
`1e`/`1m`/`2a`/`2e`/`2i`/`2l`/`2m`/`2o`/`2t`/`2x`/`3b` (Admin, `screens/
admin/*`); `1a`/`1a-1`/`1j`/`1j-1`/`2s` (Auth, `screens/auth/*` — this
session's own prior task); `1z` (cross-domain specimen, `NO_LIVE_CONSUMER_
REQUIRED`); `1x` (주간 리포트/weekly report — a static `ui-only` stub whose
entire content is Markpoint point/mission/level data, no `screens/family/*`
or `screens/markpoint/*` directory exists for it either way — genuinely
unbuilt, Markpoint-shaped, not Family).

**Family denominator: 32.**

## Family Home (`1b`) — top priority, per this task's own §6

`/family` is not a stub: `platform/pages/FamilyLanding.tsx` is a real,
carefully-reasoned page (its own docblock explains three deliberate
distinctions it refuses to blur: family-admin ≠ service-admin, an inactive
subscription must not offer an entry point that 403s, and losing one family
is not a logout). It handles two real states: no-active-family (a real
multi-family selector, necessary for any account in >1 family) and
family-selected (family name/role/admin badges, a family switcher when
>1 family, 2 real `ServiceCard`s for Markpoint/Wagle with real active/
inactive status, 7 real feature links, a real permission list).

The canonical `1b` Screen (frozen visual: profile greeting + hero Wagle CTA
+ "가족 최근 활동" activity feed + a 4-tile service grid, no multi-family
concept at all) covers a **different, narrower** slice than what the real
page does. Rather than force the whole real page into the frozen visual
(which would either fabricate a "coming soon" state for now-real features
or drop real multi-family/admin/permission functionality — both
prohibited), this task:

1. Extracted `screens/family/FamilyHome/FamilyHomeScreen.tsx` (zones 1-4
   only) from the previously-never-live-wired `FamilyHomePreview`, moving
   its two page-local avatar/bell image assets with it (`git mv`, history
   preserved). The bottom dock nav (Zone 5) stayed Preview-only — it is
   DEVICE_CHROME-equivalent (the real product route already renders
   `MongleAppShell`'s own nav in that position; duplicating it would be a
   second, dead nav bar), the same reasoning this file's own comments
   already applied to the OS status bar/home indicator.
2. Built `platform/pages/FamilyHomeContainer.tsx`, a Product Adapter that
   **composes** the canonical Screen at the top of `FamilyLanding`'s
   family-selected branch, with every pre-existing real section rendered
   unchanged immediately below it — additive, not a replacement.
3. Widened the canonical Screen's own service-tile contract
   (`highlighted`/`available` split instead of the frozen mockup's single
   binary `active`) so the 3 "가족 일정"/"앨범"/"할 일" tiles can correctly
   show as real/available (they are live product features today, unlike
   when the mockup was frozen) without losing "포인트 잔치"'s own
   highlighted/mascot-image treatment or its real subscription-driven
   availability badge.
4. Wired real data: greeting name from `useAuthStore().accountDisplayName`
   (already available, no new fetch); "가족 최근 활동" from the **existing**
   real `family_activity_log` API (already live at `2r`) — filtered to
   positive-shaped events only (the frozen visual has exactly 3 tone slots,
   star/level/gift, no red/neutral slot, and its own 3 example events were
   themselves all positive) rather than fabricating events; notification
   bell dot from a real `GET /api/me/notifications` unread check.
5. Extracted the activity-log→display-event mapping
   (`ACTION_LABEL`/`ACTION_TONE`/`toActivityEvent`, previously private to
   `FamilyMembersPage.tsx`'s own `2r` view) into `shared/family/
   activityLogFormat.ts` — a real second consumer (this task's own `1b`
   hero) now exists, meeting this task's own extraction bar. `FamilyMembers
   Page.tsx` re-verified byte-identical in behavior (same function bodies,
   just relocated), confirmed by diff.

**Disclosed, not silently accepted**: the hero's Wagle CTA has no disabled/
unavailable visual state at all in the frozen mockup, unlike the tile grid
(which does). If a family's Wagle subscription is inactive, the hero still
promotes it unconditionally — clicking through lands on the real `/wagle`
route, which itself already correctly shows its own unavailable state, so
nothing is functionally broken, but the Home screen itself doesn't warn
first. This is inherited from the frozen visual's own original design (no
disabled-hero-state was ever specified), not introduced by this task.

## Family sub-screens — full re-derivation, not reliance on stale reports

A grep across every real Family feature page (`features/family-*/`,
`pages/profile/ProfilePage.tsx`) for `screens/family/*` imports found **all
31 pre-existing canonical Screens already imported and rendered** by their
real product pages. This means `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001`
had already done the *structural* single-sourcing work across the whole
Family domain — this task's own contribution is (a) re-deriving that fact
from current code rather than trusting the claim, (b) `1b` itself (the one
genuinely missing extraction), and (c) sorting the other 31 into real-vs-
still-blocked with **fresh, current-code evidence**, since the original
W7.4 Matrix's own `Implementation_Readiness` column predates W7.5's later
work and is measurably stale for several rows.

**Method**: grepped every real feature page for `Fixture`/`fixture` usage
patterns to distinguish "renders live data" from "still spreads only the
static fixture, no override" — a page can legitimately import a canonical
Screen while a specific nested view inside it is still fixture-only. Two
concrete corrections found this way, in different directions:

- `2f`/`2p`/`3i` (자녀 초대/초대 목록/가족 초대 취소): the original W7.4
  Matrix marked these `READY_FOR_WIRING`. A later W7.5 Phase C note in
  `active.md` says they were reclassified `POLICY_BLOCKED` (Invitation type
  keyed on email, excluded by decision D2) together with `2w`. This task's
  own direct read of `FamilyMembersPage.tsx` **confirms the later note,
  not the Matrix**: `child-invite`/`invitations`/`cancel-invite` views all
  still render only their own static fixture with no-op callbacks. Deferred,
  not force-implemented.
- `2y` (사진 공유 설정): a W7.5 Phase D note lists it among 6 screens with a
  "recurring missing-input-control" gap (with `1i`/`1v`/`2z`/`3j`). This
  task's own direct read of `FamilyAlbumPage.tsx` found its own docblock
  comment explicitly states **"1p/1w/2y real"** — i.e. `2y` was
  subsequently fixed and the Phase D note is now stale for this one screen
  specifically. Per this task's own Gate 1/5 (current code over past
  reports), `2y` is recorded `PRESERVE_AND_REGRESSION_TEST`, with the
  conflicting older note disclosed, not hidden.

**Full per-screen table** (32 rows; see the Matrix CSV's own per-row
`Implementation_Evidence` column for the complete text):

| Action | Count | IDs |
|---|---|---|
| `IMPLEMENTED` (this task) | 1 | `1b` |
| `PRESERVE_AND_REGRESSION_TEST` (already real, unchanged) | 15 | `1f, 1g, 1h, 1n, 1o, 1p, 1q, 1r, 1w, 2k, 2n, 2q, 2r, 2u, 2y` |
| `DEFER_CONFIRMED_BLOCKER` (real, current-code-confirmed gap) | 16 | `1i, 1u, 1v, 2f, 2p, 2v, 2w, 2z, 3a, 3f, 3g, 3h, 3i, 3j, 3k, 3l` |

Sum: 1 + 15 + 16 = 32 = denominator. Every deferred row's own reason is a
**re-confirmation of already-existing evidence** (this task's own current-
code read, or a prior task's disclosed finding), never a newly-invented
policy/design opinion, and no PM/design/infrastructure decision was made by
this task.

## Files changed

- `frontend/src/screens/family/FamilyHome/**` (new): `types.ts`,
  `FamilyHomeScreen.tsx`, `FamilyHomeScreen.module.css` (zones 1-4, moved
  verbatim from the original `FamilyHomePreview.module.css`, dock block
  removed), `familyHome.fixture.ts`, `index.ts`, `assets/{a2-profile-
  avatar.png,a2-notification-bell.png}` (`git mv`'d from `pages/
  FamilyHomePreview/assets/`, history preserved).
- `frontend/src/platform/pages/FamilyHomeContainer.tsx` (new) — the Product
  Adapter described above.
- `frontend/src/platform/pages/FamilyLanding.tsx` — 3 lines added (import +
  one `<FamilyHomeContainer .../>` mount), nothing else touched.
- `frontend/src/pages/FamilyHomePreview/{index.tsx,FamilyHomePreview.module.css}`
  — rewritten to consume the extracted Screen + its own fixture, keeping
  only the preview-local dock.
- `frontend/src/shared/family/activityLogFormat.ts` (new) — extracted
  shared helper, described above.
- `frontend/src/features/family-members/FamilyMembersPage.tsx` — the same
  helper's local definition removed and replaced with the shared import;
  0 behavior change (same function bodies).
- `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
  — additive columns for the 32 Family rows only, chained after the
  existing Wagle/Admin/Auth columns for other rows, not overwriting them.
- `agent-system/qa/COVERAGE_MAP.md` — one new row,
  `FE-W7-4-FAMILY-HOME-SINGLE-SOURCE-001`.
- `agent-system/active.md`, `agent-system/relay/current.md` — this task's
  own entries.
- This handoff and its QA evidence file.

## Database — additive-only, fully cleaned up

`mc_festival`'s `accounts`/`family_groups`/related tables were measured
empty (0 rows) at task start. Rather than run the repository's own existing
`backend/scripts/phase1_seed_synthetic.py` (whose own docstring says
"isolated database only" and which performs a **blanket** `DELETE` across
`Account`/`FamilyGroup`/`WagleRoom`/`MarkpointMission`/etc. — unsafe against
this persistent dev DB regardless of those specific tables being empty
right now), this task wrote two small, disposable, **INSERT-only** scripts
(never committed, deleted immediately after use) that created exactly one
synthetic Account + FamilyGroup + FamilyMembership + owner role + Markpoint/
Wagle subscription + credential each time, for real-login verification.
Both were fully removed afterward via ID-scoped (never blanket) `DELETE`s
in FK-safe order, independently re-verified via direct `psql` row counts:
`accounts`/`family_groups`/`account_sessions`/`family_memberships`/
`account_credentials`/`membership_role_assignments`/`service_subscriptions`
all confirmed **0** after cleanup — the exact state found at task start.
`git status --short backend/` confirmed clean throughout.

## Validation

- `pnpm run lint` — clean.
- `pnpm run build` (`tsc -b && vite build`) — clean, two real TypeScript
  errors caught and fixed during development (a stale type import left
  over from the shared-helper extraction; a `const`-assertion-on-ternary
  TS1355 in the new Container, fixed with an explicit type annotation
  instead).
- `git diff --check` — clean.
- `git status --short` — matches the file list above exactly.

## Runtime verification (executed)

Against the same native `./dev.sh` stack as the prior Auth task:

- Real login (disposable synthetic account) → `/family`: canonical `1b`
  renders with real account name, real empty-state activity feed (honestly
  empty — this synthetic family had no Markpoint audit events, not
  fabricated), all 4 service tiles correctly showing schedule/album/todo as
  available (not the frozen mockup's stale "준비중"); clicking the
  markpoint tile navigated to the real `/markpoint`; every pre-existing
  real section (family name header, admin badge, 7 feature links,
  permission list) rendered unchanged below it; 0 console/page errors.
- 3-viewport check (390×844/820×1180/1180×820): 0 horizontal overflow at
  any size.
- `/__wave6/1b` (Preview) independently re-checked: still renders via the
  same canonical Screen + its own fixture, dock present and unaffected.
- 9-route regression spot-check (`/family/members`, `/family/schedule`,
  `/family/album`, `/family/todo`, `/family/rules`, `/family/
  notifications`, `/family/search`, `/profile`, `/onboarding`): exactly 1
  canonical-Screen marker (`[data-canonical-screen-id]`) and 0 console/page
  errors on every single route.

Not executed: a full per-screen functional regression of all 32 rows
(e.g. actually exercising every input control, every filter, every nested
overlay). The 9-route spot-check confirms each route's own root Screen
renders cleanly with real data and no runtime error; it does not exhaustively
exercise every nested view/overlay inside each page (e.g. `2r`'s own filter
buttons, `1w`'s search query). Flagged as a disclosed scope limit, not
silently skipped — full per-view exhaustive testing of 32 rows was judged
disproportionate for this task's own actual code changes (which touched
exactly `1b` plus one shared-helper extraction; the other 31 rows were
already-shipped code by a prior task, not modified here).

## Independent QA

Not performed by this task (implementer does not self-award QA PASS, per
`agent-system/rules.md` Invariant 6).

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md

The four fields above are the documentation-synchronization obligations
only. This is narrower than a Lifecycle of `COMPLETED`, PM approval,
graduation, or a later independent verification pass's own separate
verdict — see `Verification` in `active.md`'s own entry for this task,
deliberately left at `DEVELOPER_SELF_CHECK_COMPLETE`/`INDEPENDENT_QA_
PENDING`, not `PASS`.

## Unverified / estimated values (explicit)

- No value above is presented as measured without having actually been
  measured this session. The one disclosed non-exhaustive item: the 16
  deferred rows' own blocker reasons are **re-confirmations** of prior
  tasks' findings (cited by task ID) plus this task's own fresh source
  reads, not independently re-derived from first principles for every one
  of the 16 (e.g. the exact backend reasoning behind `2v`'s storage-
  abstraction gap was not re-audited from the backend code itself this
  task — only the frontend's own "still fixture" state was re-confirmed).

## Next Action

Awaiting PM review and a focused Independent QA pass. The 16 deferred Family
rows require the same already-open PM/design/infrastructure decisions prior
tasks surfaced (invitation-model policy for `2f`/`2p`/`2w`/`3i`; missing
input controls for `1i`/`1v`/`2z`/`3j`; storage/calendar-sync infrastructure
for `2v`/`3a`; account-deletion policy for `3h`; settings-policy decisions
for `3f`/`3g`/`3k`/`3l`; the PIN-digit mismatch for `1u`, shared with the
Auth task) — no new decision item is introduced by this task. Markpoint
domain and W7.6 remain out of this task's scope, untouched. No backend/
migration/RBAC change of any kind. No commit/push/merge/rebase performed.
