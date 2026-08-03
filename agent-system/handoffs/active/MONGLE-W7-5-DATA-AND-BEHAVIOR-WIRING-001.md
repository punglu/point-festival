# Handoff — MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001

## Status: IMPLEMENTATION_EVIDENCE_FROZEN — READY_FOR_PM_REVIEW / READY_FOR_INDEPENDENT_QA (not PASS)

All resolvable implementation across Phase 0/B/C/D/E/F/G/H is complete,
including `3e` (previously listed below as `NEW_SLICE_REQUIRED`, now
built) and the pre-existing `bcrypt` backend failure (now fixed — the
backend suite is genuinely 375/375, 0 failed, 0 errors as of Phase H).
What remains is exclusively genuine PM decisions: **13 PM/design gates +
1 separate infrastructure gate (`GATE-2B`) = 14 total decision items** —
see `engineering/phase2/MONGLE_W7_5_PM_DECISION_PACKAGE.md` §4 (never
"13 total" including `2b`; that was itself a miscount corrected in
Phase H) — and Independent QA, deliberately not started yet. See "Phase
H" (bottom of this file) for the current, fully reconciled numbers; every
earlier "Phase E/F"/"Phase G"/"Phase 0/B/C/D" block in this file is kept
for historical detail but its gate-count/Phase-D-denominator/backend-
suite figures are stale — do not cite them without reading Phase H first.

## Status (historical, Phase D checkpoint): Phase 0 + Phase B + Phase C + Phase D (10/11 Slices) complete

```
Phase 0 (functional/API inventory):          COMPLETE — 64/64 classified
Phase B (wire existing APIs):                PHASE_B_PROCESSING_COMPLETE = 6/6
  PHASE_B_FUNCTIONALLY_WIRED:                4 — 1a-1, 1r, 1q*, 2t
  PHASE_B_HUMAN_GATE:                        2 — 1u, 2s (DESIGN_CONTRACT_MISMATCH/HUMAN_GATE)
  (* 1q corrected mid-implementation from WIRE_EXISTING_API to EXTEND_EXISTING_API)
Phase C (extend existing APIs):              11 / 11 rows processed
  Fully wired and verified:                  3 — 1t (member-list half), 1s, 2g
  Screen-partially-complete (capability-split): 3 — 1f, 1k, 2z (see Matrix CAPABILITY_STATUS)
  Reclassified, no change needed:            1 — 2c (no bonus mechanic exists; disclosed 0)
  Design-contract gap/mismatch (HUMAN_GATE):  3 — 2o, 3b, 2z's write half (counted once above)
  Policy-blocked (folded into existing gates): 2 — 2p (new), 3i (confirmed)
Phase D (new vertical slices):               10 / 11 Slices built, 19 / 19 candidate
  screens processed (1 Slice, SLICE-WAGLE-ATTACHMENTS / 2b, correctly not
  built — POLICY_REQUIRED, same storage-infra gate as 2v/1p/2z)
  Fully real end-to-end:                     12 — 2n, 1g, 1o, 2u, 1h, 1w, 1l, 2h,
    2j, 1n, 2r, 3c, 3d (13, see Matrix; some rows share one Slice)
    [CORRECTED, Phase G: `1n`'s claim here was false when written —
    NotificationsPage.tsx had no real API calls at all until Phase G's
    frontend audit found and fixed it. See Phase E/F/G sections above.]
  Screen-partially-complete (capability-split): 3 — 1i, 1v, 2y (real backend,
    read or list/toggle real; write/create blocked — frozen Screen has no
    input control, same design-contract-gap shape as Phase C's 2z/3b)
  Design-contract gap (API_READY_UI_BLOCKED): 1 — 3j (real, tested backend;
    frozen Screen's search box is a static <span>, no <input> anywhere in
    its entry chain)
  Reclassified, confirmed still needed:      1 — 3e (NEW_SLICE_REQUIRED,
    reaction/like concept still does not exist; 3c/3d landing was its own
    precondition, now satisfied)
  Not built (policy-blocked):                1 — 2b (storage-infra gate)
Policy/design-gate rows isolated, unchanged from Phase C: 3h, 2f, 2w, 2p, 3i,
  1t's mute (D6-P2), 1u, 2s, 2o, and now also 1i/1v/2y/3j's missing-input
  gap and 2b/3e's own gates
Client-only assumptions (disclosed):         4 — 3f/3g/3k/3l
No backend change needed:                    22 (already real or pure nav/static)

Lint / typecheck / build / diff-check:       all PASS (re-verified after Phase D)
Backend suite (isolated disposable DB):      KNOWN_CONDITION, not PASS — see
  Coverage Map registration below. Same pre-existing, unrelated failure
  carried from Phase C,
  `test_wagle_service_binding.py::test_01_user_jwt_blocked_from_service_ingress`
  (bcrypt 72-byte-limit crash), confirmed via `git stash` to be pre-existing
  on clean HEAD, not fixed here (out of declared scope).
3c/3d additionally live-verified in a real Chromium session (Playwright)
  against the isolated stack, not just typechecked: a real HTTP-created
  board post rendered and opened, a real comment submitted through the
  Screen's own input rendered in the thread.
```

