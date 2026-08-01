# MONGLE_MARKPOINT_ON_MONGLE_CONTRACT

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

> **STATUS: PARTIALLY_SUPERSEDED_BY_MONGLE_TARGET_DECISION_FREEZE.** Current inventory remains valid. D5-B approves FamilyGroup ownership, FamilyMembership identity and no separate MarkpointParticipant at this stage; D5-C is machine-only; D8 RESET prohibits Legacy data import/backfill. Pure arithmetic is reuse candidate material; state transitions, ledger/balance, approval, expiry and notifications require Target contract review for actor/scope/transaction/idempotency/audit and the `cancelled` mismatch.

마크포인트 (Markpoint) is a `FAMILY`-owned optional service built on 몽글's Account/FamilyGroup/FamilyMembership/Role/Permission/Session structure — not the legacy `players`-owned system as-is. This contract inventories which business logic is reusable (`REUSE_LOGIC_ONLY`) versus which persistence/authorization surface must be newly built (`TRANSFORM`).

**Approved Target boundary (D5-B):** Owner is `FamilyGroup`; human identity is `FamilyMembership`. A FamilyMember may request activation; FamilyAdmin approves or activates directly. Once `ACTIVE`, every `ACTIVE` FamilyMembership has default MEMBER access — **default access is not forced Mission participation**, and per-membership restriction is available by explicit policy. ServiceAdmin authority exists only by explicit assignment, and the registrant is never automatically ServiceAdmin. **No `MarkpointParticipant` aggregate is introduced at this stage.**

**Approved routing (D7):** Markpoint is reached under `/families/{familyId}/markpoint`; the server never trusts a URL or client `familyId` and revalidates Session, Membership, service ownership, Role/Permission and resource ownership. The former "open naming/routing decision" is therefore **closed** — only the cosmetic physical-table naming question remains open elsewhere, and it blocks nothing here.

**Approved data boundary (D8):** the exact physical schema and API realisation is implementation work. It is **not** a license to convert, import or backfill existing Legacy rows.

## Reusable business logic — REUSE_LOGIC_ONLY, verified by direct source read this task

