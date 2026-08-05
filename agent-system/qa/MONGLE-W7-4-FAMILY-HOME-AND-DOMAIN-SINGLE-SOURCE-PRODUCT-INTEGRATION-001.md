# QA Evidence — MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Role: Developer self-check (implementer). **Not** Independent QA.
- Full narrative, per-row Family classification table, and design reasoning:
  see this task's own handoff,
  `agent-system/handoffs/active/MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md`.
  This file records the concrete evidence only.

## Baseline

- Branch: `dev-newmarkp`
- HEAD at start: `97bc09ddf1bd3c3002b969f89c089bd3d423e04a` (unchanged
  throughout — same as the prior Auth task this session, no commit made by
  either)
- `accounts`/`family_groups` tables: 0 rows, confirmed by direct `psql`
  query before any seeding

## Static checks

| Check | Command | Result |
|---|---|---|
| Lint | `pnpm run lint` | PASS |
| Typecheck + build | `pnpm run build` (`tsc -b && vite build`) | PASS (2 real TS errors found and fixed during development, see handoff) |
| Diff whitespace | `git diff --check` | PASS |
| Diff scope | `git status --short` | Matches declared file list exactly |

## Database seeding/cleanup (additive-only, verified)

```
Seed 1 (Family Home manual verification):
CREATED account_id=1 family_group_id=1 membership_id=1

Seed 2 (9-route regression spot-check):
CREATED account_id=2 family_group_id=2 membership_id=2
```

Both removed via ID-scoped DELETEs (never blanket) in FK-safe order
(MembershipRoleAssignment → ServiceSubscription → AccountCredential →
AccountSession → FamilyMembership → FamilyGroup → Account). Final
independently re-queried counts, all tables:

```
accounts=0 families=0 sessions=0 memberships=0 creds=0 roles=0 subs=0
```

`git status --short backend/` confirmed clean before, during, and after —
no repository-tracked file was ever touched by either seed/cleanup pair
(both were disposable, un-committed `.local.py` scripts, deleted
immediately after each use).

## Runtime checks — Family Home (`1b`)

Login: real `/login` (Account-model), disposable seed account.

| Check | Result |
|---|---|
| `/family` renders canonical `1b` (`[data-canonical-screen-id="1b"]` count) | `1` |
| Greeting shows real account display name | `안녕하세요, QA 검증용 계정님!` |
| Activity zone, no real events for this fresh synthetic family | `아직 활동이 없어요.` (honest empty state, not fabricated) |
| Service tiles | `포인트 잔치`(highlighted, available), `가족 일정`/`앨범`/`할 일` (all available, no stale "준비중") |
| Real family name header still renders below | `QA 검증 가족` |
| Real feature-link count below (schedule/album/todo/members/notifications/rules/search) | `7` |
| Click markpoint tile → real navigation | `http://localhost:5174/markpoint` |
| Console/page errors | `0` |

### Responsive (same session)

| Viewport | Horizontal overflow | Tiles | Canonical `1b` |
|---|---|---|---|
| 390×844 | `false` | 4 | 1 |
| 820×1180 | `false` | 4 | 1 |
| 1180×820 | `false` | 4 | 1 |

### Detached Preview regression

