# MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001 — PM Decision Package

Produced during a scope-reconciliation pass over the existing W7.5 work.
This document is the authority for "what still needs a PM/design decision"
— `agent-system/active.md` and the Matrix CSV point here rather than
repeating the full text of each item.

## 0. Why this document exists

A prior checkpoint's own summary lines undercounted and overcounted in
several places (Phase C's own arithmetic said "10" while listing entries
that summed to 11; `active.md` said "14 total" gates while literally
naming 17 distinct screen IDs). None of the underlying work was wrong —
every number below was re-derived directly from the current Matrix CSV,
current source, and current test runs, not from the prior summary prose.
Where a prior count was wrong, this document states the corrected count
and traces exactly which items it comprises, rather than quietly fixing
the number.

## 1. Phase-level reconciliation

### Phase B — reconciled, no defect found

```text
Phase B total: 6  (1a-1, 1r, 1q, 2t, 1u, 2s)
Functionally wired: 4  (1a-1, 1r, 1q, 2t)
Human Gate: 2  (1u, 2s)
Duplicate: 0
Omitted: 0
```

Re-verified this pass, not merely re-asserted:
- `frontend/src/screens/family/PinChange/PinChangeScreen.tsx` — confirmed
  the digit input is still hard-capped at 4 (`.slice(0, 4)`), local-state
  only, no API call anywhere in the file.
- `frontend/src/features/family-onboarding/OnboardingFlowPage.tsx`'s `2s`
  branch — confirmed unchanged, same local-only flow.
- `backend/app/config.py` — confirmed `WAGLE_PIN_LENGTH: int = 6` is
  still the live value; `backend/app/domains/wagle/device_pin_service.py`
  still rejects any non-6-digit PIN with `PIN은 숫자 {expected}자리여야
  합니다`.

