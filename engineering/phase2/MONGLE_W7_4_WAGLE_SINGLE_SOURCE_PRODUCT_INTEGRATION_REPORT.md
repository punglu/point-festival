# MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001 — Implementation Report

```text
Verdict: CONDITIONAL
```

`CONDITIONAL` because the code-level implementation, single-source wiring,
and static validation (lint/typecheck/build) all passed cleanly with the
full implementation-ready Wagle target set (1/1) implemented, but no
browser/E2E runtime was available in this session to independently confirm
behavior at runtime (no local `backend/.venv`, no local PostgreSQL — see
Section 8). This is a disclosed measurement gap, not a code-level blocker.

## 1. Baseline

```text
Worktree: /Users/mac/mac_Project/mongle_ui
Branch:   dev-newmarkp
HEAD (start): 0319940ad452105ed512029b8260b5159d2a4815 (unchanged through this task)
Existing dirty at start: none (git status --short was empty)
Task-owned changes: see Section 7 (file list)
Commit/push/merge/rebase: none performed
```

## 2. Scope Clarification (mid-task correction, resolved)

Partway through implementation, a "SCOPE CORRECTION" instruction arrived
claiming `mongle_ui` and `minecraft_points_festivals` share one `.git` as
linked worktrees, that `frontend/src/platform/**` was PM-unapproved
"Doran" draft work, and that this Task must freeze exactly the files it
needed to modify (`WagleRoomView.tsx`, `WagleLanding.tsx`,
`MongleAppShell.tsx`).

Before acting on it, each claim was independently checked against the live
repository rather than accepted on the instruction's own authority:

```text
mongle_ui/.git and minecraft_points_festivals/.git: both real, independent
  directories (not worktree-link files) — separate clones of the same
  GitHub remote (origin = punglu/point-festival.git), not a shared worktree
`git worktree list` run from mongle_ui: does not list minecraft_points_
  festivals at all (only itself + one unrelated stale scratchpad worktree)
`find . -iname "*DoranLanding*"` in mongle_ui: 0 results
`find frontend/frontend`: does not exist
`git diff --name-only -- backend/app/domains/family`: empty, untouched
```

The claim's premise did not hold. This was reported back before any file
under `frontend/src/platform/**` had been touched (the only changes at that
point were the new `screens/wagle/FamilyChat/` directory and the
`FamilyChatPreview` page rewrite). PM confirmed the correction was itself
based on a different repository's state (`minecraft_points_festivals`,
`dev` branch) misapplied to this session, and cancelled it in full. No
rollback was necessary because no protected-path edit had occurred. Work
resumed at the original Task scope with no loss.

## 3. Authority Readback

```text
Matrix:  engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv
Report:  engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_REPORT.md
QA/handoff: MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001 and its
  CONDITIONAL-CLOSEOUT-REMEDIATION-001 companion, both read in full
```

Wagle target derivation method: grepped the Matrix CSV case-insensitively
for `wagle` across every column (not just `Screen_Label`), to avoid missing
a row whose Wagle ownership only shows up in `Canonical_Source` /
`Actual_Product_Consumer` text. This surfaced **7** rows, not the 6-row
candidate list (`1t, 2b, 2g, 3c, 3d, 3e`) carried over from prior sessions
— that list omitted `1d` (가족 대화 / `WagleLanding`), the actual `/wagle`
route root. The stale 6-count is exactly the discrepancy this Task's own
Section 3.2 warned not to reuse.

## 4. Wagle Target Set

