# MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001 — Phase 0 Report

## 0. Matrix numeric reconciliation (PM-requested correction)

The Matrix now carries a `BACKEND_SLICE_ID` column so `SCREEN_ID →
BACKEND_SLICE` relationships are explicit rather than implied. **Screen
counts (64) and Slice counts are never mixed** below — every number states
which of the two it counts.

**Why 22 `API_MISSING` screens ≠ 19 `CREATE_NEW_VERTICAL_SLICE`:** not
every `API_MISSING` screen needs a brand-new backend Slice. The 22 break
down as:

| Of the 22 `API_MISSING` screens | Count | `IMPLEMENTATION_STRATEGY` |
| --- | --- | --- |
| Need a genuinely new backend Slice | 19 | `CREATE_NEW_VERTICAL_SLICE` |
| Can reuse Wagle rooms/messages as-is (no new table) | 2 (`3c`, `3d`) | `REUSE_EXISTING_PRODUCT_LOGIC` |
| Can extend an already-real endpoint instead | 1 (`2z`, extends `GET /api/me`) | `EXTEND_EXISTING_API` |

**The 19 `CREATE_NEW_VERTICAL_SLICE` screens map to only 11 distinct
backend Slices**, because several screens share one underlying aggregate:

| `BACKEND_SLICE_ID` | Screens (count) |
| --- | --- |
| `SLICE-SCHEDULE` | `1g`, `1o`, `2u`, `3a` (4) |
| `SLICE-ALBUM-METADATA` | `1h`, `1p`, `1w`, `2y` (4) |
| `SLICE-REWARD-CATALOG` | `1l`, `2h`, `2j` (3) |
| `SLICE-TODO` | `1i` (1) |
| `SLICE-NOTIFICATION-LIST` | `1n` (1) |
| `SLICE-NOTIFICATION-PREFERENCES` | `2n` (1) |
| `SLICE-FAMILY-RULES` | `1v` (1) |
| `SLICE-FAMILY-ACTIVITY-LOG` | `2r` (1) |
| `SLICE-WAGLE-ATTACHMENTS` | `2b` (1) |
| `SLICE-WAGLE-BOARD-REACTIONS` | `3e` (1) |
| `SLICE-SEARCH` | `3j` (1) |
| **Total** | **19 screens, 11 Slices** |

**`EXISTING_API_READY` (20 screens) — current status of each, verified
directly against the Matrix CSV (not reconstructed from memory):**

| Status | Count | Screens |
| --- | --- | --- |
| `ALREADY_WIRED` (real before this task touched them) | 16 | `1a`, `1b`, `1c`, `1d`, `1e`, `1j`, `1j-1`, `1m`, `1x`, `1z`, `2a`, `2e`, `2i`, `2l`, `2m`, `2x` |
| `WIRED_AND_VERIFIED` this checkpoint (Phase B done) | 3 | `1a-1`, `1r`, `2t` |
| `WIRE_EXISTING_API_PENDING` (Phase B, next) | 1 | `1u` |
| **Subtotal, `EXISTING_API_READY`** | **20** | |

`2s`'s `API_READINESS` is `FRONTEND_ADAPTER_REQUIRED`, not `EXISTING_API_READY`
(it reuses the Wagle device-PIN endpoint as a *candidate*, not yet
confirmed as the final design — see its own Matrix note) — it is Phase
B's other remaining item but is not part of the 20 above.

`1q` started as `EXISTING_API_READY` in the initial Phase 0 pass, then was
**corrected to `API_PARTIAL`** mid-implementation (its `MembershipSummary`
response turned out to lack a display name) — it is counted under
`API_PARTIAL` (11 total) below, not under this 20, and its `IMPLEMENTATION_
STRATEGY` is `EXTEND_EXISTING_API`, now `WIRED_AND_VERIFIED` after the
additive fix.

## 1. Task

Wire the 64 W7.4-bound canonical Screens to real data, mutations, auth/
permission, and error states. Reuse existing Backend/API where possible,
extend minimally where partial, build new vertical Slices only where
genuinely missing. Do not build a policy-undecided feature ahead of a PM
decision.

## 2. Status at this checkpoint

**Phase 0 (functional/API Inventory): COMPLETE — 64/64 classified.**

**Phase B — `PHASE_B_PROCESSING_COMPLETE = 6/6`** (all 6 Phase B rows
reached a final, evidenced classification; this is a processing-throughput
count, not a functionality count):
- `PHASE_B_FUNCTIONALLY_WIRED = 4/6` — `1a-1`, `1r`, `1q`, `2t` call real
  backend endpoints, verified end-to-end.