Verdict: `1u`/`2s` remain correctly `HUMAN_GATE` (`DESIGN_CONTRACT_REQUIRED`
in this document's taxonomy — see §4). This is not an implementation gap;
building a 6-digit UI on these Screens would be a W7.3 visual-baseline
redesign, explicitly out of this task's authority to perform unilaterally.

### Phase C — reconciled, 11/11, zero omissions

The prior checkpoint's own tally line ("fully wired: 3, capability-split:
3, reclassified: 1, new design-contract gaps: 2, policy reclassification:
1" = 10) undercounted by one row. Re-derived directly from the Matrix CSV
for all 11 rows:

| Screen | Category | Detail |
| --- | --- | --- |
| `1t` | CAPABILITY_SPLIT | member-list `WIRED_AND_VERIFIED`; mute-toggle `POLICY_REQUIRED` (D6-P2) |
| `1f` | CAPABILITY_SPLIT | core profile `WIRED_AND_VERIFIED`; streak/badge stats `POLICY_REQUIRED` (see §4, GATE-STREAK-BADGE — newly corrected this pass, previously mislabeled `NEW_SLICE_REQUIRED`) |
| `1k` | CAPABILITY_SPLIT | description/checklist `WIRED_AND_VERIFIED`; photo evidence `POLICY_REQUIRED` (storage infra) |
| `1s` | FULLY_WIRED | — |
| `2c` | RECLASSIFIED_NO_CHANGE_NEEDED | no level-up bonus mechanic exists anywhere; disclosed `0`, not fabricated |
| `2g` | FULLY_WIRED | — |
| `2o` | DESIGN_CONTRACT_REQUIRED | legacy-admin/family-scope authorization bridge (see §4, GATE-2O) |
| `2p` | POLICY_REQUIRED | folds into GATE-INVITE (see §4) |
| `2z` | CAPABILITY_SPLIT | read `WIRED_AND_VERIFIED`; write `DESIGN_CONTRACT_REQUIRED` (see §4, GATE-2Z-INPUT); avatar upload `POLICY_REQUIRED` (storage infra) |
| `3b` | DESIGN_CONTRACT_REQUIRED | folds into GATE-3B-INPUT (see §4) |
| `3i` | POLICY_REQUIRED | folds into GATE-INVITE (see §4) |

```text
Phase C total rows: 11
Classified: 11
Duplicate: 0
Omitted: 0
```

### Phase D — reconciled

The Phase D Slice Mapping document
(`engineering/phase2/MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md`) declared **11
Slices and 21 screens from the very start**, before any Phase D code was
written — including `SLICE-WAGLE-ATTACHMENTS` (`2b`) and
`SLICE-WAGLE-BOARD-REACTIONS` (`3e`) in that original 11. A later
checkpoint's shorthand ("19 candidate screens") only counted the 19
`CREATE_NEW_VERTICAL_SLICE` rows and silently dropped the 2
`REUSE_EXISTING_PRODUCT_LOGIC` rows (`3c`/`3d`) that the same Mapping
document's own header already totals in ("21 screens total"). There is no
newly discovered 12th Slice or 20th/22nd screen — the apparent mismatch
was an imprecise later summary, not a scope change. Re-derived directly
from the Matrix CSV and the Mapping document:

```text
ORIGINAL_SLICE_COUNT: 11
NEWLY_DISCOVERED_SLICE_COUNT: 0
EFFECTIVE_SLICE_COUNT: 11
BUILT_SLICE_COUNT: 10  (all except SLICE-WAGLE-ATTACHMENTS)
PENDING_SLICE_COUNT: 1  (SLICE-WAGLE-ATTACHMENTS / 2b)
POLICY_BLOCKED_SLICE_COUNT: 1  (SLICE-WAGLE-ATTACHMENTS / 2b)
IMPLEMENTATION_REQUIRED_SLICE_COUNT: 0

ORIGINAL_SCREEN_COUNT: 21  (19 CREATE_NEW_VERTICAL_SLICE + 2 REUSE_EXISTING_PRODUCT_LOGIC)
NEWLY_DISCOVERED_SCREEN_COUNT: 0
EFFECTIVE_SCREEN_COUNT: 21
```

**`SLICE-WAGLE-BOARD-REACTIONS` (`3e`) was resolved during this
reconciliation pass, not deferred.** Investigation found the reaction
concept was already fully determined by the existing frozen Screens
themselves — both `3c` and `3e` already render `♥ likes · 💬 comments` as
a core visual element — so this was `IMPLEMENTATION_REQUIRED`, not a PM
policy question. Built this session: migration `0020_wagle_message_
reactions`, toggle service/router, `GET .../wagle/board/popular` real
ranking (reaction_count + comment_count within week/month/all, matching
the Screen's own range labels exactly), 8 new backend tests, real counts
wired into `3c`'s post list and `3e`'s ranked list. The reaction *toggle*
itself has no click target in either frozen canonical Screen (`3c`'s
`FamilyBoardProps` and `3e`'s `PopularPostsProps` both lack any
like/react callback) — folds into the same missing-input-control shape
as the six items in §4, but is not counted as a 7th duplicate there since
its backend is materially further along (fully built and tested, not
just planned).

Effective Phase D screen classification (21/21, exhaustive, non-overlapping):

| Category | Count | Screens |
| --- | --- | --- |
| `FULLY_WIRED` | 13 | `2n`, `1g`, `1o`, `2u`, `1h`, `1w`, `1l`, `2h`, `2j`, `1n`, `2r`, `3c`, `3d` |
| `BACKEND_READY_FRONTEND_DESIGN_REQUIRED` | 5 | `1i`, `1v`, `2y`, `3e` (toggle only), `3j` |
| `INFRASTRUCTURE_REQUIRED` | 2 | `1p` (image half), `2b` |
| `EXTERNAL_INTEGRATION_REQUIRED` (disclosed 7th category — Section 6 named 6 buckets, none fit `3a`'s actual shape; forcing it into one would misrepresent it) | 1 | `3a` |
| `POLICY_REQUIRED` | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `NO_BACKEND_REQUIRED` | 0 | — |

```text
Effective Screen Count: 21
Sum of categories: 13 + 5 + 2 + 1 = 21
Duplicate: 0
Omitted: 0
```

`3a` (가족 캘린더 공유): Google/Apple Calendar sync and a webcal
subscription link require real external-service OAuth credentials and a
feed-generation integration this repository has never held and this task
has no authority to provision. This is categorically different from a
storage-infra decision (`2b`, `1p`'s image half) — no in-house engineering
choice resolves it, only an external-service integration decision (which
provider, whose developer account, what scopes) that itself depends on a
product decision (is external calendar sync a committed feature at all).

## 2. API_READINESS drift, corrected

The Matrix's `API_READINESS` field was overwritten in place for 3 rows
during Phase B/C reclassification, losing the original Phase-0-time value.
**Fixed this pass**: a new `ORIGINAL_API_READINESS` column now sits beside
`API_READINESS` in the Matrix CSV, preserving both.

```text
                              ORIGINAL   CURRENT
API_MISSING                      22         22
EXISTING_API_READY               21         19
API_PARTIAL                      10         11
POLICY_REQUIRED                   4          6
NO_BACKEND_REQUIRED               6          6
FRONTEND_ADAPTER_REQUIRED         1          0
                                 ---        ---
                                  64         64
```

Every delta traces to an already-disclosed, already-narrated correction
(no new finding):
- `1q`: `EXISTING_API_READY` → `API_PARTIAL` (the `MembershipSummary`
  display-name gap found mid-Phase-B).
- `1u`: `EXISTING_API_READY` → `POLICY_REQUIRED` (PIN-digit mismatch found).
- `2s`: `FRONTEND_ADAPTER_REQUIRED` → `POLICY_REQUIRED` (same PIN-digit
  mismatch, shared reuse target).

## 3. Resolved work this pass

| Item | Was | Now | Evidence |
| --- | --- | --- | --- |
| `3e` (Board Reactions) | `NEW_SLICE_REQUIRED` (implied nothing buildable) | `SCREEN_PARTIALLY_COMPLETE` — read/ranking `WIRED_AND_VERIFIED`, toggle `API_READY_UI_BLOCKED` | Migration `0020`, 8 new backend tests, real counts wired into `3c`/`3e` |
| `1u`/`2s` (Phase B) | Recheck requested | Confirmed still correctly `HUMAN_GATE`, re-verified against live source (config + service code), not just re-asserted | See §1 |
| Phase C row count | Miscounted 10/11 in a prior summary | Corrected 11/11 table, §1 | Matrix CSV re-derivation |
| `API_READINESS` original values | Overwritten, unrecoverable from the CSV alone | Restored as `ORIGINAL_API_READINESS`, both values now visible | §2 |
| `1f` streak/badge sub-capabilities | Mislabeled `NEW_SLICE_REQUIRED` (implies "just unbuilt") | Corrected to `POLICY_REQUIRED` (see GATE-STREAK-BADGE, §4) — genuinely undefined game-mechanic questions, same shape as `2c`'s level-up-bonus finding | Matrix CSV corrected this pass |
| `2b` `FINAL_W7_5_STATUS` field | Still literally read `NEW_SLICE_REQUIRED` from the original Phase 0 pass, inconsistent with its own `POLICY_BLOCKED` narrative everywhere else | Corrected to `POLICY_BLOCKED` for internal consistency | Matrix CSV corrected this pass |

No implementation was deferred to this document that could have been
completed instead — see §5 for the explicit non-deferral statement.

## 4. PM/Design Decision Gates — reconciled to 13 canonical decisions + 1 separate infrastructure gate

**Correction made this pass**: an earlier version of this section's own
table listed `GATE-2B` as one of "13 canonical decisions", conflating a
`POLICY_REQUIRED`/`DESIGN_CONTRACT_REQUIRED` product decision with a
distinct `INFRASTRUCTURE_DECISION_REQUIRED` decision. They are not the
same kind of gate and must not share one denominator: a PM/design gate
asks "what should the product do"; `GATE-2B` asks "what storage backend do
we run", a question with no product-policy content of its own. Corrected
structure, verified against every raw screen-level flag this document is
aware of:

```text
FORMAL_PM_AND_DESIGN_GATES: 13
INFRASTRUCTURE_DECISION_GATE: 1  (GATE-2B, see §4.2 and §5 — not one of the 13)
TOTAL_UNRESOLVED_DECISION_ITEMS: 14
```

`agent-system/active.md` previously stated "14 total" while literally
naming 17 distinct screen IDs, and a later pass corrected that to "13"
without separating `GATE-2B` back out — both were imprecise. Ground truth:
**17 raw screen-level flags, consolidating to 13 canonical PM/design
decisions** (once genuine duplicates are merged) **plus 1 separate
infrastructure decision (`GATE-2B`)**, for 14 total open decision items.
This section is now the canonical register; `active.md` points here.

### 4.1 The 13 canonical PM/design gates

Each gate lists all 12 required fields.

---

**GATE-3H**
- TYPE: `POLICY_REQUIRED`
- RELATED_SCREEN_IDS: `3h`
- DECISION_QUESTION: Account-deletion scope, ownership transfer, message/ledger retention, soft-delete vs. anonymization, recovery window?
- CURRENT_IMPLEMENTATION: No deletion endpoint, service function, or policy exists anywhere (grep-confirmed again this pass: zero matches for a delete-account path in `backend/app/domains/family/` or `account_*`)
- WHY_BLOCKED: Deleting an Account touches ledger/message retention and family-ownership transfer, none of which has an approved rule
- RECOMMENDED_OPTION: Soft-delete + 30-day recovery window + family-ownership-transfer-required-first (lowest destructive risk)
- ALTERNATIVES: Hard delete; anonymize-in-place
- DEFAULT_IF_DEFERRED: No account deletion ships; `3h` stays fixture
- W7_5_IMPACT: Isolated — does not block a `CONDITIONAL` verdict
- POST_DECISION_IMPLEMENTATION_REQUIRED: New endpoint + service function + migration (soft-delete column or reuse existing `deleted_at` convention) + ownership-transfer precondition check
- TEST_IMPACT: New backend test file covering the chosen deletion/transfer/retention behavior; no existing test currently exercises this path

---

**GATE-INVITE**
- TYPE: `POLICY_REQUIRED`
- RELATED_SCREEN_IDS: `2f`, `2w`, `2p`, `3i`
- DECISION_QUESTION: Is a family "invitation" FamilyAdmin-provisions-only (current reality), or a real invitee-initiated request/accept flow? If the latter, what identity key, since D2 excludes email/phone?
- CURRENT_IMPLEMENTATION: Backend only supports FamilyAdmin-initiated provisioning (`member-accounts`); `2p`'s own `Invitation` type is keyed on `email`, a field that does not exist under D2's Account-native model
- WHY_BLOCKED: Building any of these 4 screens' UI would either misrepresent the current provisioning-only reality or require inventing an invitee-identity key D2 has not approved
- RECOMMENDED_OPTION: Keep FamilyAdmin-provisioning as the only model; redesign `2f`/`2w`/`2p`/`3i` to reflect it (no new invite flow)
- ALTERNATIVES: Build a real invitee-initiated flow keyed on username (new Slice, real scope)
- DEFAULT_IF_DEFERRED: All 4 screens stay fixture-shaped, contradicting the real backend model
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: If redesigned to match current reality — 4 screens' UI copy/flow change only, no backend work. If a new invite flow is approved — new Slice (invite table, accept endpoint, identity-key resolution)
- TEST_IMPACT: New backend + Playwright coverage only if the invite-flow alternative is chosen; the redesign-only option needs no new backend test

---

**GATE-PIN**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `1u`, `2s`
- DECISION_QUESTION: Redesign these 2 frozen Screens to 6 digits, or relax `WAGLE_PIN_LENGTH` to 4 for this UX?
- CURRENT_IMPLEMENTATION: `PinChangeScreen.tsx` still hard-caps input at 4 digits (`.slice(0, 4)`, local-state only, no API call); `backend/app/config.py` still sets `WAGLE_PIN_LENGTH: int = 6`; `device_pin_service.py` still rejects any non-6-digit PIN with a real HTTP 400 — all three re-confirmed against live source this pass, not re-asserted
- WHY_BLOCKED: Two frozen W7.3 canonical Screens render a 4-key/4-dot design; the real backend enforces 6 digits; no code change can reconcile a visual contract with a validation contract without changing one of them, which is a design/security decision, not an implementation gap
- RECOMMENDED_OPTION: Redesign the 2 Screens to 6 digits (preserves the already-security-reviewed 6-digit entropy)
- ALTERNATIVES: Relax backend to 4 digits (weakens the already-approved PIN entropy — not recommended)
- DEFAULT_IF_DEFERRED: Both Screens stay local-state-only; no real PIN change/setup ships
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: If redesigned to 6 digits — new W7.3-visual-baseline-approved layout for 2 Screens + wire to the already-real `device_pin_service` endpoints (no backend change needed, the API already exists and is tested). If backend relaxed to 4 — a migration-free config change plus a security re-review this task has no authority to approve unilaterally
- TEST_IMPACT: New Playwright case exercising a real PIN set/change once wired; the existing `device_pin_service` backend tests already cover the 6-digit contract and need no change

---

**GATE-D6P2** (pre-existing, not this task's discovery)
- TYPE: `POLICY_REQUIRED`
- RELATED_SCREEN_IDS: `1t` (mute half only — its member-list half is `WIRED_AND_VERIFIED`)
- DECISION_QUESTION: Room-level mute/notification-setting semantics — what does muting a Room actually suppress (push only? in-app badge too? both?), and is it per-device or per-Account?
- CURRENT_IMPLEMENTATION: No mute-state column or endpoint exists on `WagleRoom`/`WagleParticipant`; `1t`'s mute toggle is fixture-only
- WHY_BLOCKED: Already registered in `agent-system/active.md`'s own D6-P table (`D6-P2`, "Room별 mute 및 알림 설정") before this task began — this task inherited, did not discover, this gate, and has no standing to redefine a decision already assigned to its own owner
- RECOMMENDED_OPTION: Unchanged — defer to the existing D6-P2 owner
- ALTERNATIVES: — (not this task's call to propose)
- DEFAULT_IF_DEFERRED: Mute toggle stays unbuilt on `1t`
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New `is_muted`-shaped column/table + toggle endpoint + push-suppression check in the existing delivery path, once D6-P2 resolves
- TEST_IMPACT: New backend test for mute-state enforcement in the push/delivery path

---

**GATE-2O**
- TYPE: `DESIGN_CONTRACT_REQUIRED` (authorization-architecture)
- RELATED_SCREEN_IDS: `2o`
- DECISION_QUESTION: Should the legacy admin surface gain a family-selector to call the family-scoped `markpoint/config` endpoint, or does this wait for a future Account-native admin surface?
- CURRENT_IMPLEMENTATION: Two authorization systems confirmed unable to share a credential by direct source read: `require_admin` is platform-wide with no Family concept; the config endpoint is Account-native and family-scoped
- WHY_BLOCKED: Bridging the two is an authorization-architecture decision (widen legacy admin's authority surface vs. wait for a new surface), not a wiring task
- RECOMMENDED_OPTION: Defer to a future Account-native admin surface (avoids widening the legacy admin's authority surface)
- ALTERNATIVES: Add a family-selector bridge to the legacy admin surface now
- DEFAULT_IF_DEFERRED: `2o` stays fixture
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: If bridged now — a family-selector UI element + a legacy-admin-to-Account-native credential exchange path (security-sensitive, needs its own review). If deferred — no code change until the new admin surface exists
- TEST_IMPACT: New authorization-boundary test for whichever bridge mechanism is chosen (must prove the legacy admin credential cannot silently gain Account-native family-scoped power beyond what's explicitly granted)

---

**GATE-1I-INPUT**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `1i`
- DECISION_QUESTION: No create-todo form/screen exists anywhere in the 64-screen canonical set; `onAdd` has nowhere to navigate to. What fields (title/assignee/due-date), what layout?
- CURRENT_IMPLEMENTATION: `FamilyTodoScreen`'s own type contract confirmed this pass: `onAdd?: () => void` — no argument slot; no companion form Screen exists anywhere (re-verified via directory search)
- WHY_BLOCKED: Adding real inputs to a frozen canonical Screen's type contract is a visual/interaction design decision this task has no authority to make unilaterally
- RECOMMENDED_OPTION: A minimal bottom-sheet/modal (title + optional assignee + optional due date), matching `1o`'s (Schedule Add) already-approved form pattern
- ALTERNATIVES: A full new dedicated canonical Screen
- DEFAULT_IF_DEFERRED: List/toggle/delete stay real; create stays unreachable from the UI
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New modal/bottom-sheet component + `onAdd(title, assignee?, dueDate?)` signature change + wire to the already-real, already-tested `POST /api/families/{id}/todos` endpoint (no backend change needed)
- TEST_IMPACT: New Playwright case for real todo creation once the input exists; existing backend create-todo test already covers the API side

---

**GATE-1V-INPUT**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `1v`
- DECISION_QUESTION: No rule add/edit form exists; `onSave`/`onAddRule` take no arguments. What fields and layout?
- CURRENT_IMPLEMENTATION: `FamilyRulesProps` confirmed: no editable field, no argument on any callback; only a separate static guide Screen (`2q`) exists, not an editor
- WHY_BLOCKED: Same frozen-Screen-authority limit as GATE-1I-INPUT
- RECOMMENDED_OPTION: A category+label+value form reusing the whole-list-replace `PUT` already built
- ALTERNATIVES: Per-row inline edit instead of a form
- DEFAULT_IF_DEFERRED: Read stays real; write stays unreachable
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New form component + `onSave(rules)` signature change; the already-real, already-tested `PUT` endpoint needs no backend change
- TEST_IMPACT: New Playwright case for a real rule save once the input exists

---

**GATE-2Y-INPUT**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `2y`
- DECISION_QUESTION: No per-member toggle callback exists at all in the type contract. What interaction (checkbox row vs. multi-select)?
- CURRENT_IMPLEMENTATION: `AlbumShareSettingsProps` confirmed: only `onBack`/`onSave`, no per-member callback signature
- WHY_BLOCKED: Same frozen-Screen-authority limit
- RECOMMENDED_OPTION: Add an `onToggleMember(name: string)` callback + a real `<input type="checkbox">`/switch per row
- ALTERNATIVES: Redesign as a multi-select list with one confirm action
- DEFAULT_IF_DEFERRED: Read stays real; write stays unreachable
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New callback + checkbox/switch UI; the already-real, already-tested share-settings endpoint needs no backend change
- TEST_IMPACT: New Playwright case for a real per-member toggle once the input exists

---

**GATE-2Z-INPUT**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `2z`
- DECISION_QUESTION: No editable field or per-field change callback exists. What fields become editable, and how does the color swatch work?
- CURRENT_IMPLEMENTATION: `ProfileEditProps` confirmed: `onSave?: () => void` only, no `onChangeField`; every field renders as non-editable text; the color swatch has no click handler
- WHY_BLOCKED: Same frozen-Screen-authority limit
- RECOMMENDED_OPTION: Add real `<input>`s for name/bio/birthday + a working color-swatch click handler; `onSave` carries the edited values
- ALTERNATIVES: Split into per-field inline edits instead of one form
- DEFAULT_IF_DEFERRED: Read stays real; write stays unreachable
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New input elements + `onSave(fields)` signature change; the already-real, already-tested `PATCH /api/me` endpoint needs no backend change. (Avatar image upload itself is separately `POLICY_REQUIRED` under the storage-infra question, not this gate — see GATE-2B.)
- TEST_IMPACT: New Playwright case for a real profile-field save once the input exists

---

**GATE-3B-INPUT**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `3b`
- DECISION_QUESTION: No period/member/status selection is possible; `onApply` takes no arguments. What filter fields?
- CURRENT_IMPLEMENTATION: `MissionStatisticsFilterProps` confirmed: no model prop at all, `onApply?: () => void`
- WHY_BLOCKED: Same frozen-Screen-authority limit
- RECOMMENDED_OPTION: Add a real model (period options, member list, status) + `onApply(filters)`; reuse `1o`'s date-input pattern for the period field specifically
- ALTERNATIVES: —
- DEFAULT_IF_DEFERRED: The already-real, already-tested `cycle-progress`/`weekly-summary` backend (confirmed period-filterable) stays unreachable from this Screen
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New filter form UI + `onApply(filters)` signature change; no backend change needed
- TEST_IMPACT: New Playwright case for a real filtered statistics view once the input exists

---

**GATE-3J-INPUT**
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `3j`
- DECISION_QUESTION: No query input exists anywhere in this Screen's entry chain. Real `<input>` on the Screen, or a route query-param?
- CURRENT_IMPLEMENTATION: `SearchAllScreen`'s `.searchBox` confirmed to render `<span>{model.query}</span>`, not an `<input>`; `FamilyLanding`'s entry link passes no initial query either
- WHY_BLOCKED: Same frozen-Screen-authority limit
- RECOMMENDED_OPTION: Add a real `<input>` + `onQueryChange`; wire `FamilyLanding`'s entry link to open with an empty query
- ALTERNATIVES: Add a query param to the route instead of an in-page input
- DEFAULT_IF_DEFERRED: The already-real, already-tested cross-entity search backend stays unreachable
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: New input element + debounced query state; no backend change needed
- TEST_IMPACT: New Playwright case for a real search query once the input exists

---

**GATE-3E-REACTION-TOGGLE** (new this pass — the reaction backend was built and is real; only its own UI click target is the open gate, and this document previously folded it into the six `*-INPUT` gates' shape without giving it its own entry, undercounting the canonical total)
- TYPE: `DESIGN_CONTRACT_REQUIRED`
- RELATED_SCREEN_IDS: `3c`, `3e`
- DECISION_QUESTION: Neither frozen Screen's type contract (`FamilyBoardProps`, `PopularPostsProps`) declares a like/react callback. What does tapping the `♥` actually call, and is a double-tap-to-unlike gesture in scope?
- CURRENT_IMPLEMENTATION: Backend is real and tested — `POST .../messages/{id}/reactions` toggles, `GET .../wagle/board/popular` ranks by `reaction_count + comment_count`; `reaction_count`/`reacted_by_me` are already wired into both Screens' *displayed* data. Only the tap handler is missing
- WHY_BLOCKED: Adding a callback to a frozen canonical Screen's type contract is the same design-authority limit as the six `*-INPUT` gates above — this task cannot unilaterally add an interaction surface to a frozen visual baseline
- RECOMMENDED_OPTION: Add `onToggleReaction(messageId: string)` to both Screens' props, calling the already-real, already-tested endpoint
- ALTERNATIVES: Ship read-only counts indefinitely (no toggle from the UI, API-only reactions as seeded by this task's own test data)
- DEFAULT_IF_DEFERRED: Both Screens display real, live reaction/comment counts; no user can actually react from the UI
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: A callback prop + a tap handler in both consuming pages (`WagleBoardPage.tsx` and its Popular Posts overlay) — zero backend change, the endpoint already exists and is tested
- TEST_IMPACT: New Playwright case for a real reaction toggled from the UI (today's evidence toggles it over the API directly, disclosed as such); existing 8 backend reaction tests need no change

---

**GATE-STREAK-BADGE** (corrected this pass from a prior mislabel of `NEW_SLICE_REQUIRED`)
- TYPE: `POLICY_REQUIRED`
- RELATED_SCREEN_IDS: `1f` (2 sub-capabilities: streak count, badge list)
- DECISION_QUESTION: What defines a "streak day" (any mission completed? all assigned missions? approved-only?) and what triggers a "badge" (mission-count milestones? level milestones? something else)?
- CURRENT_IMPLEMENTATION: Frozen `1f` Screen shows these as pure display stats with zero interactivity; grep-confirmed no streak/badge concept exists anywhere in the Ledger/Mission pipeline — same shape as `2c`'s already-accepted level-up-bonus finding
- WHY_BLOCKED: The screen itself does not determine the rule; inventing one would fabricate game-mechanic policy this task has no authority to set
- RECOMMENDED_OPTION: Do not build; keep the current disclosed fixture values (already shipped, not a regression) until a real definition is decided
- ALTERNATIVES: Define "streak" = consecutive calendar days with ≥1 approved Mission; define "badge" = a fixed milestone list (5/10/25/50 lifetime missions)
- DEFAULT_IF_DEFERRED: `1f` keeps its 2 disclosed-fixture stats indefinitely
- W7_5_IMPACT: Isolated
- POST_DECISION_IMPLEMENTATION_REQUIRED: A new computed-field service function (streak) + a new milestone-check function (badge), both read-only derivations over the existing Ledger — no new table needed for either recommended definition
- TEST_IMPACT: New backend tests for the streak/badge computation once a rule is approved

---

```text
Raw screen-level IDs accounted for: 3h(1) + 2f,2w,2p,3i(4) + 1u,2s(2) + 1t(1)
  + 2o(1) + 1i,1v,2y,2z,3b,3j(6) + 1f(1) = 16 raw PM/design flags,
  plus the reaction-toggle gap (3c/3e, +1, previously undercounted as a
  note rather than its own canonical gate) = 17 total raw flags this
  document is aware of, EXCLUDING 2b (counted separately, §4.2).
Canonical PM/design decisions after consolidating true duplicates
  (GATE-INVITE absorbs 4, GATE-PIN absorbs 2): 13.
Reclassification tally (PM/design gates only, 2b excluded):
  POLICY_REQUIRED: 4               (GATE-3H, GATE-INVITE, GATE-D6P2, GATE-STREAK-BADGE)
  DESIGN_CONTRACT_REQUIRED: 9      (GATE-PIN, GATE-2O, GATE-1I/1V/2Y/2Z/3B/3J-INPUT, GATE-3E-REACTION-TOGGLE)
  IMPLEMENTATION_REQUIRED: 0       (none remain — the reaction backend itself was built this task, only its own UI callback is gated)
  CLOSED_BY_EXISTING_DECISION: 0   (GATE-D6P2 is pre-existing but still open, not closed)
  DUPLICATE_GATE (folded, not double-counted): 4  (2w,2p,3i → GATE-INVITE; 2s → GATE-PIN)
  Sum: 4 + 9 = 13 canonical PM/design gates ✓
  Sum of canonical + folded duplicates: 13 canonical + 4 folded = 17 raw ✓
```

None of these 13 block a `CONDITIONAL` W7.5 verdict — each is isolated per
this task's own standing stop-condition rule, carried since Phase B.

### 4.2 The separate infrastructure decision gate — `GATE-2B`

`GATE-2B` is **not** one of the 13 PM/design gates above. It is counted
separately because its question ("which storage backend do we run") has
no product-policy content — it is an infrastructure choice with cost,
durability, and operational tradeoffs, not a "what should the product do"
question.

- GATE_ID: `GATE-2B`
- TYPE: `INFRASTRUCTURE_DECISION_REQUIRED`
- RELATED_SCREEN_IDS: `2b` (Wagle attachments); the same underlying
  question also blocks `2v`'s (album upload) and `2z`'s (avatar upload)
  binary halves, disclosed in §5, but only `2b` is this document's own
  Phase D Slice
- DECISION_QUESTION: Full 16-field storage-infrastructure decision — see §5
- CURRENT_IMPLEMENTATION: No storage abstraction exists anywhere in
  `backend/app` (repo-wide grep, confirmed again this pass)
- WHY_BLOCKED: Building any storage backend before this decision would
  either guess wrong at real operational cost, or require a follow-up
  migration to move already-uploaded files — both worse than waiting
- RECOMMENDED_OPTION: See §5's own recommended option (Option A, local
  filesystem, for a first ship)
- ALTERNATIVES: See §5 (Options B/C/D)
- DEFAULT_IF_DEFERRED: `2b` stays entirely unbuilt, not even metadata
- W7_5_IMPACT: Isolated — does not block a `CONDITIONAL` verdict
- POST_DECISION_IMPLEMENTATION_REQUIRED: New `wagle_message_attachments`
  table (or equivalent for the chosen backend) + upload endpoint + the
  UI upload control itself (currently absent, same shape as the
  `*-INPUT` gates above, but not counted among them since building it
  before the storage decision would be premature)
- TEST_IMPACT: New backend tests for upload/retrieval/auth-on-access
  once a backend is chosen; new Playwright case for a real file upload

```text
FORMAL_PM_AND_DESIGN_GATES: 13
INFRASTRUCTURE_DECISION_GATE: 1
TOTAL_UNRESOLVED_DECISION_ITEMS: 14
```

## 5. GATE-2B — Wagle Attachment Storage Infrastructure Decision Package

No storage backend, file-size limit, retention policy, or access-URL
scheme is decided anywhere in this repository. This package exists so a
real decision can be made without this task guessing.

### Decision fields

| Field | Answer needed |
| --- | --- |
| Supported file types | Images only (jpg/png/webp)? + video? + arbitrary documents? |
| Max file size | Per-file cap (e.g. 10MB images, 50MB video)? |
| Max per message | 1? Up to N (matching `2v`'s "여러 장" album-upload language)? |
| Auto-compress | Client-side, server-side, or none? |
| Thumbnail | Generated server-side or client-side-only preview? |
| Original preserved | Yes/no, and for how long? |
| Storage backend | See options below |
| Access URL | Signed/expiring URL vs. permanent public path vs. proxied through the API |
| Auth on access | Every fetch re-checks Family/Room membership, or a time-boxed signed URL bypasses that check for its lifetime? |
| Retention | Indefinite, or tied to message retention (`D6-P7`, itself still undecided)? |
| Soft delete | Same `deleted_at` convention as `WagleMessage`, or hard-delete the binary on message delete? |
| Malware/virus scan | Required before serving, or accepted risk for a family-internal product? |
| EXIF handling | Strip location/device metadata before storage (privacy), or preserve as-is? |
| NAS vs. cloud | Does this run on the same infra as the persistent dev stack, or a separate service? |
| Backup | Included in existing DB backup only (object storage needs its own), or none? |
| Failure/retry | Client retries on upload failure, or the server queues and retries? |

### Options

**A. Local filesystem + DB metadata row**
- Pros: zero new infrastructure dependency, fastest to build.
- Cons: does not survive a container rebuild/redeploy without a mounted
  volume; no CDN; scaling requires a shared filesystem later anyway.
- Migration impact: one new `wagle_message_attachments` table (message_id,
  path, mime_type, size, uploaded_by), no change to existing tables.
- Frontend impact: an upload `<input type="file">` control needs to exist
  somewhere — `2v` (앨범 업로드 진행) and this Screen (`2b`) both currently
  have no such control either, so this decision and GATE for Album's own
  binary half are the same underlying infrastructure choice.
- Recommended: **for a first ship**, if operational simplicity matters
  more than durability guarantees right now.

**B. S3-compatible object storage (self-hosted MinIO or a cloud provider)**
- Pros: durable, scalable, standard signed-URL access pattern, matches
  how most comparable products solve this.
- Cons: new operational dependency (credentials, bucket lifecycle,
  network egress cost if cloud-hosted); more to configure before any code
  ships.
- Migration impact: same new metadata table as Option A, plus storage
  credentials in configuration (`app/config.py`).
- Recommended: **for a durable, scalable answer**, if this product is
  expected to carry real family photo/file volume long-term.

**C. DB `bytea`/large-object storage**
- Pros: one system to back up, no separate storage credential.
- Cons: bloats the primary database, poor fit for anything beyond very
  small files; this repository's existing tables never do this for any
  binary data today (no precedent to extend).
- Not recommended for this product's likely file sizes (photos).

**D. Disable attachment/photo-upload features for this Wave**
- Pros: zero engineering cost, zero new operational risk.
- Cons: `2v` (album upload) and `2b` (Wagle attachments) both stay
  structurally present but functionally inert indefinitely.
- Valid choice if photo/file sharing is not a near-term product priority.

No option is implemented pending this decision. `2b` and `2v`'s binary
half remain `POLICY_BLOCKED`; no fake upload success or temporary
production storage has been built anywhere in this task's history.

## 6. What is NOT deferred here

Every item in §4 and §5 is a genuine PM/design/infrastructure decision —
none is an implementation task this session avoided. Verification: each
gate's "Existing Evidence" column above cites a direct code read performed
this session (type-contract inspection, live HTTP reproduction, or a
repo-wide grep), not an assumption carried from a prior summary.

## 7. Readiness statement

```text
PHASE_B_STATUS_RECONCILED: true
PHASE_C_11_OF_11_RECONCILED: true
PHASE_D_EFFECTIVE_SCOPE_RECONCILED: true  (11 Slices / 21 screens, both original == effective)
ALL_RESOLVABLE_IMPLEMENTATION_COMPLETE: true  (3e built earlier this task; the pre-existing bcrypt backend defect fixed this pass; nothing else remains resolvable without a real decision)
BOARD_REACTIONS_RESOLVED: true  (implemented, not deferred)
PM_AND_DESIGN_GATES: 13 canonical / 17 raw screen-level flags, all classified, 0 unclassified
INFRASTRUCTURE_DECISION_GATE: 1  (GATE-2B, §4.2 — kept separate from the 13, not folded in)
TOTAL_UNRESOLVED_DECISION_ITEMS: 14
TEST_EVIDENCE_EXACT: see agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md's own "Exact test evidence" section for the current run table
READY_FOR_PM_DECISION: true
```