| ID | Screen | Canonical Source | Product Consumer | Implementation Readiness (write-once, preserved) | This Task Action |
| --- | --- | --- | --- | --- | --- |
| `1d` | 가족 대화 | `FamilyChatPreview` | `WagleLanding` → `WagleRoomView` (`/wagle`) | `READY_FOR_LEGACY_REPLACEMENT` | **REPLACE_LEGACY_WITH_CANONICAL / MERGE_CANONICAL_INTO_EXISTING_CONTAINER** |
| `1t` | 와글 대화방 멤버 목록 | `ChatSettingsPreview` | `WagleRoomView` settings overlay | `ALREADY_COMPLETE` | `PRESERVE_AND_REGRESSION_TEST` |
| `2b` | 파일 뷰어(와글 첨부) | `FileViewerPreview` | none (storage infra absent) | `INFRASTRUCTURE_PREREQUISITE_REQUIRED` | `DEFER_CONFIRMED_BLOCKER` |
| `2g` | 채팅 답장 | `ChatReplyPreview` | `WagleRoomView` reply overlay | `ALREADY_COMPLETE` | `PRESERVE_AND_REGRESSION_TEST` |
| `3c` | 가족 게시판 | `FamilyBoardPreview` | `WagleBoardPage` (`/wagle/board`) | `DESIGN_DECISION_REQUIRED` (reaction-toggle click target) | `DEFER_CONFIRMED_BLOCKER` |
| `3d` | 댓글 작성 | `CommentComposerPreview` | `WagleBoardPage` | `ALREADY_COMPLETE` | `PRESERVE_AND_REGRESSION_TEST` (no file touched — out of implementation scope, already complete) |
| `3e` | 인기 게시글 | `PopularPostsPreview` | `WagleBoardPage` | `DESIGN_DECISION_REQUIRED` (shared reaction-toggle gap) | `DEFER_CONFIRMED_BLOCKER` |

```text
Total Wagle canonical screens:            7
ALREADY_COMPLETE (pre-existing):          3 (1t, 2g, 3d)
READY_FOR_LEGACY_REPLACEMENT:             1 (1d)
Decision blocked (DESIGN_DECISION_REQUIRED): 2 (3c, 3e)
Infrastructure blocked:                   1 (2b)
This Task implemented count:              1 (1d)
Deferred count:                           3 (2b, 3c, 3e — all pre-existing,
                                            genuine blockers, none newly
                                            created by this Task)
```

`1d` was the only screen in `READY_FOR_LEGACY_REPLACEMENT` /
`READY_FOR_PARTIAL_INTEGRATION_COMPLETION` / `READY_FOR_WIRING` state — the
implementation set this Task's own charter defines as in-scope. It was
implemented. Nothing implementation-ready was left unprocessed.

## 5. Implemented Screen — `1d` (가족 대화)

```text
Previous consumer:  WagleLanding -> WagleRoomView, ad hoc JSX (no shared
                     canonical Screen; FamilyChatPreview held its own
                     duplicate, hardcoded-fixture, prop-less markup)
Final consumer:      WagleLanding -> WagleRoomView -> FamilyChatScreen
                     (canonical, props-driven), same component
                     FamilyChatPreview now renders
Strategy:            MERGE_CANONICAL_INTO_EXISTING_CONTAINER — the room-list
                     sidebar and every hook/API/realtime/overlay stayed
                     exactly as they were (Product Container territory);
                     only the room-pane's presentation layer (header /
                     thread / composer) became the canonical Screen
Container:           frontend/src/platform/wagle/WagleRoomView.tsx
Route/trigger:       /wagle (room selected); back button returns to the
                     room list (setSelectedRoomId(null))
Canonical source:    frontend/src/screens/wagle/FamilyChat/FamilyChatScreen.tsx
Preserved behavior:  room list/selection, realtime connect/gap-recovery,
                     send/retry/error, reply overlay (2g) trigger and
                     state, settings overlay (1t) trigger, files overlay
                     trigger (2b, still fixture-backed pending storage
                     infra — unchanged), board link, auto-scroll-to-latest
Extracted component: FamilyChatScreen + types + fixture (new canonical
                     Screen, not a refactor extraction from elsewhere)
Tests:               lint/build/typecheck only this pass — see Section 8
Evidence:            frontend/src/screens/wagle/FamilyChat/**,
                     frontend/src/pages/FamilyChatPreview/index.tsx,
                     frontend/src/platform/wagle/WagleRoomView.tsx(.module.css)
```

### 5.1 Why `MERGE_CANONICAL_INTO_EXISTING_CONTAINER`, not a literal swap