## Phase E/F — reconciliation, `3e` build, closeout-readiness (current, supersedes stale figures above)

Authoritative detail: `engineering/phase2/MONGLE_W7_5_PM_DECISION_PACKAGE.md`
(new document, primary artifact of this pass) and
`agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md`'s "Phase E"
and "Phase F" sections. Summary:

```
Phase B:     re-verified against live source, no defect — 4 wired, 2 HUMAN_GATE
Phase C:     11/11 (corrected from a prior tally that summed to 10)
Phase D:     PHASE_D_TOTAL_SLICES_ORIGINAL_SCOPE: 11 (declared by
             MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md from the start,
             including 2b — "listed here for completeness of the
             11-Slice count", that document's own words; 2b is INSIDE
             the original 11, never a 12th slice added on top)
             CODE-IMPLEMENTABLE_SLICES_COMPLETE: 10 / 10 (verified this
             pass by directory existence: family_todo/, family_rules/,
             notification_preferences/, family_schedule/, family_album/,
             reward_catalog/, account_notification/,
             family_activity_log/, family_search/ all exist, plus
             wagle/'s reaction toggle/ranking code for 3e — 10 domains,
             matching 10 of the 11 original Slices)
             INFRASTRUCTURE-BLOCKED_SLICE: 1 of the 11 (2b — correctly
             not built, POLICY_BLOCKED on the storage-infra decision,
             not a code gap)
             21/21 screens processed; 3e no longer open (see below).
             Never write "Phase D 11/11 complete" without the split
             above — 2b is one of those 11, not built, and folding it
             silently into "11/11" is exactly the contradiction this
             checkpoint exists to remove.
Phase E:     scope reconciliation + 6 real frontend defects found and
             fixed + Matrix API_READINESS data-loss defect fixed +
             2 taxonomy mislabels corrected + 17-raw/13-canonical PM gate
             table built + 2b's full 16-field/4-option Decision Package written
Phase F:     permanent 3c/3d/3e Playwright spec run for real (not just
             committed) — first run failed on a genuine test defect, fixed;
             re-seed exposed a second genuine seed-script defect, fixed;
             re-run PASS 1/1
Independent QA: NOT STARTED (by design — genuine PM decisions must clear first)
Overall verdict: CONDITIONAL / HUMAN_GATE — never plain PASS while genuine
  PM decisions remain open
```

**`3e` (SLICE-WAGLE-BOARD-REACTIONS) resolved and built**, correcting the
Phase-D-era `NEW_SLICE_REQUIRED` classification below: both `3c`'s and
`3e`'s own frozen canonical Screens already render `♥ likes · 💬 comments`,
so the product meaning was already determined — this was
`IMPLEMENTATION_REQUIRED`, not a PM question. Built: migration
`0020_wagle_message_reactions` (toggle semantics via a unique
`(message_id, reactor_membership_id)` constraint), `wagle.service.
react_to_message`/`reaction_counts_for`/`list_popular_posts`, two router
endpoints, additive `MessageResponse.reaction_count`/`.reacted_by_me`
fields. 8 new backend tests, all pass. Real counts wired into `3c`'s post
list and `3e`'s ranked Popular Posts list. The reaction *toggle* itself
still has no click target in either frozen Screen's type contract — that
specific gap is tracked as a canonical PM gate (`DESIGN_CONTRACT_REQUIRED`),
not silently left undone.