- `PHASE_B_HUMAN_GATE = 2/6` — `1u`, `2s` were found genuinely blocked on a
  real design/backend contract mismatch (4-digit Screen vs. 6-digit backend
  PIN) and correctly reclassified `DESIGN_CONTRACT_MISMATCH`/`HUMAN_GATE`
  rather than forced through. These 2 are **not** functionally wired; do not
  read `PHASE_B_PROCESSING_COMPLETE` as "6 screens work."

**Phase C (extend existing APIs): 1/11 done** (`1t` — and even `1t` is not a
single undivided status: its member-list capability is
`WIRED_AND_VERIFIED`, its mute-toggle capability is separately
`POLICY_REQUIRED`/`HUMAN_GATE` on `D6-P2`. See the Matrix's own
`CAPABILITY_ID`/`CAPABILITY_STATUS`/`POLICY_DEPENDENCY` columns — a
Screen-level status is never allowed to collapse a per-capability policy
gap out of view). **Phase D (new vertical slices): not started** (19 rows,
11 backend Slices). Full detail in this task's QA evidence. Not a final
W7.5 verdict.

## 3. Governance correction (performed before Phase 0)

W7.3 and W7.4 had real completed code, reports, handoffs, and QA-evidence
files but were never registered in `agent-system/active.md`,
`agent-system/graduated/`, or `agent-system/relay/current.md` — the exact
registration-gap failure shape `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-
AUDIT-002` exists to catch. Corrected per PM direction:

- W7.3/W7.4 graduated to `agent-system/graduated/2026-08.md`, matching the
  existing `MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001` precedent (self-
  reported, never independently QA'd, disclosed as such).
- Their handoffs moved from `handoffs/active/` to `handoffs/archive/2026-08/`.
- `agent-system/qa/MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001.md` now
  carries an explicit `HISTORICAL_POLICY_DEVIATION` section: that task's own
  verification used `/tmp` scripts and mutated the **persistent** dev-runtime
  database (`mongle-db-1`) rather than the isolated `mc_phase0`/`mc_phase1`
  stacks `tests/README.md` requires. Disclosed, not retroactively justified;
  does not by itself reverse the self-reported PASS, but flags the evidence
  as not independently reproducible from a disposable environment.
- `relay/current.md` now points at this task; all prior Wave 5/6 history
  preserved, not deleted.
- W7.5 registered as the sole `active.md` entry.

## 4. Phase 0 methodology

Two parallel research passes, cross-validated against a live read-only
`GET /openapi.json` call to the already-running dev backend (non-destructive
reconnaissance only — no data was created, mutated, or read as a test
fixture):

1. **Backend capability inventory** — every route in all 18
   `backend/app/domains/*` directories, with method, path, auth-dependency
   type (Legacy player/admin JWT vs. Account-native vs. Hybrid-accepts-both),
   request/response schema, and backing table.
2. **Frontend data-source inventory** — every existing API client/hook,
   and for each of the 16 real Product Containers built in W7.4, whether it
   currently consumes real API data, a static fixture, or a mix.

## 5. Phase 0 Matrix — final counts

`engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_MATRIX.csv`,
64/64 rows, no duplicates, no omissions.

### API_READINESS (sums to 64)

| Value | Count |
|---|---|
| `API_MISSING` | 22 |
| `EXISTING_API_READY` | 21 |
| `API_PARTIAL` | 10 |
| `NO_BACKEND_REQUIRED` | 6 |
| `POLICY_REQUIRED` | 4 |
| `FRONTEND_ADAPTER_REQUIRED` | 1 |

### IMPLEMENTATION_STRATEGY (sums to 64)

| Value | Count |
|---|---|
| `NO_BACKEND_CHANGE_REQUIRED` | 22 |
| `CREATE_NEW_VERTICAL_SLICE` | 19 |
| `EXTEND_EXISTING_API` | 11 |
| `WIRE_EXISTING_API` | 6 |
| `POLICY_BLOCKED` | 4 |
| `REUSE_EXISTING_PRODUCT_LOGIC` | 2 |

### FINAL_W7_5_STATUS (interim, sums to 64)

| Value | Count | Meaning |
|---|---|---|
| `NEW_SLICE_REQUIRED` | 22 | Genuinely missing backend, no policy blocker |
| `ALREADY_WIRED` | 16 | Real data end-to-end already (11 from before W7.5, plus none newly closed at this checkpoint) |
| `PARTIAL_WIRING_PENDING` | 10 | Core real, specific fields/sub-features fixture-backed |
| `WIRE_EXISTING_API_PENDING` | 5 | Backend ready, frontend call not yet written |
| `POLICY_BLOCKED` | 4 | Genuine PM/product decision required, not just unbuilt |
| `CLIENT_ONLY_ASSUMED` | 4 | Disclosed assumption: kept client-only (localStorage), reversible |
| `NO_CHANGE_REQUIRED` | 2 | Pure navigation or static content, fixture is correct long-term |
| `FRONTEND_ADAPTER_REQUIRED` | 1 | `1a-1`, deliberately parked since W7.3 |

## 6. Backend capability summary (what already exists)

Rich, real, Account-native (family-scoped) capability:

- **Family/RBAC** (`family` domain): family CRUD, members, roles,
  permissions, service subscriptions. No invite-acceptance flow.
- **Markpoint** (`markpoint_target`, `markpoint_access`): missions (create/
  submit/approve/reverse/reject/cancel/expire), recurring templates, ledger
  adjustments/corrections, per-family cycle config, activation requests/
  restrictions/service-admins, and a full `/api/me/markpoint/*` self-service
  surface (balance, level, weekly, projection, deduction history).
- **Wagle** (`wagle`, realtime): rooms, participants, messages, read-state,
  service-actor relay, WebSocket realtime, resume/catch-up, Web Push
  subscriptions, device PIN lock.

Real but **Legacy** (player/admin JWT, not Account-native, still backing
the existing AdminDashboard views that stay `KEEP_EXISTING_AS_CANONICAL`):
`admin` aggregator, `mission`, `daily_point`, `deduction`, `level_tier`,
`mission_template`, `cheer`, `feedback`, `notification`, `login_log`,
`player`, `chat`, `config`.

**Confirmed zero backend capability anywhere** (grep-verified, not
assumed): schedule/calendar, album/photo, todo, family-rules (distinct from
RBAC), cross-entity search, reward catalog, family board/post, file/message
attachments, per-account notification preferences, account deletion.

## 7. Notable findings from Phase 0 itself

- **`2t` (관리자 알림 발송) was misclassified as a gap in W7.4.** Its own
  container comment said "no send API exists yet," but
  `POST /api/admin/notifications` is real, already exists, and matches the
  screen's form fields exactly. This is a pure frontend-wiring quick win
  with zero backend work — not trusting a prior classification and checking
  the actual code again paid off, same as `3j` and `2m` did in W7.4.
- **Four screens (`2f`, `2w`, `2p`, `3i`) share one underlying policy gap**:
  the backend has no self-service, invitee-initiated "join a family" flow
  at all — only FamilyAdmin-initiated provisioning (parent creates an
  Account, hands over a one-time password out-of-band). The frontend
  screens assume the opposite direction (a member requests, a parent
  approves; or an invite code, entered by the joiner). Recommending these
  four be resolved together as one "family invitation model" PM decision
  rather than four separate ones.
- **Three screens (`1l`, `2h`, `2j`) share one reward-catalog gap.** The
  point-debit side already works via the existing ledger-adjustment
  endpoint; only a `Reward` catalog aggregate (name/cost/availability) is
  missing. Recommending it be built once, not three times.
- **Album/photo upload (`2v`) and avatar upload (`2z`) share a genuine
  infra gap, not just missing CRUD**: no storage abstraction (local disk vs.
  S3-compatible object storage, size/type limits, serving strategy) exists
  anywhere in `backend/app`. Flagged as `POLICY_REQUIRED` for the binary-
  upload path specifically, distinct from ordinary `API_MISSING` metadata
  CRUD, which has no such blocker.
- **`1t`'s per-room mute setting is `D6-P2`**, a policy item already
  registered in `active.md` as `DEFERRED_TO_RELEVANT_TASK_START_GATE` before
  this task even began — correctly inherited as `POLICY_REQUIRED`/
  `HUMAN_GATE`, not re-litigated.
- **Legacy `/api/notifications` is not safely reusable** for the
  Account-native `1n` screen: it is `player_id`-scoped via
  `LegacyIdentityMapping`, which the frozen D8 decision explicitly excludes
  for new Account-native users (no legacy identity import). Needs its own
  Account-native notification-list slice.
- **Client-only assumptions, disclosed rather than silently chosen**:
  `3f`/`3g`/`3k`/`3l` (language, theme, widget layout, shortcuts) are kept
  as localStorage-only preferences for W7.5 — standard, reversible,
  low-risk defaults, not treated as PM-decision blockers the way `3h`
  (account deletion) or the invitation model genuinely are. Revisit only if
  cross-device sync becomes a stated requirement.

## 8. Next (Phase C onward)

Phase B closed clean: `PHASE_B_PROCESSING_COMPLETE = 6/6`, of which
`PHASE_B_FUNCTIONALLY_WIRED = 4/6` and `PHASE_B_HUMAN_GATE = 2/6` (`1u`/
`2s`, correctly found blocked on a real UI/backend contract mismatch —
4-digit Screen vs. 6-digit backend PIN requirement — rather than forced
through with a visual redesign, which is explicitly out of scope). `1t`
(Phase C's first row) has its member-list capability done, using the same
"add a missing display-name field" pattern `1q` needed — a real, recurring
gap shape across this codebase's list endpoints, not a one-off — while its
mute-toggle capability stays separately `POLICY_REQUIRED`/`HUMAN_GATE` on
`D6-P2`.

## 9. Phase C — complete (10/10 rows processed)

All 10 remaining Phase C rows (`1f`, `1k`, `1s`, `2c`, `2g`, `2o`, `2p`,
`2z`, `3b`, `3i`) reached a final, evidenced classification. As with Phase
B, **row-count-complete is not the same as functionally-wired** — 5 of the
10 surfaced a genuine gap that this task does not have the authority to
paper over, and are recorded as such rather than forced through:

| Row | Outcome | Why |
|---|---|---|
| `1s` | `WIRED_AND_VERIFIED` | `rejection_reason` already existed on `markpoint_missions`, never exposed on `MissionOut` — schema-only fix, same shape as `1q`/`1t`. New `reviewer_display_name` resolved the same cross-domain way as `1t`'s participant name. |
| `2g` | `WIRED_AND_VERIFIED` | `reply_to_message_id` already existed on `wagle_messages`, never exposed. Design finding: the frozen overlay's own compose bar has no real input, so real typing was routed through the room's always-real composer instead — not a redesign of the frozen screen, a different orchestration of it. |
| `1f` | `SCREEN_PARTIALLY_COMPLETE` | Core profile/level/points/family-meta wired real. Streak and badge stats have no backing data model anywhere (grep-confirmed) — disclosed fixture values, reclassified `NEW_SLICE_REQUIRED`, not fabricated. |
| `1k` | `SCREEN_PARTIALLY_COMPLETE` | Description and checklist are new additive fields (migration `0012`), checklist is real and interactively toggleable. Photo-evidence submission stays `POLICY_REQUIRED` — same storage-infra gate as `2v`/`2z`'s avatar half, not a new blocker. |
| `2c` | `NO_CHANGE_REQUIRED` (reclassified from `PARTIAL_WIRING_PENDING`) | No level-up bonus mechanic exists anywhere in the Ledger/mission pipeline. `bonusPoints: 0` is a disclosed absence; inventing an award amount/trigger would be a real economy business-rule decision, flagged for PM, not built silently. |
| `2z` | `SCREEN_PARTIALLY_COMPLETE` | Read side wired real (`PATCH /api/me` + self-service `PATCH .../members/me` both built and tested). **Write side blocked on a design gap, not a backend gap**: the frozen canonical Screen renders every field as non-editable text with no color-swatch click handler — there is nothing on-screen to submit a changed value from. |
| `3b` | `DESIGN_CONTRACT_GAP` (new status value) | Backend fit-check done and confirmed ready (`cycle-progress`/`weekly-summary` both support real period filtering). The frozen Screen's `<select>`s each have exactly one hardcoded option and `onApply` takes no arguments — no input exists to wire to a real filter call. |
| `2o` | `DESIGN_CONTRACT_MISMATCH` | The legacy admin surface (`require_admin`, platform-wide, no Family concept) and the family-scoped Account-native config endpoint are two authorization systems that cannot present the same credential. Bridging them is a new authorization-bridge feature requiring a PM decision, not a wiring gap — same discipline as `1u`/`2s`'s PIN mismatch. |
| `2p` | `POLICY_BLOCKED` (reclassified, corrected from this task's own earlier optimistic Phase 0 framing) | The screen's `Invitation` type is keyed on `email`; D2 already excludes email/phone from the Account-native credential model entirely (grep-confirmed). Not a metadata gap on top of a workable list — the screen's data shape assumes an invite model D2 already ruled out. Folded into the same `POLICY-FAMILY-INVITATION-MODEL` decision as `2f`/`2w`. |
| `3i` | `POLICY_BLOCKED` (confirmed, no change) | Cancel semantics cannot be built before the invitation model itself is decided. |

**New Matrix columns** (`CAPABILITY_ID`, `CAPABILITY_STATUS`,
`POLICY_DEPENDENCY`), added per PM direction after Phase B: a Screen-level
status is never allowed to collapse a per-capability gap out of view again
(the pattern `1t` first exposed). Every row above with more than one real
outcome (`1f`, `1k`, `2z`) carries its capabilities split explicitly rather
than one blended `FINAL_W7_5_STATUS`.

**Backend changes this phase**, all additive, one migration
(`0012_profile_mission_fields`, kept ≤32 chars per `0011`'s own documented
`alembic_version.version_num` trap): `accounts.bio`/`birthday`/
`avatar_color` (nullable), `markpoint_missions.description` (nullable
Text) and `.checklist` (nullable JSONB). No existing column altered, no
backfill. New endpoints: `PATCH /api/me`, `PATCH
/api/families/{family_id}/members/me`, `PATCH
/api/families/{family_id}/markpoint/missions/{id}/checklist`. `MissionOut`
gained a `mission_out()` async builder (same cross-domain-resolve shape as
`1t`'s `participant_out`) used at every mission-returning endpoint, so
`reviewer_display_name` is never silently `None` because a route forgot to
resolve it.

**Test evidence**: 15 new backend tests
(`backend/tests/test_w75_phase_c_extensions.py`) covering `PATCH /api/me`,
self-service relationship update (including the cross-family-403 and
unknown-code-422 boundaries), mission description/checklist/
rejection_reason/reviewer-name exposure, checklist-toggle authorization
(wrong assignee, post-submission), and Wagle reply-to (including the
cross-room-forgery-rejection boundary) — all passed against a freshly
migrated disposable Postgres. 4 new Playwright cases added to the
**permanent** `tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts` (`1f`,
`1k`, `2g`; `1s` intentionally not duplicated at the E2E layer since its
real fields are already HTTP-covered) — all passed against an isolated
disposable stack (Postgres on 15435, throwaway backend on 18099, a
second throwaway Vite dev server on 5199 proxying to it, none of them the
persistent dev runtime). Full backend suite re-run clean except one
**pre-existing, unrelated** failure
(`test_wagle_service_binding.py::test_01_user_jwt_blocked_from_service_ingress`,
a `bcrypt`-72-byte-limit crash when a legacy JWT is presented as a service
credential secret) — confirmed pre-existing via `git stash` against clean
HEAD before this task touched anything, not a regression this task
introduced or is in scope to fix.

## 10. Phase D — 10 of 11 Slices built (19 of 19 candidate screens processed)

Mapping built before any code, per PM direction:
`engineering/phase2/MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md` (`SCREEN_ID →
CAPABILITY → BACKEND_DOMAIN → BACKEND_SLICE_ID → QUERY/COMMAND →
SHARED_CONSUMER_SCREENS`), so a Slice shared by several screens is built
once, not once per screen. Execution order followed that mapping's own
plan exactly.

| Slice | Screens | Migration | Outcome |
|---|---|---|---|
| `SLICE-TODO` | `1i` | `0013` | List/toggle real; create blocked (no input on frozen Screen) |
| `SLICE-FAMILY-RULES` | `1v` | `0014` | Read real; write blocked (no input) |
| `SLICE-NOTIFICATION-PREFERENCES` | `2n` | `0015` | Fully real |
| `SLICE-SCHEDULE` | `1g`, `1o`, `2u` (`3a` out of scope) | `0016` | Fully real |
| `SLICE-ALBUM-METADATA` | `1h`, `1p`, `1w`, `2y` | `0017` | Real except `2y`'s write (no input) and `1p`'s image (storage-infra gate) |
| `SLICE-REWARD-CATALOG` | `1l`, `2h`, `2j` | `0018` | Fully real |
| `SLICE-NOTIFICATION-LIST` | `1n` | `0019` | Fully real (no producer route yet — disclosed, not a gap in this Slice's own scope) |
| `SLICE-FAMILY-ACTIVITY-LOG` | `2r` | none (reads `MarkpointAuditEvent`) | Fully real |
| `REUSE-WAGLE-ROOMS-AS-BOARD` | `3c`, `3d` | none (reuses Wagle) | Fully real, live-verified in a real browser |
| `SLICE-SEARCH` | `3j` | none (reads Missions + Wagle) | Backend real and tested; frontend blocked (no query input exists anywhere in this Screen's own chain) |
| `SLICE-WAGLE-ATTACHMENTS` | `2b` | — | **Not built** — `POLICY_REQUIRED`, same storage-infra gate as `2v`/`1p`/`2z` |

**A repeating pattern across this phase, worth naming once rather than
per-row**: five rows (`1i`, `1v`, `2y`, `2z` from Phase C, `3b` from
Phase C, `3j`) hit the exact same shape — the real backend endpoint was
built, tested, and works, but the **frozen canonical Screen has no input
control to drive it from** (a static `<span>` instead of an `<input>`, a
button with no form behind it, a `<label>` with no click handler). This is
not a missing-wiring gap this task can close; it needs a PM/design
decision to add real inputs to those specific frozen Screens. Recording
it once here rather than treating each occurrence as a surprise.

**New design decisions made without a schema change, worth carrying
forward**: (1) `markpoint_target.service.self_spend` — a member spending
their own points needs `require_access` only, never `POINTS_ADJUST` (an
admin-only permission no child holds); reusing `adjust_points` would have
required granting redemption authority no design intends a child to have.
(2) The Wagle board reuses one `WagleRoom` per Family (sentinel title) and
encodes `[category] title\nsummary` into a plain message body — zero
schema change, and comments reuse `2g`'s `reply_to_message_id` directly
rather than a second reply concept.

**Test evidence**: 34 new backend tests across all 10 built Slices
(`backend/tests/test_w75_phase_d_slices.py`), full backend suite clean
except the same pre-existing `test_01_user_jwt_blocked_from_service_ingress`
failure carried from Phase C (unrelated, not fixed here). `3c`/`3d` were
additionally live-verified in a real Chromium session via Playwright
against the isolated stack (real HTTP-created post rendered, opened, a
real comment submitted through the Screen's own input and rendered in the
thread) — not just typechecked.

**Isolated environment, same discipline as Phase B/C**: disposable
`postgres:16.9-alpine` (port 15435), throwaway backend (port 18099), a
second throwaway Vite dev server (port 5199) — none the persistent dev
runtime. All migrations `0013`→`0019` applied clean.

## 11. What remains after Phase D

- `2b` (`SLICE-WAGLE-ATTACHMENTS`) — not built, `POLICY_REQUIRED` on the
  storage-infra gate.
- `3e` (`SLICE-WAGLE-BOARD-REACTIONS`) — not built, `NEW_SLICE_REQUIRED`;
  its own precondition (3c/3d landing) is now satisfied for a future pass.
- The repeating missing-input-control gap named in §10 (`1i`, `1v`, `2y`,
  `2z`, `3b`, `3j`) needs a PM/design decision before those Screens'
  already-real, already-tested write/read paths can be used.
- All prior Phase B/C policy/design gates remain open exactly as before:
  `3h`, `2f`/`2w`/`2p`/`3i`, `1t`'s D6-P2 mute half, `1u`/`2s`'s PIN-digit
  mismatch, `2o`'s legacy-admin/family-scope authorization bridge.
- Backend-suite `KNOWN_CONDITION` (non-deterministic Wagle concurrency
  contention) remains registered in `COVERAGE_MAP.md`; stabilizing the
  actual contention is still separate, not-yet-scheduled work.
- Independent QA per `.claude/agents/test-agent.md` — not started for any
  phase of this task.

## 12. Phase E/F — scope reconciliation, `3e` resolution, closeout-readiness pass

Full detail lives in `engineering/phase2/MONGLE_W7_5_PM_DECISION_PACKAGE.md`
(the primary deliverable of this pass) and in
`agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md`'s own "Phase
E" and "Phase F" sections (raw evidence trail). Summarized here so this
report's own numbers stay current rather than frozen at §11:

- **§11's `3e` entry above is now stale and superseded**: `3e`
  (`SLICE-WAGLE-BOARD-REACTIONS`) was investigated, found to be
  `IMPLEMENTATION_REQUIRED` rather than a genuine PM policy question (both
  `3c` and `3e`'s frozen canonical Screens already render `♥ likes · 💬
  comments` as a designed-for element), and was built: migration
  `0020_wagle_message_reactions`, toggle-reaction service/router
  endpoints, real counts wired into both the board post list and the
  ranked Popular Posts list. 8 new backend tests, all pass. The reaction
  *toggle* itself still has no click target in either frozen Screen's own
  type contract — that specific gap is `DESIGN_CONTRACT_REQUIRED` and is
  tracked as a canonical PM gate, not silently left undone.
- **Phase B/C/D counts reconciled against live source**, not re-asserted
  from memory: Phase B confirmed correct (no defect). Phase C recounted to
  a corrected 11/11 (a prior tally line had summed to 10 by arithmetic
  slip). Phase D's 21-screen/11-Slice scope (§0 above) confirmed to have
  been the true scope from the start — no phantom 20th/22nd screen or 12th
  Slice was ever discovered; an earlier "19 screens" shorthand in some
  summaries was imprecise, not a real scope gap.
- **A real data-loss defect in the Matrix CSV was found and fixed**: the
  `API_READINESS` field for `1q`/`1u`/`2s` had been overwritten in place
  during Phase B reclassification, losing the original Phase-0 value. A
  new `ORIGINAL_API_READINESS` column now preserves both values.
- **Two taxonomy mislabels corrected**: `1f`'s streak/badge sub-capabilities
  were `NEW_SLICE_REQUIRED` (implies "just unbuilt code") when they are
  genuinely undefined game-mechanic questions — corrected to
  `POLICY_REQUIRED`. `2b`'s `FINAL_W7_5_STATUS` field still literally read
  `NEW_SLICE_REQUIRED` from the original Phase 0 pass despite every other
  reference correctly saying `POLICY_BLOCKED` — corrected for consistency.
- **The "14 PM gates" figure was a miscount**: `active.md` said "14 total"
  while literally naming 17 distinct screen-level flags. Reconciled to 17
  raw flags consolidating into 13 canonical decisions (the family-invitation
  model folds `2f`/`2w`/`2p`/`3i` into one gate; the PIN-digit mismatch
  folds `1u`/`2s` into one gate). Full 13-gate Decision-Package-grade table,
  plus `2b`'s own 16-field/4-option storage-infrastructure Decision
  Package, is in the PM Decision Package document (§4/§5).
- **A frontend fixture-fallback-on-error audit found and fixed 6 real
  defects** present since as early as Phase B (`FamilyMembersPage.tsx`,
  `FamilyTodoPage.tsx`, `FamilyRulesPage.tsx`, `FamilySchedulePage.tsx`,
  `FamilyAlbumPage.tsx`, `ProfilePage.tsx`) — each fell back to its entire
  fixture dataset (fake names/todos/rules/events/albums/profile) on a
  genuine API load failure instead of a real empty state plus a real error
  message. All six fixed; `tsc --noEmit`/`eslint`/`vite build` clean after.
- **The permanent `3c`/`3d`/`3e` Playwright spec
  (`tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts`) was actually run,
  not just committed**: its first execution failed (`page.goBack()` doesn't
  return to `WagleBoardPage.tsx`'s in-component board view, since that view
  is local `useState`, not a route) — a real test defect, fixed by using
  the comment composer's own back control instead. Re-seeding for the
  re-run exposed a second, independent, real defect in
  `backend/scripts/phase1_seed_synthetic.py` (FK delete-order violation
  once a real Wagle message existed in that seed DB for the first time) —
  fixed by reordering the cleanup list. Neither fix touched product code.
  Re-run: 1/1 pass, full real flow (sign-in → post → reload → comment →
  reaction → back-navigation → Popular ranking) verified end to end.
- **Full backend suite, cleanest run of the task**: 374 passed, 1 failed
  (pre-existing, unrelated `bcrypt` 72-byte crash in
  `test_wagle_service_binding.py`, confirmed pre-existing via `git blame`),
  0 errors. Backend-suite `KNOWN_CONDITION` (Wagle concurrency
  non-determinism, §11) remains formally registered in `COVERAGE_MAP.md`
  and is unaffected by this checkpoint's own work.
- **Closeout-readiness verdict for this pass**: `CONDITIONAL` /
  `HUMAN_GATE` combination — not a plain `PASS`. All resolvable
  implementation for this pass is complete; what remains is exclusively
  genuine PM/design decisions (the 13 canonical gates plus `2b`'s storage
  Decision Package) and Independent QA, which has deliberately not been
  started yet per this task's own instructions. See the PM Decision
  Package's §7 readiness statement for the exact boolean breakdown.

## 13. Phase G — migration downgrade full verification; `1n`'s completeness claim corrected

Two closeout checks completed after §12: (1) the full `0012`→`0020`
migration downgrade chain was verified against a dedicated throwaway DB —
every migration has a real, non-stub `downgrade()`, a fresh-DB
upgrade→downgrade-to-`0011`→re-upgrade round trip is clean, and 3
representative table/column changes were confirmed via direct schema
inspection, not just exit codes. (2) A broader frontend functional-state
audit (loading/error/permission-denied/mutation-pending/mutation-failure/
retry, beyond the fixture-fallback pattern already fixed) found and fixed
6 more real defects, and — more significantly — found that
`NotificationsPage.tsx` (`1n`) had never actually been wired to its own
real, already-built, already-tested backend: this directly contradicts
§10's own "Fully real end-to-end" listing of `1n`. Now fixed, real end to
end. Full detail in the QA evidence "Phase G" section; this is a
correction to a completeness claim, not a scope or count change — `1n`
was already counted as wired in the Matrix.

## 14. Phase H — Final Pre-Independent-QA Reconciliation and Evidence Freeze

Full detail: QA evidence "Phase H" section. Summary of what changed
relative to every number this report stated through §13:

- **The "13 canonical gates" figure itself had a defect**: §12/§4 of the
  PM Decision Package had folded `GATE-2B` (Wagle attachment storage, an
  infrastructure question with no product-policy content) into "13
  canonical decisions." Corrected: **13 PM/design gates + 1 separate
  infrastructure gate = 14 total decision items.** To keep the PM/design
  total at 13 without `GATE-2B`, the previously-narrated-but-ungated
  reaction-toggle click-target gap (`3c`/`3e`) is now its own canonical
  gate, `GATE-3E-REACTION-TOGGLE`.
- **Phase D's "10 of 11 Slices built" was correct, but a later summary
  drifted to a self-contradicting "11/11 complete... `2b` correctly not
  built."** Corrected framing, verified fresh by directory existence:
  `PHASE_D_TOTAL_SLICES_ORIGINAL_SCOPE=11` (declared from the start,
  including `2b`), `CODE-IMPLEMENTABLE_SLICES_COMPLETE=10/10`,
  `INFRASTRUCTURE-BLOCKED_SLICE=1` (`2b`, inside the 11, never a phantom
  12th).
- **The pre-existing `bcrypt` backend failure (§7, §9, §13 all cited it as
  pre-existing/unrelated/out of scope) was investigated and safely
  fixed.** Root cause: `get_current_service_principal` called
  `bcrypt.checkpw` on a legacy-JWT-shaped secret routinely over bcrypt's
  72-byte hard limit, raising an unhandled `ValueError` instead of a plain
  401. Fixed with a 3-line length guard in `wagle/service_actor.py` —
  verified against all 6 required safety conditions (no policy/auth-
  contract/migration change, backward compatible, no security regression,
  Backend-Guide-conformant) before touching it. **Backend suite is now
  genuinely 375/375, 0 failed, 0 errors** — re-verified twice (once
  immediately after this fix, once again after the boundary fix below),
  not merely once.
- **The Playwright `2t` skip (§9, §13) is resolved**: 10/10 passed, 0
  skipped, using a synthetic, disposable-only credential created directly
  in a throwaway DB (same precedent this task's own Phase B section
  already used for `2t`'s API-level check) — never a genuine
  `ENVIRONMENT_REQUIRED` condition.
- **A genuine Backend Guide boundary gap found and fixed**:
  `family_activity_log` and `family_search` queried another domain's ORM
  model directly instead of through that domain's own dotted-reference
  service function. Fixed by adding 3 read-only functions to
  `markpoint_target/service.py` and `wagle/service.py` and updating the 2
  call sites — identical queries, zero behavior change, verified by the 9
  directly-affected tests plus a full-suite re-run (375/375, 0
  regressions).
- **One more real fixture-fallback defect found and fixed**:
  `ProfilePage.tsx`'s 4 secondary stat fetches (level/balance/mission-
  count/member-count) silently swallowed failures with no error state,
  letting `toMyProfileModel`'s fixture fallback render fake numbers (Lv.3,
  320P, etc.) indistinguishably from a genuine failure. Fixed to render a
  real "unavailable" indicator instead, for both the loading-flicker and
  the confirmed-failure case. Two look-alike candidates elsewhere
  (`MarkpointUser.tsx`'s reward-overlay balance, `FamilyAlbumPage.tsx`'s
  photo like/comment counts) were reviewed and confirmed **not** defects
  — the first is unreachable dead code given the component's own state
  machine, the second is an already-accepted disclosed-fixture-stat shape
  with no real backend concept to have failed in the first place.
- **Migration re-verification, deeper pass**: all 9 migrations
  (`0012`-`0020`) cross-checked column-by-column against their model
  files — zero drift found on any field, FK, constraint, or index.
- Full verification suite re-run clean: backend 375/375, permanent E2E
  spec 10/10 (0 skipped), `tsc --noEmit`/`eslint`/`vite build` all clean,
  `agent-system/tools/check_all.py` shows no W7.5-specific warning,
  `git diff --check` clean.
- **Verdict for this checkpoint**: `IMPLEMENTATION_EVIDENCE_FROZEN` /
  `READY_FOR_PM_REVIEW` / `READY_FOR_INDEPENDENT_QA` — not
  `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`. The 13 PM/design gates and
  1 infrastructure gate remain genuine, open, PM-owned decisions; every
  currently code-resolvable item has now been resolved and re-verified.