Direct code comparison showed a genuine structural mismatch: the canonical
`1d` preview is a single fixed room (hardcoded 4 named participants, its
own preview-only bottom dock, no room-switching), while `WagleRoomView` is
a real multi-room messenger (room list + selected room pane). Section 5 of
this Task's own charter requires preserving "room selection" as existing
functionality — a literal full-page swap to the single-room canonical
visual would have deleted it. `MERGE_CANONICAL_INTO_EXISTING_CONTAINER`
(Section 8 of the charter) is the strategy defined for exactly this shape:
container/shell (room list, real data plumbing) stays; only the
presentation layer inside the pane becomes canonical.

### 5.2 Disclosed adaptations (not silent redesign)

- **Preview-only bottom dock removed from the reusable Screen.** The
  fixture's dock had `aria-label="미리보기 하단 메뉴"` (self-disclosed as
  preview-only) and duplicated `MongleAppShell`'s already-real mobile dock
  (`nav.mobileNav`, 3 items). Keeping it in the shared Screen would have
  produced a literal double bottom-dock in Product — a defect this Task's
  own responsive gate (Section 14) requires to be 0. `MongleAppShell`'s own
  comment (Wave 6.0B §8) already recorded a prior PM decision not to build
  the mockup's 4-icon dock as real routes; this is consistent with that
  decision, not a new one.
- **`?room=` URL sync added.** `MongleAppShell.tsx` already contained
  `isWagleConversationMobile = pathname === '/wagle' && searchParams.get('room')`,
  gating a mobile CSS rule (`wagleConversationMode`) that hides the global
  header so the canonical chat header can be primary — per its own comment,
  built for exactly this integration (Wave 6.0B §6.1) but never wired,
  since `WagleRoomView`'s room selection was plain component state. This
  Task added the missing half: `selectedRoomId` now mirrors into `?room=`
  via `useSearchParams`, one-way (state → URL only; no inbound deep-link
  resolution was added, to keep this change to activating the already-built
  switch rather than adding new navigation behavior).
- **`ownParticipantId` resolved for real**, fixing a previously disclosed
  gap (the 2g adapter's own comment: "No participant-name lookup wired to
  this component yet... falls back to neutral label"). The signed-in
  account's own `family_membership_id` (`useFamilyContextStore`'s
  `context.families[].membership.id`) is matched against the room's real
  participants (`ParticipantResponse.family_membership_id`) to find the
  own participant id — both fields already existed in the OpenAPI schema
  and were simply unused for this purpose. This is what makes the
  canonical Screen's own/other bubble split (a real part of its frozen
  visual contract) actually work against real data instead of always
  rendering everything as "other."
- **Participants now load on room selection, not only when the settings
  overlay opens** (`listParticipants` broadened trigger, same existing
  endpoint) — needed for both the header avatar stack and the own/other
  split above; this also still feeds the unchanged `1t` settings overlay.
- **Per-message time display added**, formatting the already-real
  `MessageResponse.created_at` field (previously fetched but never
  rendered) — not new functionality, a real field simply wasn't shown.