**Two real defects found and fixed while running the permanent 3c/3d/3e
Playwright spec** (`tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts`) for
real evidence rather than trusting it as committed-but-unexecuted:
1. The spec itself called `page.goBack()` expecting it to return to
   `WagleBoardPage.tsx`'s board list, but that view is local component
   state (`openPostMessageId`), not a route — `goBack()` left `/wagle/board`
   entirely. Fixed by clicking the comment composer's own `←` (`onCancel`)
   control instead.
2. `backend/scripts/phase1_seed_synthetic.py`'s cleanup loop deleted
   `WagleParticipant` before `WagleMessage`/`WagleParticipantReadState`,
   violating an `ON DELETE RESTRICT` FK the first time this specific seed
   DB ever held a real Wagle message (i.e., after this task's own Phase E
   Playwright run created one). Fixed by reordering the delete list.

Neither fix touched product code. Re-run after both fixes: 1 passed (3.0s),
full real flow verified end to end.

**Two additional defects found this pass, both in the Matrix/gate
bookkeeping, not code**: `1f`'s streak/badge sub-capabilities were
mislabeled `NEW_SLICE_REQUIRED` (corrected to `POLICY_REQUIRED` — they are
undefined game-mechanic questions, not unbuilt code); `2b`'s
`FINAL_W7_5_STATUS` field still literally read `NEW_SLICE_REQUIRED` despite
every other reference correctly saying `POLICY_BLOCKED` (corrected for
consistency). The Matrix's `API_READINESS` field for `1q`/`1u`/`2s` had
also been overwritten in place during Phase B, losing the original Phase-0
value — a new `ORIGINAL_API_READINESS` column now preserves both.

**"14 PM gates" was a miscount**: `active.md` said "14 total" while
literally naming 17 distinct screen-level flags. Reconciled to 17 raw
flags, 13 canonical decisions after merging true duplicates (the
family-invitation model folds `2f`/`2w`/`2p`/`3i` into one gate; the
PIN-digit mismatch folds `1u`/`2s` into one). Full per-gate table (question,
existing evidence, recommended option, alternatives, default-if-deferred,
whether it blocks W7.5 PASS) plus `2b`'s own full storage-infrastructure
Decision Package (16 fields, 4 named options with pros/cons/migration/
frontend impact) are in the PM Decision Package document.

**Full backend suite, cleanest run of the task**: 374 passed, 1 failed
(pre-existing, unrelated `bcrypt` 72-byte crash in
`test_wagle_service_binding.py`, confirmed pre-existing via `git blame` —
predates this task, not touched by it), 0 errors. Backend-suite
`KNOWN_CONDITION` (Wagle concurrency non-determinism) remains registered in
`COVERAGE_MAP.md`, unaffected and unresolved by this pass (separate,
not-yet-scheduled work).

**What is genuinely still open, and why none of it is more code work**:
the 13 canonical PM/design gates (family-invitation model, PIN-digit
mismatch, account deletion, legacy-admin/family-scope bridge, Wagle mute,
six missing-input-control Screens, streak/badge mechanic, reaction-toggle
click target) all require an actual product/design decision this task has
no authority to make — each has a recommended option and disclosed
default-if-deferred in the PM Decision Package, not a silent pick. `2b`
(Wagle attachments storage) additionally needs an infrastructure decision
(local disk vs. S3-compatible vs. DB bytea vs. disable) before any storage
code is written — building any of the four options before that decision
would risk a real migration/frontend-impact cost on a guess. Independent
QA is intentionally not started, per this task's own instruction that it
only begins after all resolvable implementation is complete and PM gates
are documented — that condition is now met.

## Phase G — migration downgrade verified in full; frontend audit found `1n` was never actually wired

Full detail: QA evidence "Phase G" section. Two closeout-readiness checks
completed:

- **Migration downgrade, full chain**: all 9 migrations `0012`→`0020` have
  real (non-stub) `downgrade()`s; a fresh throwaway DB was taken to head,
  downgraded all the way back to `0011`, and re-upgraded to head — zero
  errors, and 3 representative table/column additions were confirmed to
  genuinely appear/disappear via direct schema inspection, not just exit
  codes.