`/__wave6/1b`: canonical `1b` marker count `1`, dock present (`[data-
visual-zone="dock"]` count `1`), greeting shows the fixture's own
`서연` (unaffected by the Product Adapter's real-data wiring), `0` page
errors.

## Runtime checks — Family sub-screen 9-route spot-check

Same login flow, second disposable seed account, one Markpoint + one Wagle
subscription granted (broader coverage than the first seed).

| Route | Canonical markers | Body text length | Errors |
|---|---|---|---|
| `/family/members` | 1 | 229 | 0 |
| `/family/schedule` | 1 | 298 | 0 |
| `/family/album` | 1 | 220 | 0 |
| `/family/todo` | 1 | 197 | 0 |
| `/family/rules` | 1 | 176 | 0 |
| `/family/notifications` | 1 | 102 | 0 |
| `/family/search` | 1 | 241 | 0 |
| `/profile` | 1 | 249 | 0 |
| `/onboarding` | 1 | 158 | 0 |

All 9 routes: exactly 1 canonical-Screen marker, non-trivial real body
text, 0 console/page errors.

## Source-level verification of the 16 deferred rows (current-code evidence)

Each deferred row's blocker was re-confirmed by direct source read this
task (not assumed from a prior task's prose alone):

- `2f`/`2p`/`3i`: `features/family-members/FamilyMembersPage.tsx`'s own
  `child-invite`/`invitations`/`cancel-invite` views all render only their
  respective static fixture (`childInviteFixture`/`invitationListFixture`/
  `familyInviteCancelFixture`) with no-op or navigate-only callbacks — no
  real create/resend/cancel API call anywhere in those branches.
- `2w`: `features/family-onboarding/OnboardingFlowPage.tsx`'s invite-
  acceptance branch renders only `familyInviteAcceptanceFixture`, no
  override.
- `2v`: `features/family-album/FamilyAlbumPage.tsx`'s own docblock comment
  explicitly states "2v (앨범 업로드 진행) staying fixture."
- `3a`: `features/family-schedule/FamilySchedulePage.tsx`'s own docblock
  comment explicitly states "3a's Google/Apple sync stays fixture."
- `3j`: `features/family-search/FamilySearchPage.tsx` spreads only
  `{...searchAllFixture, activeFilter}` — no real search query execution
  exists.
- `1i`/`1v`/`2z`: real GET-wired read/empty-state paths exist (confirmed by
  source read), but no real create/edit input-control path was found for
  any of the three — consistent with the already-disclosed W7.5 Phase D
  "missing input control" finding, re-confirmed not resolved.
- `1u`: unchanged from this session's own prior
  `MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001` finding
  (PIN 4-digit-Screen-vs-6-digit-backend mismatch).
- `3f`/`3g`/`3h`/`3k`/`3l`: unchanged, re-confirmed only, no new evidence
  this task beyond confirming the screens still import only their own
  static fixtures in `pages/profile/ProfilePage.tsx`.

**One correction found in the opposite direction**: `2y` was listed in a
W7.5 Phase D note among 6 screens with a missing-input-control gap.
`features/family-album/FamilyAlbumPage.tsx`'s own current docblock comment
explicitly states "1p/1w/2y real" — current code (the more recent evidence)
overrides the older note; `2y` is recorded `PRESERVE_AND_REGRESSION_TEST`,
not deferred, with the conflict disclosed in the handoff rather than
silently resolved either way.

## Known gaps (disclosed)

- Full per-view exhaustive functional testing (every filter, every nested
  overlay, every input control) was not performed across all 32 rows — only
  each route's own root-Screen render and the specific flows described
  above. This task's own actual code changes were limited to `1b` plus one
  shared-helper extraction; the other 31 rows' underlying implementation
  was not modified here, so exhaustive re-testing of unmodified code was
  judged disproportionate.
- The exact backend-side reasoning for `2v`'s storage-abstraction gap and
  `3a`'s calendar-sync gap was not independently re-audited from the
  backend code this task — only the frontend's own "still fixture" state
  was re-confirmed.
- No currently-locked seed account or multi-family account existed to
  exercise `1b`'s own no-active-family selector branch live — verified by
  diff that this branch's code is completely untouched (0 lines changed),
  not by live exercise.

## Final Declaration

- Verification: `DEVELOPER_SELF_CHECK_COMPLETE` / `INDEPENDENT_QA_PENDING`.
- Not a self-declared Independent QA PASS.
- No product/backend/migration/seed/RBAC change of any kind (the two
  disposable seed scripts were additive-only, never committed, and fully
  cleaned up with independently re-verified 0-row counts). No commit/push/
  merge/rebase performed.