- **Preview-only decorative elements with no real functional analog were
  not carried into the reusable Screen**: date-separator grouping, an
  "unread starts here" divider, and an album-notice/photo-message bubble
  style. None of these correspond to an implemented feature anywhere in
  the product (no date-grouping computation exists; no per-thread
  unread-position marker exists; no photo/attachment message type exists
  in `MessageResponse` — `2b`'s file-viewer gate is exactly this absence).
  Per Section 5's "존재하지 않는 기능을 새로 만들지 않는다," these were
  retired along with the fixture messages that only existed to demonstrate
  them, rather than fabricated as fake product behavior. `SERVICE_ACTION`
  messages (a real message type already rendered distinctly in
  `WagleRoomView`) received an equivalent "notice card" treatment in the
  canonical visual language instead.
- **Header action buttons for 1t/2b were added** (파일 🖼 / 설정 ⚙), since
  the canonical `1d` mockup's header has no such icons but `WagleRoomView`
  had real, already-tested trigger buttons for both overlays
  (`wagle-open-files` / `wagle-open-settings`) that Section 20's PASS
  criteria require not to regress ("canonical child trigger 회귀 0").
  Additive, not a redesign of the frozen visual's existing elements.

## 6. Mixed Parent/Child Result

```text
/wagle parent:     WagleLanding (unchanged) -> WaglePinLock -> WagleRoomView
                    (Product Container, now consumes FamilyChatScreen)
board parent:       WagleBoardPage — NOT MODIFIED (out of this Task's
                    implementation scope: DESIGN_DECISION_REQUIRED on 3c/3e)
canonical child surfaces: 1t (ChatSettingsScreen overlay), 2g
                    (ChatReplyScreen overlay), 2b (FileViewerScreen overlay,
                    still fixture-backed) — all unchanged, all trigger
                    points preserved verbatim
2g contract:        CHILD_OF parent chat surface / NO_ROUTE / KEEP_PAGE_
                    LOCAL / INLINE_OVERLAY — untouched; no route added
trigger preservation: wagle-open-files, wagle-open-settings, wagle-reply-{id},
                    wagle-reply-cancel, wagle-open-board all present with
                    identical data-testid values in the new FamilyChatScreen
```

## 7. Common Components

```text
Extracted: FamilyChatScreen + types.ts + familyChat.fixture.ts + index.ts
  under frontend/src/screens/wagle/FamilyChat/ — mirrors the established
  sibling pattern (ChatSettings/ChatReply/FileViewer): model+callbacks
  props, data-canonical-screen-id="1d", own frozen-palette CSS module
  (not the app's design-token system — matching how 1t/2g/2b's own CSS
  modules are also self-contained, since these Screens render as
  full-surface takeovers, not blended chrome)
Reused: none new — ChatReplyScreen/ChatSettingsScreen/FileViewerScreen
  overlays already existed and were not touched
Kept local: message-tone/avatar-initial logic (MessageRow, Avatar) — single
  consumer (FamilyChatScreen itself), no extraction warranted
Rejected extraction candidates: none proposed — this Task's only new
  presentational surface is 1d itself; no 2-plus-consumer duplication was
  found elsewhere in the Wagle target set to justify extracting a second
  shared component (Section 9.1's "actual 2+ consumers" bar was not met by
  anything else)
```

## 8. Single-Source Validation

```text
Product -> canonical:    WagleRoomView imports FamilyChatScreen directly
                          (frontend/src/platform/wagle/WagleRoomView.tsx)
Preview -> canonical:    FamilyChatPreview/index.tsx now a 3-line wrapper:
                          <FamilyChatScreen model={familyChatFixture} />
Product -> Preview import: 0 (grep-verified: FamilyChatPreview is imported
                          only by App.tsx's /__wave6/1d route)
Duplicate legacy/canonical consumer: 0 — the old ad hoc JSX in
                          WagleRoomView and the old duplicate fixture
                          markup in FamilyChatPreview were both removed in
                          the same change, not left as a second copy
Retired legacy source:   frontend/src/pages/FamilyChatPreview/
                          FamilyChatPreview.module.css deleted (0 remaining
                          references, confirmed via grep before deletion)
```

## 9. Behavior Regression (code-review basis; see Section 12 for what was
   and was not runtime-executed)

```text
auth/family context:  untouched — useFamilyContextStore usage unchanged in
                       shape, only a new selector (context) added
realtime:              useWagleRealtime wiring, connection-state labels,
                       gap/reconnect handlers all untouched
message flow:          loadMessages/sendMessage/handleSend logic untouched;
                       only the rendering of the result moved into
                       FamilyChatScreen
room flow:              loadRooms, room-list JSX, room selection untouched
board flow:             not touched (WagleBoardPage out of scope)
navigation/back:        preserved — onBack now routed through
                       FamilyChatScreen's back button to the same
                       setSelectedRoomId(null) call the old backButton used
modal/overlay:          reply/settings/files overlay JSX blocks in
                       WagleRoomView are byte-identical to before except
                       for the settingsMembers -> roomParticipants rename
```