- **Frontend functional-state audit, broadened beyond the fixture-fallback
  pattern**: 6 more real defects found and fixed (`FamilySchedulePage.tsx`
  delete-failure/create-failure/stale-error handling,
  `FamilyTodoPage.tsx` silent toggle-failure, `FamilyAlbumPage.tsx`'s
  nested photo-detail fixture-leak + search-error + fake-match-card,
  `ProfilePage.tsx`'s silent notification-toggle failure,
  `WagleBoardPage.tsx`'s comment-send failure never shown in context).
  **More significant**: `NotificationsPage.tsx` (`1n`) was found to be
  calling nothing real at all — contradicting this file's own "Fully real
  end-to-end" claim for `1n` two sections above, corrected in place. The
  backend and API client were genuinely built and tested in Phase D; the
  page consuming them was simply never wired, an exact instance of this
  task's own "Backend exists ≠ Frontend complete" rule, caught late by
  this checkpoint rather than by the phase that originally claimed it
  done. Fixed now, real end to end. One item found and deliberately left
  unfixed and disclosed: the frozen `CommentComposerScreen` has no
  send-button pending/disable state — fixing it would require adding a
  prop to a frozen canonical Screen's type contract, out of bounds without
  a PM/design decision.
- `tsc --noEmit` and `eslint` both clean after all fixes.
- This does not change the 13-canonical-gate count or the Slice/screen
  totals — `1n` was already counted as wired/complete in the Matrix; the
  correction is that the claim is now actually true, not that scope
  changed.

## What this task did

### Governance correction (before Phase 0)
W7.3 and W7.4 had real completed code but were never registered anywhere in
the Agent System. Corrected: both graduated to `graduated/2026-08.md`
(self-reported, never independently QA'd — same disclosed pattern as
`MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001`), their handoffs archived,
W7.4's QA evidence got an explicit `HISTORICAL_POLICY_DEVIATION` section
(that task used `/tmp` scripts and mutated the persistent dev DB —
disclosed, not retroactively justified, does not reverse its self-reported
PASS). `relay/current.md` points here; all prior history preserved.

### Phase 0 — full 64-screen functional/API inventory
Two parallel research passes (backend: all 18 domains, every route, auth
model, schema; frontend: every API client, every W7.4 Product Container's
real-vs-fixture data source) plus a live read-only OpenAPI cross-check.
Full findings in `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_REPORT.md`.

Headline: rich real Account-native APIs already exist for family/members/
roles, Markpoint (missions/ledger/level/config), and Wagle
(rooms/messages/realtime/push/device-PIN). **Zero backend exists** for
schedule, album/photo, todo, family-rules, search, reward-catalog,
family-board, or account deletion — confirmed by grep, not assumed.

### Phase B — complete: 4 wired, 2 correctly blocked
`1a-1` (Account-native login — found and fixed a real defect in the
process, below), `1r` (family creation), `1q` (family member list), `2t`
(admin notification send) all now call real backend endpoints, verified
end-to-end via the **permanent** `tests/e2e/specs-mongle/
04-w75-data-wiring.spec.ts` + `tests/e2e/playwright.mongle-manual.config.ts`
(a companion config for running the same specs against a self-managed
disposable stack instead of the shared `mc_phase1` Compose project, which
was already running persistently for unrelated reasons when this task
started — see the config's own file header). An earlier pass of this
checkpoint used a scratch script that was deleted after use; corrected per
PM direction — the spec/config are now committed artifacts, not disposable.

`1u`/`2s` (Wagle device-PIN change/initial-setup) were wired to the same
pattern, then **reverted** when real verification found the backend
requires a 6-digit PIN while both frozen W7.3 Screens have a 4-dot/4-key
design — extending either would be a visual-baseline redesign, explicitly
out of scope. Reclassified `DESIGN_CONTRACT_MISMATCH`/`HUMAN_GATE` rather
than forced through.

**Real defect found and fixed**: `shared/api/httpClient.ts`'s global 401
interceptor was missing `/api/auth/account/login` from its no-global-
redirect allowlist, so a wrong password on the real login screen was
misread as an expired session and force-redirected to the legacy
player-select screen, discarding the login screen's own error state.
Found by the Playwright spec's own wrong-password test failing, not by
inspection.

**Two backend changes made**, both additive, no migrations:
- `MembershipSummary.account_display_name` (`family/schema.py`,
  `service.py`, `router.py`) — `1q`'s classification was corrected from
  `WIRE_EXISTING_API` to `EXTEND_EXISTING_API` mid-implementation when this
  was discovered by actually trying to wire it.
- Backend-Guide-audited on PM request afterward: no cross-domain-ORM
  violation, Thin Controller/Service SSOT intact, matches an existing
  unannotated `db.get()` convention already in the file, additive/backward-
  compatible, OpenAPI diff exactly 2 lines, 318/318 backend suite pass on
  the clean run.

### Phase C — started: `1t` done (1/11)
Same gap shape as `1q`: `ParticipantResponse` only had
`family_membership_id`, no display name. Fixed identically
(`wagle/schemas.py`, new `service.participant_display_name()` cross-domain
helper via `family_service.get_account()` — matching this file's own
pre-existing `family_service` import pattern, not a new violation,
`router.py`'s `participant_out()` made async across all 4 call sites).
Frontend: `wagleApi.ts` gained `listParticipants()`, `WagleRoomView.tsx`'s
chat-settings overlay now shows real member names. Verified via the same
permanent spec (new `1t` test block). Focused Wagle suite 112/112; full
suite results feed the `KNOWN_CONDITION` finding above (this change
touches only sequential reads, not the concurrent-write paths that failed).

### Phase C — complete (11/11 rows processed)

Full row-by-row outcome table is in the Report's §9. Summary of what
shipped, all additive, one migration (`0012_profile_mission_fields`, name
kept ≤32 chars per 0011's own documented `alembic_version.version_num`
trap):

- **`accounts.bio` / `birthday` / `avatar_color`** (nullable) + `PATCH
  /api/me` (self-service, no permission beyond authentication) + `PATCH
  /api/families/{family_id}/members/me` (self-service relationship label,
  bypasses `FAMILY_MEMBERS_MANAGE` by design — a member declaring their own
  role is not FamilyAdmin authority over someone else, and the schema has
  no `status` field). Wired into `1f`'s real profile display and `2z`'s
  read side.
- **`markpoint_missions.description` / `.checklist`** (nullable Text /
  JSONB) + new `PATCH .../missions/{id}/checklist` (assignee-only, only
  while `status=active`) + `MissionOut.rejection_reason`/
  `reviewer_display_name` (the latter via a new `mission_out()` async
  builder used at every mission-returning endpoint, same cross-domain-
  resolve shape as `1t`'s `participant_out`). Wired into `1k`'s real,
  interactive checklist and `1s`'s real reviewer/reason.
- **`wagle_messages.reply_to_message_id`** exposed on `MessageCreate`/
  `MessageResponse` (column already existed, unused) + a same-room
  existence check in `send_message` (never trust a client-supplied id to
  belong to this Room without a server lookup). Wired into `2g`: the
  frozen overlay's own compose bar has no real input, so real typing was
  routed through the room's always-real composer, carrying the pending
  reply target through as a cancellable banner.

**Three genuine gaps found by attempting the wiring, not by inspection
alone** (same discipline as `1u`/`2s`'s PIN mismatch):

- **`2o`**: legacy admin (`require_admin`, platform-wide, no Family
  concept) vs. the family-scoped Account-native config endpoint are two
  authorization systems that cannot present the same credential to each
  other. `DESIGN_CONTRACT_MISMATCH` — needs a PM decision (family-selector
  bridge, or defer to a future Account-native admin surface), not a
  silent pick.
- **`3b`**: backend fit-check confirmed `cycle-progress`/`weekly-summary`
  are period-filterable and ready, but the frozen Screen's `<select>`s each
  have exactly one hardcoded option and `onApply` takes no arguments —
  `DESIGN_CONTRACT_GAP`, nothing to wire the ready backend to.
- **`2z`'s write half**: every field renders as non-editable text with no
  color-swatch click handler. The write endpoints are real and tested but
  intentionally not called from this Screen — wiring a fabricated save
  would invent a value the user never entered.

**One reclassification correcting this task's own earlier framing**
(`2p`, was `PARTIAL_WIRING_PENDING` in Phase 0): the screen's `Invitation`
type is keyed on `email`, and D2 already excludes email/phone from the
Account-native credential model entirely (grep-confirmed zero email field
anywhere in the family domain). Folded into the same
`POLICY-FAMILY-INVITATION-MODEL` gate as `2f`/`2w`/`3i`, one level more
specific: whatever model is chosen must also decide the invitee identity
key.

Test evidence: 15 new backend tests
(`backend/tests/test_w75_phase_c_extensions.py`), 4 new Playwright cases
in the permanent `04-w75-data-wiring.spec.ts` (`1f`, `1k`, `2g`), full
backend suite re-run. Isolated environment for this phase: disposable
`postgres:16.9-alpine` on port 15435 (`mc_w75_phasec_db`), throwaway
backend on port 18099, a second throwaway Vite dev server on port 5199
proxying to it — none of them the persistent dev runtime
(`mongle-db-1`/`mongle-backend-1`/`mongle-frontend-1`), all torn down after
use.

## Notable findings worth carrying forward

- **`2t` was misclassified as a gap in W7.4.** `POST /api/admin/notifications`
  already existed and matched the screen exactly — a pure frontend-wiring
  quick win, now closed.
- **The "list endpoint has an ID but no display name" gap is a recurring
  pattern**, not a one-off: hit twice now (`1q`'s `MembershipSummary`,
  `1t`'s `ParticipantResponse`), same fix shape both times. Worth checking
  proactively before starting any remaining `EXTEND_EXISTING_API` row that
  touches a list endpoint.
- **`2f`, `2w`, `2p`, `3i` share one policy gap**: no self-service,
  invitee-initiated family-join flow exists at all, only FamilyAdmin-
  initiated provisioning. Recommend resolving as one "family invitation
  model" PM decision, not four.
- **`1l`, `2h`, `2j` share one reward-catalog gap** — build once, not three
  times.
- **Album upload (`2v`) and avatar upload (`2z`) share a real infra gap**:
  no storage abstraction exists anywhere in the backend. `POLICY_REQUIRED`,
  distinct from ordinary `API_MISSING` metadata CRUD.
- **`1u`/`2s`'s 4-digit-vs-6-digit PIN mismatch** — a real UI/backend
  contract gap found only by attempting the wiring and verifying against
  the real endpoint, not by reading either side's code in isolation.
- **Legacy `/api/notifications` is not safely reusable for `1n`**: it's
  `player_id`-scoped via `LegacyIdentityMapping`, which the frozen D8
  decision excludes for new Account-native users.

## Deferred / next

- **Phase D remainder**: `2b` (`SLICE-WAGLE-ATTACHMENTS`, `POLICY_REQUIRED`
  on the storage-infra gate) and `3e` (`SLICE-WAGLE-BOARD-REACTIONS`,
  `NEW_SLICE_REQUIRED` — needs a reaction/like concept that still does not
  exist anywhere in Wagle; its own precondition, `3c`/`3d` landing, is now
  satisfied).
- **A repeating missing-input-control gap, now spanning both Phase C and
  D**: `1i` (할 일 추가), `1v` (규칙 저장), `2y` (구성원별 접근 권한), `2z`
  (프로필 편집), `3b` (통계 필터), `3j` (검색) all have a real, tested
  backend but their frozen canonical Screen has no input control to drive
  it from (a static `<span>`/label instead of an `<input>`, or a button
  with nothing behind it). Needs a PM/design decision to add real inputs
  to these six Screens before their write/read paths can be used from the
  UI — not more backend engineering.
- **13 other policy/design-gate items** unchanged from Phase C: account
  deletion (`3h`), family-invitation model + invitee-identity-key
  (`2f`/`2w`/`2p`/`3i`), Wagle room mute (`1t`'s remaining half,
  already-registered `D6-P2`), the `1u`/`2s` PIN-digit-length mismatch,
  the `2o` legacy-admin/family-scope authorization bridge.
- Backend-suite `KNOWN_CONDITION` is now formally registered in
  `agent-system/qa/COVERAGE_MAP.md`
  (`KNOWN-W7-5-WAGLE-CONCURRENCY-001`); stabilizing the actual
  non-deterministic contention remains separate, not-yet-scheduled work
  and is still a precondition for a genuine full-suite PASS.
- Independent QA per `.claude/agents/test-agent.md` — not started for any
  phase of this task.

## Phase D implementation detail

10 new backend Slices (migrations `0013`→`0019`, plus 2 read-only Slices
with no migration — `SLICE-FAMILY-ACTIVITY-LOG` reads `MarkpointAuditEvent`,
`SLICE-SEARCH` reads Missions + Wagle messages, `REUSE-WAGLE-ROOMS-AS-BOARD`
reuses `WagleRoom`/`WagleMessage` with zero schema change). Full per-Slice
detail, outcome table, and the recurring missing-input-control finding are
in the Report's §10/§11 — not duplicated here. Two design decisions worth
flagging for whoever picks this up next:

- **`markpoint_target.service.self_spend`** (new): a member spending their
  own points (Reward redemption) needs `require_access` only, never
  `POINTS_ADJUST` — that permission is admin-only and no child holds it.
  Reusing `adjust_points` would have required granting redemption
  authority no design intends a child to have.
- **The Wagle board is one `WagleRoom` per Family** (reserved sentinel
  title, never shown to the user) with posts as plain `WagleMessage`s
  encoding `[category] title\nsummary` in the body — zero schema change.
  Comments reuse `2g`'s `reply_to_message_id` directly.

34 new backend tests (`backend/tests/test_w75_phase_d_slices.py`).
`3c`/`3d` were also live-verified in a real Chromium session via Playwright
against the isolated stack (not committed as a permanent spec — an ad hoc
verification, deleted after use, per the same discipline that keeps
scratch scripts out of the worktree): real HTTP-created post rendered and
opened, a real comment submitted through the Screen's own input rendered
in the thread.

## Where to look

- Matrix: `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_MATRIX.csv`
  (64 rows, `BACKEND_SLICE_ID` column groups screens sharing one Slice;
  `CAPABILITY_ID`/`CAPABILITY_STATUS`/`POLICY_DEPENDENCY` columns split
  per-capability status where a screen-level status would hide a gap)
- Report: `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_REPORT.md`
  (§12 has the current Phase E/F reconciliation; §0-§11 are the Phase 0-D
  historical record and are not all still current — read §12 first)
- PM Decision Package (current, authoritative gate list):
  `engineering/phase2/MONGLE_W7_5_PM_DECISION_PACKAGE.md`
- Phase D Slice mapping: `engineering/phase2/MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md`
- QA evidence: `agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md`
- Coverage Map: `agent-system/qa/COVERAGE_MAP.md`
  (`API-W7-5-PROFILE-MISSION-WAGLE-EXT-001`, `KNOWN-W7-5-WAGLE-CONCURRENCY-001`)
- Reproducible E2E spec: `tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts`
  (run via `MONGLE_PLAYWRIGHT_BASE_URL=<your dev server> npx playwright
  test --config playwright.mongle-manual.config.ts specs-mongle/04-w75-data-wiring.spec.ts`
  against a self-managed isolated backend — see the config file header)

## Phase H — Final Pre-Independent-QA Reconciliation and Evidence Freeze (current, authoritative)

Full detail: QA evidence "Phase H" section; Report §14. This is the
authoritative, current state — every number above this section that
conflicts with the following is superseded:

```
PM_AND_DESIGN_GATES: 13 (GATE-3E-REACTION-TOGGLE added as the 13th;
  GATE-2B removed from this count — it was wrongly folded in before)
INFRASTRUCTURE_DECISION_GATE: 1 (GATE-2B, separate)
TOTAL_UNRESOLVED_DECISION_ITEMS: 14
PHASE_D_TOTAL_SLICES_ORIGINAL_SCOPE: 11 (2b is inside this 11, not a 12th)
CODE-IMPLEMENTABLE_SLICES_COMPLETE: 10/10
INFRASTRUCTURE-BLOCKED_SLICE: 1 (2b)
BACKEND_SUITE: 375 passed, 0 failed, 0 errors (bcrypt defect fixed;
  re-verified twice, both clean)
PLAYWRIGHT_FULL_SPEC: 10 passed, 0 skipped, 0 failed (2t skip resolved)
BACKEND_GUIDE_BOUNDARY_FIX: family_activity_log/family_search now call
  markpoint_target.service/wagle.service via dotted reference instead of
  querying their models directly (0 behavior change, 0 regressions)
FRONTEND_DEFECT_FIXED: ProfilePage.tsx secondary-stat fixture fallback
  (level/balance/mission-count/member-count) — now real "unavailable"
  state instead of fake fixture numbers on failure
MIGRATIONS_MODEL_METADATA_CROSS_CHECK: 9/9 zero drift
VERDICT: IMPLEMENTATION_EVIDENCE_FROZEN / READY_FOR_PM_REVIEW /
  READY_FOR_INDEPENDENT_QA — never MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS
  or INDEPENDENT_QA_PASS while the 14 decision items remain open
```

No commit/push/merge/rebase performed this checkpoint. All throwaway
infrastructure used this checkpoint (`mc_bcrypt_verify`, `mc_w75_r3_db`,
`mc_guide_fix_verify`, and the migration-verify container from an earlier
checkpoint) torn down; no leftover process on any throwaway port.

## Phase I — MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001 (current, authoritative)

Full detail: QA evidence "Phase I" section; Report §15. **Disclosure**:
`agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-001.md` — the report this
remediation instruction named as its own evidence — does not exist in this
repository, its git history, or any task registry. Every technical claim
was independently reproduced against current source and a live disposable
database before being acted on.

```
F1_ROOT_CAUSE_CONFIRMED: true (int bound into a text-concat interval expr,
  reproduced with the exact original error text)
F1_FIXED: true (5-line diff, wagle/service.py, :days * INTERVAL '1 day')
F1_REGRESSION_TESTS_ADDED: 7 (proven real via revert-and-reconfirm: 5
  failed with the original error when temporarily reverted)
F1_PLAYWRIGHT_EVIDENCE_GAP_FIXED: true (network-response assertion +
  overlay-scoped text, replacing a page-wide text search that could pass
  even on a 500)
F1_NEW_DEFECT_FOUND_BY_STRICTER_ASSERTION: board-room creation race
  (app's own mount effect vs. the test's own identical find-or-create
  logic) — fixed at test level only (waitForLoadState('networkidle'));
  the same race in real concurrent multi-device usage is disclosed to PM,
  not fixed (needs a migration-level unique constraint, out of this
  checkpoint's stated no-new-migration scope)
F1_FRONTEND_DEFECT_FOUND_AND_FIXED: WagleBoardPage.tsx's Popular Posts
  fetch failure was indistinguishable from a genuine empty result — added
  a distinct error state
F2_RUNNER_SCRIPT: tests/e2e/scripts/run-w75-full-spec.sh (new, documented
  in tests/README.md) — disposable DB+backend+frontend, synthetic admin
  password generated and hashed locally (never written to a file), full
  spec run, unconditional teardown. Verified 2 consecutive times: 10
  passed, 0 skipped, 0 failed both times.
F3_BACKEND_SUITE_RUN_1: 382 passed, 0 failed, 0 errors
F3_BACKEND_SUITE_RUN_2: see QA evidence for the exact confirmed count
F5_BASELINE_RESTORED: tests/e2e/test-results/.last-run.json restored to
  HEAD via `git checkout --` on that one tracked file after this
  checkpoint's own Playwright runs modified it (drift reproduces on every
  run; restored each time)
UNRELATED_CONCURRENT_WORK_OBSERVED: a branding change (BrandCharacter
  component + aria-hidden fixes across 6 files) already/still in progress
  in this same worktree, not this checkpoint's own work — recorded, not
  touched
VERDICT: REMEDIATION_EVIDENCE_FROZEN / READY_FOR_FOCUSED_INDEPENDENT_RE_QA
  — never MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS or
  MONGLE_W7_5_INDEPENDENT_QA_PASS while the 14 PM/infrastructure decision
  items remain open
```

No commit/push/merge/rebase performed. All throwaway infrastructure used
this checkpoint torn down and verified via `docker ps -a`/`lsof` after
every run, not only claimed.
