# MONGLE_MARKPOINT_ON_MONGLE_CONTRACT

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

마크포인트 잔치 is a Service built on Mongle's Account/Group/Membership/Role/Permission/Session structure, per PM's corrected framing — not the legacy `players`-owned system as-is. This contract inventories exactly which business logic is reusable unchanged (`REUSE_LOGIC_ONLY`) versus which persistence/authorization surface must change (`TRANSFORM`), and flags the one open naming/routing decision (`PM_DECISION_REQUIRED`) this document depends on.

**PM_DECISION_REQUIRED (blocks the specifics below, not the classification)**: this contract recommends `family_membership_id` as MarkPoint's target ownership FK (see Target Table/Column Dictionaries for the full reasoning: consistency with Doran's own already-approved pattern) and recommends MarkPoint's authorization move from legacy `PLAYER_ONLY`/`ADMIN_ONLY` to the same `family.service.require_permission`-style Group/Role/Permission check Doran already uses, against the already-seeded `markpoint.*` permission codes. Neither is finalized without PM confirmation.

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

**Conclusion**: MarkPoint's entire algorithmic core is reusable without modification. Every change required to re-host it on Mongle is a persistence-ownership change (which FK column) and an authorization change (which dependency function gates each route) — never a business-rule rewrite.

## What must change (TRANSFORM) — summarized, full detail in Target Table/Column/API Inventory documents

1. Ownership FK on `missions`, `mission_templates`, `daily_points`, `deductions`, `feedbacks`, `notifications`: `player_id` -> `family_membership_id`.
2. A Group-scope column added to `cheer_messages` (`family_group_id`) since it currently has no scope column at all.
3. The leveling input (`total_earned`) re-homed from `players` to `family_memberships`.
4. Every MarkPoint route's auth dependency: legacy `PLAYER_ONLY`/`ADMIN_ONLY`/`ADMIN_JWT` -> Group Role/Permission check against the already-seeded `markpoint.own.read`/`markpoint.missions.manage`/`markpoint.points.adjust` permission codes.
5. `mission/service.py::_emit_mission_completed_event`'s legacy-identity-resolution step becomes unnecessary and can be simplified once ownership itself is Membership-based.

## What is explicitly NOT a Gap under this corrected framing

Per PM's instruction, a difference from the legacy system's current behavior is not automatically a Gap — only a failure to meet the *target* product's requirement is. None of the above TRANSFORM items are regressions: MarkPoint's actual mission/point/level UX (what a parent or child sees and does) does not change at all; only the underlying ownership identity and authorization mechanism does, invisibly to the end user. The `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md` reserves the term "Gap" for cases where the target product genuinely cannot do something it needs to (e.g. 와글와글 having no frontend wiring), not for this kind of internal re-platforming work.

## Data worth carrying forward (MIGRATE_DATA candidates, not decided here)

Existing legacy point/mission history (`missions`, `daily_points`, `deductions`, `feedbacks`, `cheer_messages`, `level_tiers`' seed rows) represents a real family's actual usage history. Whether to migrate this data (mapping each legacy `player_id` to a newly-created Membership via a one-time backfill, similar in spirit to how `LegacyIdentityMapping` already bridges Player->Account) versus starting MarkPoint-on-Mongle with a clean slate is a product/PM decision with real user-facing consequences (a family losing their point history vs. a migration script needing to run against production data) — not resolved in this task, and explicitly out of scope for any document here to decide unilaterally.