## 10. Screen Tests

```text
component/unit:    none exist for Wagle in this repository today (no
                    *.test.*/*.spec.* under frontend/src/**/wagle/**) — none
                    added this pass; out of this Task's explicit
                    prohibitions is nothing about adding new unit tests,
                    but doing so was judged lower-value than the disclosed
                    runtime gap below given the time available
route:              N/A (1d has no dedicated route; verified via App.tsx
                    read that /wagle and /__wave6/1d wiring is unchanged)
focused E2E:        NOT EXECUTED this pass — see below
viewport results:   NOT EXECUTED this pass — see below
```

## 11. Validation

```text
lint:               PASS (pnpm run lint, exit 0, 0 findings)
build:               PASS (pnpm run build = tsc -b && vite build; one
                    pre-existing >500kB chunk-size warning, unrelated to
                    this Task's files)
tests:               NOT EXECUTED (see Section 12)
detached preview:   statically reviewed, not runtime-executed (see Section 12)
git diff --check:   PASS (clean, no whitespace errors)
check_all.py:        report-only mode, exit 0; all WARNING lines pre-date
                    this Task (none reference MONGLE-W7-4-WAGLE-SINGLE-
                    SOURCE-PRODUCT-INTEGRATION-001); this Task's own new
                    docs re-checked after creation, 0 new warnings
                    attributable to this Task's lineage
known pre-existing warnings: check_active.py/check_closeout.py WARNING
                    lines listed in this Task's QA evidence, all pre-dating
                    this session
```

## 12. Runtime/E2E — explicitly not executed, disclosed rather than assumed

```text
No local backend/.venv exists in this environment.
No local PostgreSQL (psql/pg_isready) is reachable.
The fixed native-E2E resources (DB mc_w75_native_runner, backend :18096,
  Vite :5195) were confirmed NOT already running (not RESOURCE_BUSY —
  simply never started this session).
Standing up a local Postgres cluster and Python venv from scratch was
  judged out of this Task's reasonable scope without explicit operator
  confirmation (an environment-provisioning action, not a code change),
  and was not attempted.
```

Concretely NOT verified by this Task, and not claimed as PASS:

- `tests/e2e/specs-mongle/03-target-ui.spec.ts` Journey 4 (Wagle
  realtime/room-list/connection-state/two-browser message delivery)
- `tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts` (`1t`/`2g` reply
  flow, full-spec `1t`/`2g` coverage)
- 3-viewport (390×844 / 820×1180 / 1180×820) responsive sweep against a
  live Product shell
- `1d` fresh browser session (own/other bubble rendering against real
  multi-participant data, `?room=` URL sync observed live, mobile header
  hiding via `isWagleConversationMobile` observed live)

What was done in place of runtime verification: full manual code trace of
every `data-testid` the existing Playwright specs assert on
(`wagle-room-list`, `wagle-connection-state[data-state]`,
`wagle-composer-input`, `wagle-send`, `wagle-messages`,
`wagle-reply-{id}`, `wagle-reply-overlay`, `wagle-reply-banner`,
`wagle-reply-quote-{id}`, `wagle-open-files`, `wagle-open-settings`,
`wagle-open-board`, `wagle-room-{id}`, `wagle-forbidden`,
`wagle-rooms-empty`, `wagle-messages-empty`) against the new
`FamilyChatScreen`/`WagleRoomView` source — every one is present with an
unchanged attribute contract. This is corroborating evidence, not a
substitute for actually running the suite.

## 13. Documents