| Logic | Current location | Why it's identity-agnostic (reusable as-is) |
|---|---|---|
| Mission status state machine (`ROLE_TRANSITIONS` table: which status can move to which, per role) | `mission/service.py:146-160` | Operates purely on `(current_status, new_status, role)` strings; never references `player_id` or any identity table directly in its transition-validity logic |
| Point-sync-on-status-change (`_sync_daily_point_on_status_change`) | `mission/service.py:366-398` | Takes a `Mission` ORM object and delegates the actual point write to `daily_point.service.adjust_daily_point` — the *owning identity* of that Mission/DailyPoint row is whatever the FK says, the arithmetic itself (earned_delta on completion, negative on revert) doesn't care |
| Lifetime total-earned sync (`_sync_total_earned`) | `mission/service.py:16-32` | A single `UPDATE ... SET total_earned = total_earned + :delta` — trivially re-targetable to any owning table/FK |
| Cycle-range calculation (`get_cycle_range`: daily/weekly/biweekly/monthly/quarterly/yearly) | `mission/service.py:49-95` | Pure date arithmetic, zero identity coupling |
| Level/tier hybrid calculation (`calculate_level`, including the auto-extension-beyond-last-tier logic) | `level_tier/service.py:120-194` | Explicitly documented as "DB 접근 없음 — 순수 계산 함수" (no DB access — pure calculation function); takes a plain `total_earned: int` and a `tiers` list, returns a `PlayerLevelInfo` — the "Player" in that response model's name is the only identity-coupled thing about it, and that's a naming/schema label, not logic |
| Lazy-expiry of stale missions (`expire_stale_missions`, `expire_overdue_missions`) | `mission/service.py:111-142,549-571` | Pure `UPDATE ... WHERE date < :x AND status IN (...)` — no identity coupling |
| Mission-completion Outbox event emission (`_emit_mission_completed_event`) | `mission/service.py:308-363` | Already written to resolve the *current* identity model (`family_service.resolve_current_account({"player_id": ...})`) to a Group-scoped event — this function is the one piece of MarkPoint code that already explicitly bridges legacy Player identity to the Mongle Account/Group model, and its own docstring frames the legacy-Player case as the expected near-term reality ("most legacy players have no linked Account/Family yet... that is not an error"). Once mission ownership itself moves to `family_membership_id`, this bridging step becomes unnecessary (the Membership's Group is already known directly), simplifying this function, not breaking it. |
| Point-cycle guard validation (`validate_cycle_change`: locks cycle changes mid-period or while active recurring templates exist) | `config/service.py:32-75` | Pure date/count comparison logic against `mission`/`mission_template` tables, no identity coupling beyond whatever FK those tables already use |

**Conclusion**: pure calculation logic is a reuse candidate. State transitions, approvals, ledger/balance and events need Target contract review; implementation creates new Target records and does not migrate Legacy operational data.

**Reuse of business logic ≠ migration of operational data.** Porting a verified pure function into the Target codebase is approved in principle. Reading, converting or backfilling any legacy `players`/`missions`/`daily_points` **row** into Target is prohibited by D8. The two must never be bundled into one task.

## What must change (TRANSFORM) — summarized, full detail in Target Table/Column/API Inventory documents

1. New Target Markpoint ownership is FamilyGroup/FamilyMembership-scoped per D5-B; no direct Legacy `player_id` conversion or row import is authorized.
2. A Group-scope column added to `cheer_messages` (`family_group_id`) since it currently has no scope column at all.
3. The leveling input (`total_earned`) re-homed from `players` to `family_memberships`.
4. Every MarkPoint route's auth dependency: legacy `PLAYER_ONLY`/`ADMIN_ONLY`/`ADMIN_JWT` -> Group Role/Permission check against the already-seeded `markpoint.own.read`/`markpoint.missions.manage`/`markpoint.points.adjust` permission codes.
5. `mission/service.py::_emit_mission_completed_event`'s legacy-identity-resolution step becomes unnecessary and can be simplified once ownership itself is Membership-based.

## What is explicitly NOT a Gap under this corrected framing

Per PM's instruction, a difference from the legacy system's current behavior is not automatically a Gap — only a failure to meet the *target* product's requirement is. None of the above TRANSFORM items are regressions: MarkPoint's actual mission/point/level UX (what a parent or child sees and does) does not change at all; only the underlying ownership identity and authorization mechanism does, invisibly to the end user. The `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md` reserves the term "Gap" for cases where the target product genuinely cannot do something it needs to (e.g. 와글와글 having no frontend wiring), not for this kind of internal re-platforming work.

## Markpoint → Wagle system notifications — D5-C approved

Automated Markpoint notifications are published under a **non-human 마크포인트 system actor**, technically represented by `ServicePrincipal`. They are never sent under a FamilyAdmin, ServiceAdmin or FamilyMember name, and `ServicePrincipal` never substitutes for FamilyMembership, ServiceAdmin, Registrant or Owner.

Required properties:

- delivered only to an approved Wagle Room in the **FamilyGroup where the source event occurred**; cross-family delivery is prohibited
- human messages and system messages are distinguishable in both UI and audit
- each system message is traceable to its source Markpoint event, and duplicate publication of the same mission/approval/point event is prevented
- unaffected by FamilyAdmin, ServiceAdmin or registrant changes
- **no new automated notification is published** for a FamilyGroup where Markpoint is `INACTIVE` or `SUSPENDED`

Whether the existing `service_principals` rows and Wagle service bindings are physically fit for reuse is an implementation verification item. It is not permission to reverse this approved logical contract, and `player_id` must never be auto-converted to either `family_membership_id` or `service_principal_id`.

## Legacy data disposition — D8 RESET

Legacy point/mission history (`missions`, `daily_points`, `deductions`, `feedbacks`, `cheer_messages`, `level_tiers` seed rows) is not migrated or backfilled. It may be retained separately read-only for reference/audit until PM-approved retirement, but new Markpoint starts with new records and a new ledger.
