# Markpoint Functional Coverage Matrix — Wave 5

Evidence was collected from legacy routers/services/models, frontend dashboard
components and current Target routes; this is a capability matrix, not a claim
that legacy player records are migrated.

| Legacy Feature ID | Domain | Feature | Legacy evidence | Target replacement | Status | Wave | Action |
|---|---|---|---|---|---|---|---|
| MP-M01 | Mission | create/assign/submit/approve | mission router/service | Target Mission APIs | COVERED_TARGET | 5 | membership-owned |
| MP-M02 | Mission | reject/cancel/expiry/revert | mission transition/expiry service | Target reject/cancel/expiry/reversal | COVERED_TARGET | 5 | append-only reversal |
| MP-M03 | Template | CRUD and rolling generation | template router/service | `POST /families/{id}/markpoint/templates/materialize-window`, `service.materialize_rolling_window` | COVERED_TARGET | 5 | Rolling-window contract: `TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE` (PM approved 2026-08-01). Both endpoints inclusive, so a Monday start spans 14 dates, a Saturday 9 and a Sunday 8. Code and docstrings are aligned — Target and legacy `get_rolling_window` were verified to compute the same window across 400 consecutive start dates. Only the Template's named assignee is targeted, never every ACTIVE membership. Duplicate prevention is the `uq_markpoint_mission_template_date` constraint plus a SAVEPOINT retry, proven under `asyncio.gather`. Tests: `test_markpoint_core_gap_wave5.py` MP-M03 section (7) |
| MP-M04 | Mission | weekly date/range/remaining | weekly routes | `GET /me/markpoint/weekly`, `service.own_weekly_detail` | COVERED_TARGET | 5 | Per-date breakdown across the **configured** cycle period, with empty days explicit rather than inferred from a gap. Tests: `test_markpoint_core_gap_wave5.py` MP-M04 section |
| MP-P01 | Point | reward/manual credit/debit | daily_point/deduction services | Ledger + balance projection | COVERED_TARGET | 5 | no legacy table reuse |
| MP-P02 | Point | daily/weekly aggregate | daily_point summary | `GET /me/markpoint/projection`, `service.own_projection` | COVERED_TARGET | 5 | Every figure derived from the Ledger — no separate mutable daily total, which is what let legacy `daily_points` disagree with its own history. today/period earned and deducted, balance, lifetime, remaining, expected. Debits reported as positive magnitudes. Tests: date-boundary, reversal, configured-cycle |
| MP-P03 | Deduction | reason/history/edit | deduction router/service | `GET /me/markpoint/deductions/history`, `POST /families/{id}/markpoint/ledger/{entry}/correct` | COVERED_TARGET | 5 | Correction is **two new rows** (reversal + optional replacement), never an edit; the original is re-read and asserted unchanged. Append-only is additionally enforced by DB triggers `markpoint_ledger_no_update`/`no_delete`. Double correction 409; cross-family 404; concurrent double-correction collapses on the idempotency key |
| MP-L01 | Level | tiers, boundary, EXP | level_tier service | `GET /me/markpoint/level`, reuses `level_tier.calculate_level` | COVERED_TARGET | 5 | Input is **lifetime_earned**, not current balance — spending must not lower a level. 10-case boundary matrix incl. 0, negative, exact tier match, exact LAST tier (keeps its curated title), auto-extension by `excess // last_gap`, and 10M. Reversal lowers lifetime EXP; spending does not |
| MP-U01 | User | dashboard/cards/date UI | frontend pages | Target API capability; UI Wave 6 | DEFERRED_TO_WAVE_6_UI | 6 | no UI work in Wave 5 |
| MP-A01 | Admin | filters/bulk approval | admin dashboard/service | `GET /families/{id}/markpoint/missions`, `POST .../missions/bulk-approve` | COVERED_TARGET | 5 | Filters: assignee, status, template, date range — `family_group_id` applied unconditionally and not omittable. Bulk approval is **all-or-nothing** (no approved contract defines partial success); each reward idempotent; bulk-vs-single race proven to pay once; foreign mission → 404 |
| MP-S01 | Cheer | daily cheer card | cheer router/component | no approved Target replacement | PM_DECISION_REQUIRED | — | retain vs Wagle decision |
| MP-S02 | Feedback | feedback/reply | feedback router/service | no approved Target replacement | PM_DECISION_REQUIRED | — | retain vs retire decision |
| MP-S03 | Notification | unread/read lifecycle | notification router/service | Wagle system messages only for Markpoint events | PM_DECISION_REQUIRED | — | in-app notification policy |
| MP-S04 | Config/cycle | global cycle guards | config service | `markpoint_family_configs` (migration 0011), `GET/PUT /families/{id}/markpoint/config` | COVERED_TARGET | 5 | Per-Family, **not** the legacy global row: one Family's change cannot move another's period. Guard A blocks a change while the current period runs (legacy `validate_cycle_change` rule, per-Family); Guard B blocks it while an ACTIVE Template exists, scoped to that Family's own templates. Cycle value set is the legacy six. **No force override** — none is defined by contract, so none exists |
| MP-S05 | Login log | login history | login_log service | AccountSession/audit | REPLACED_BY_MONGLE_PLATFORM | 1 | account-session evidence |
| MP-S06 | Chat | legacy chat | chat router | Wagle rooms/messages | REPLACED_BY_WAGLE | 2 | Wagle durable evidence |

## Summary

Closed by `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001` on 2026-08-01.

```text
COVERED_TARGET                : 10  (MP-M01..M04, P01..P03, L01, A01, S04)
PARTIALLY_COVERED Wave 5 Core :  0
MISSING_REQUIRED_IN_WAVE_5    :  0
UNCLASSIFIED                  :  0
DEFERRED_TO_WAVE_6_UI         :  1  (MP-U01 — Backend/API complete, UI only)
PM_DECISION_REQUIRED          :  3  (MP-S01 Cheer, MP-S02 Feedback, MP-S03 in-app Notification)
REPLACED_BY_*                 :  2  (MP-S05 login log, MP-S06 chat)
```

`MP-U01` uses `DEFERRED_TO_WAVE_6_UI` legitimately: every backend capability
the dashboard needs — weekly per-date detail, daily/period projection, level,
deduction history — is implemented and tested; only the rendering is Wave 6.

The three `PM_DECISION_REQUIRED` rows are **unchanged and not retired**. They
did not block this closeout and were not silently reclassified; deciding them
is PM's, and nothing in Wave 5 Core depends on the outcome.

Evidence: `agent-system/qa/MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001.md`.
Backend suite at closeout: **312 collected / 312 passed**, Alembic single head
`0011_markpoint_family_config`, zero legacy backfill.