```text
Created: engineering/phase2/MONGLE_W7_4_WAGLE_SINGLE_SOURCE_PRODUCT_
  INTEGRATION_REPORT.md (this file)
Created: agent-system/qa/MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-
  INTEGRATION-001.md
Created: agent-system/handoffs/active/MONGLE-W7-4-WAGLE-SINGLE-SOURCE-
  PRODUCT-INTEGRATION-001.md
Updated: engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_
  MATRIX.csv — 12 new additive columns (W7_4_Implementation_Task ..
  Implementation_Evidence), populated for the 7 Wagle rows only, all other
  57 rows left blank in the new columns. Primary_Classification / Confidence
  / Final_Classification / Final_Confidence / Implementation_Readiness
  (all write-once, pre-existing) were not modified for any row.
Updated (minimal): agent-system/active.md, agent-system/relay/current.md
COVERAGE_MAP.md: NO_CHANGE_REQUIRED — no test was executed or added by this
  Task; existing rows already covering this surface
  (E2E-MONGLE-WAGLE-REALTIME-001, API-W2-WAGLE-ORDERING-READ-001,
  E2E-W7-5-FULL-SPEC-001's 1t/2g coverage) remain accurate as historical
  evidence but were not re-run against this Task's changes — re-running
  them is this report's own top follow-up recommendation, not something
  silently assumed still true.
```

## 14. State After Task

```text
W7.4 Wagle integration:      IN PROGRESS -> the single implementation-ready
                              Wagle screen (1d) is now product-integrated;
                              3 screens already complete pre-task (1t, 2g,
                              3d); 3 remain deferred on genuine blockers
                              (2b infra, 3c/3e design decision) — none of
                              which this Task's scope permits resolving
W7.4 overall integration:     IN PROGRESS (Admin/Auth/Markpoint/Family
                              domains untouched, per this Task's own scope)
W7.5 overall:                  CONDITIONAL / HUMAN_GATE (unchanged)
W7.6:                          BLOCKED (unchanged)
```

## 15. Remaining Blockers

| Screen ID | Blocker type | Exact required decision/prerequisite | Why other work was not blocked |
| --- | --- | --- | --- |
| `2b` | INFRASTRUCTURE_PREREQUISITE_REQUIRED | No storage abstraction exists in the backend at all (shared gate with `1h`/`1p`/`2v`/`2y`); needs a storage-infra decision, not frontend engineering | `1d` has no dependency on file storage; its own header-action trigger for `2b` was preserved as-is (still fixture-backed), unaffected |
| `3c` | DESIGN_DECISION_REQUIRED | Reaction-toggle has no click target in the frozen `FamilyBoardProps` type contract | Entirely separate file (`WagleBoardPage.tsx`), never touched by this Task; `1d`'s implementation did not depend on it |
| `3e` | DESIGN_DECISION_REQUIRED | Same reaction-toggle gap, shared with `3c` | Same as above |

## 16. Next Recommended Task

```text
MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
```

A close second recommendation, given this report's own disclosed gap: a
focused runtime/E2E re-verification pass for this Task's `1d` change
(`tests/e2e/specs-mongle/03-target-ui.spec.ts` Journey 4 and
`04-w75-data-wiring.spec.ts`) once a Postgres/backend runtime is available
in-session — before treating this integration as independently confirmed
rather than developer self-check.

## Allowed final declarations actually supported by this Task's evidence

```text
MONGLE_W7_4_WAGLE_SINGLE_SOURCE_PRODUCT_INTEGRATION_CONDITIONAL
WAGLE_IMPLEMENTATION_READY_SCREENS_PRODUCT_BOUND (1/1: 1d)
WAGLE_CANONICAL_SINGLE_SOURCE_PRESERVED
WAGLE_EXISTING_FUNCTIONAL_BEHAVIOR_PRESERVED (by code review; not runtime-confirmed)
W7_4_PRODUCT_INTEGRATION_REMAINS_IN_PROGRESS
W7_5_OVERALL_REMAINS_CONDITIONAL_HUMAN_GATE
W7_6_REMAINS_BLOCKED
```

Not declared, because not supported: `WAGLE_PRODUCT_ENTRY_VERIFIED`,
`WAGLE_RESPONSIVE_PRODUCT_SHELL_VERIFIED`,
`WAGLE_DETACHED_PREVIEW_REGRESSION_PASS` — all three require the runtime
verification disclosed as not executed in Section 12.

No commit, push, merge, or rebase was performed by this task.
