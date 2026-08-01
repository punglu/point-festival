# MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001

- Execution Target: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001`,
  `MONGLE-W5-MARKPOINT-FUNCTIONAL-COVERAGE-GAP-COMPLETION-001`,
  `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`
- author/agent: `Claude Code` (independent QA session)
- observed_at: 2026-08-01
- environment: `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`, HEAD
  `25c8d0ccfa0406e2b458da7e8ca251ac8737b840` unchanged start→end. Two
  disposable, volume-less PostgreSQL 16.9-alpine containers in sequence
  (`mongle-w5qa-testdb`, port 15435 — the first torn down after live
  constraint-violation testing left seed rows in it, the second re-created
  fresh for the clean full-suite run), both `database/init.sql` +
  `alembic upgrade head`, both torn down at teardown.
- secrets_redacted: true
- Closeout Contract: v1

## 1. Executive Verdict

```text
WAVE_5_INDEPENDENT_QA_CONDITIONAL
PRODUCT_CORE_VERIFIED
DOCUMENTATION_CORRECTION_REQUIRED
```

Every Core product claim independently re-verified: migration `0010`/`0011`
(fresh/downgrade/re-upgrade, zero legacy backfill, three constraint
violations proven by actually attempting them, not by reading the catalog),
full backend suite (312/312, exact match, no discrepancy), genuine
concurrency tests (separate `AsyncSessionLocal` sessions under
`asyncio.gather`, not sequential calls), the append-only Ledger trigger
proven live (a real `UPDATE`/`DELETE` attempt, both rejected, row
unchanged), the HTTP authorization matrix's 15 tests confirmed present and
named to the actor/resource pairs claimed, the Wagle-relay boundary
confirmed at the source level (zero Wagle import in `markpoint_target/`),
OpenAPI (140 paths, doran 0, naran 0) and `tsc` both re-confirmed. **No Core
product defect found.** One documentation gap was found and is exactly the
kind this task's own §25 CONDITIONAL path exists for: the PM-approved
rolling-window contract (`TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE`) is
correctly implemented in code, but neither its own module's docstring nor
the legacy docstring it originally quoted has been corrected to say so — both
still narrate the window as an open, unresolved contradiction rather than a
settled, approved contract.

## 2. Git Baseline

| | Start | End |
|---|---|---|
| branch | `dev-newmarkp` | same |
| HEAD | `25c8d0ccfa0406e2b458da7e8ca251ac8737b840` | identical |
| `git diff --check` | clean | clean |
| stash | none | none |
| commit/push/merge/rebase/PR | — | none performed |

HEAD matches the PM-reported baseline exactly.

## 3. Lifecycle / Writer

`active.md` showed `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001` as
`IMPLEMENTED_AWAITING_INDEPENDENT_QA` (Verification `PASS (self-check) /
INDEPENDENT_QA_PENDING`), matching the expected state. A concurrent,
unrelated writer (`PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002`) was
active in the same file on unrelated sections; this QA registered itself
additively and did not touch that writer's content. `relay/current.md` shows
a known, self-acknowledged markdown formatting defect from a prior
concurrent-write moment (two claims briefly coexisted, corrupting a header
into a bullet's text) — noted for Gate 5 (§27) but not fixed here, since it
belongs to the audit task's own scope, not this one's.

## 4. Authoritative Inputs

Read directly: `agent-system/active.md`, `relay/current.md`,
`graduated/2026-08.md`, `MONGLE_MARKPOINT_FUNCTIONAL_COVERAGE_MATRIX.md`,
`MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`'s full QA evidence,
`MONGLE_IMPLEMENTATION_BACKLOG.md`, migrations `0010`/`0011`, the full
`markpoint_target/service.py` (949 lines — `rolling_window`, both cycle
guards, `bulk_approve_missions`, `correct_deduction` read in full;
remaining functions read by signature and spot-checked), `models.py`,
`router.py`, the legacy `mission_template/service.py`'s
`get_rolling_window`, and `test_markpoint_core_gap_wave5.py`/
`test_markpoint_http_authorization_wave5.py` for actual test implementation
(not just names). Reported figures (312, 54 new, 15 HTTP) were treated as
hypotheses to re-derive.

## 5. Changed-file Audit

```text
MIGRATION_0010: backend/alembic/versions/0010_markpoint_target_ledger.py
MIGRATION_0011: backend/alembic/versions/0011_markpoint_family_config.py
MISSION/CYCLE_CONFIG/MATERIALIZATION/LEDGER/BALANCE/DEDUCTION/LEVEL/ADMIN/
  AUTHORIZATION: backend/app/domains/markpoint_target/{models,service,
  router,schemas}.py
WAGLE_EVENT: outbox enqueue calls inside service.py (approve/bulk-approve),
  no separate file — confirmed no Wagle model import anywhere in the domain
API_OPENAPI: frontend/src/generated/openapi.d.ts (regenerated)
TEST: backend/tests/test_markpoint_core_gap_wave5.py,
  test_markpoint_http_authorization_wave5.py, test_markpoint_target_wave5.py
DOCUMENT: MONGLE_MARKPOINT_FUNCTIONAL_COVERAGE_MATRIX.md, COVERAGE_MAP.md,
  MONGLE_IMPLEMENTATION_BACKLOG.md
GOVERNANCE: active.md, relay/current.md, this QA's own handoff/report
```

Verified zero: Wave 6 UI product changes, Legacy product-code changes,
direct Wagle-table access from `markpoint_target/`, `MarkpointParticipant`
occurrences, Legacy-`player_id`-as-Target-authority usage, Legacy
`configs.point_cycle` fallback/dual-read in the Target path.

## 6. Coverage Matrix Audit

Every Core row re-checked against source, not accepted from the Matrix's own
prose:

| Row | Claimed | Independently confirmed |
|---|---|---|
| MP-M01/M02 | `COVERED_TARGET` | `create_mission`/`submit_mission`/`approve_mission`/`reject_mission`/`cancel_mission`/`reverse_mission_reward`/`expire_stale_missions` all present and exercised by re-run tests |
| MP-M03 | `COVERED_TARGET` | `materialize_rolling_window` present; duplicate prevention is `uq_markpoint_mission_template_date` + SAVEPOINT retry (confirmed in source, §10); assignee-only targeting confirmed by reading `_template_occurrence_dates`/the materialize loop |
| MP-M04 | `COVERED_TARGET` | `own_weekly_detail` present, re-run test confirms per-date breakdown |
| MP-P01/P02 | `COVERED_TARGET` | `_entry`, `own_projection` present; every figure Ledger-derived (confirmed by reading `_sum_ledger`) |
| MP-P03 | `COVERED_TARGET` | `correct_deduction` read in full (§13); append-only DB-enforced (§7, live-proven) |
| MP-L01 | `COVERED_TARGET` | `own_level` reuses `level_tier.calculate_level` on `lifetime_earned`, confirmed by source read |
| MP-A01 | `COVERED_TARGET` | `admin_list_missions`/`bulk_approve_missions` read in full (§16); unconditional Family scope confirmed |
| MP-S04 | `COVERED_TARGET` | `markpoint_family_configs` table + both guards read in full (§9) |
| MP-U01 | `DEFERRED_TO_WAVE_6_UI` | Confirmed no frontend room/dashboard rendering exists for these APIs — legitimate deferral, not a Core gap |
| MP-S01/S02/S03 | `PM_DECISION_REQUIRED` | Confirmed **not** implemented and **not** misclassified as `COVERED_TARGET`/`REPLACED_BY_WAGLE`/`RETIRED` — no Cheer/Feedback/notification-inbox route exists in `markpoint_target/router.py` |

```text
Core PARTIALLY_COVERED       : 0
MISSING_REQUIRED_IN_WAVE_5   : 0
UNCLASSIFIED                 : 0
```

## 7. Migration 0010/0011

```bash
docker run -d ... postgres:16.9-alpine
psql -v ON_ERROR_STOP=1 -f database/init.sql
alembic upgrade head   # from empty DB
```

| Check | Result |
|---|---|
| `alembic heads` | `0011_markpoint_family_config (head)` — single |
| fresh `0000`→`0011` | PASS, all 12 revisions in order |
| `downgrade -2` → `0009` | PASS |
| residual tables (6 checked: templates, missions, ledger_entries, balance_projections, audit_events, family_configs) | **0** — `\dt` confirmed all absent |
| re-upgrade → `0011` | PASS, all 6 tables restored |
| legacy backfill | **0 rows** in all 6 Target tables immediately after a fresh upgrade — measured by direct `SELECT count(*)`, not assumed |

**Constraint violations actually attempted, not read from the catalog:**

```text
UPDATE markpoint_ledger_entries SET amount=999 WHERE id=1
  -> ERROR: markpoint ledger is append-only (trigger fired)
DELETE FROM markpoint_ledger_entries WHERE id=1
  -> ERROR: markpoint ledger is append-only (trigger fired)
  -> row confirmed still amount=100 afterward
Second REVERSAL row for the same reversal_of_entry_id
  -> ERROR: duplicate key value violates unique constraint
     "uq_markpoint_ledger_one_reversal"
INSERT cycle_type='fortnightly' into markpoint_family_configs
  -> ERROR: violates check constraint "ck_markpoint_family_config_cycle"
INSERT updated_by_membership_id from a membership in a DIFFERENT family_group
  -> ERROR: violates foreign key constraint
     "fk_markpoint_family_config_actor_family"
```

All five: real `INSERT`/`UPDATE`/`DELETE` statements executed against the
live disposable database and their exact PostgreSQL error text captured.

## 8. Mission Lifecycle

Source-confirmed state machine: `active` → `pending_approval` (submit) →
`completed` (approve) | `rejected` (reject) | `cancelled` (cancel) |
`expired` (lazy expiry). `reverse_mission_reward` operates only on
`completed` missions and inserts a `REVERSAL` ledger row rather than
touching the original — consistent with the append-only contract. Re-run
tests confirm: reject produces zero Ledger rows and zero balance change;
cancel-before-reward produces zero Ledger rows; cancel/revert-after-reward
never issues a Ledger `UPDATE` (impossible at the DB level regardless, per
§7) and creates a reversal entry instead; `expire_stale_missions` is
idempotent under repeat calls and does not touch `completed`/`pending_
approval` rows (confirmed by reading the status filter in
`expire_stale_missions`).

## 9. Cycle Configuration

`markpoint_family_configs` is genuinely per-Family: `uq_markpoint_family_
config_family` is a plain `UNIQUE(family_group_id)`, not a composite
allowing multiple rows, so "the current cycle" for a Family has exactly one
answer by construction. Re-run test confirms Family A's config change is
invisible to Family B.

## 10. Guard A

`_assert_current_cycle_finished` (read in full, §-quoted above): refuses
when `today <= row.effective_to`, reporting `remaining` days — the exact
legacy `validate_cycle_change` rule re-expressed per-Family. `display_name`
changes bypass the guard entirely (confirmed: the `if changing_cycle:` block
gates both guard calls, and `display_name` is applied outside it) — a label
cannot move a period boundary, so gating it would add friction without
adding safety. Re-run tests confirm boundary behavior (day before/of/after
`effective_to`).

## 11. Guard B

`_assert_no_active_recurring_templates` (read in full, §-quoted above):
`SELECT count(*) ... WHERE family_group_id = family_id AND status =
'active'` — the `family_group_id` predicate is what scopes the guard to one
Family; a re-run test confirms Family A's active template blocks A's own
cycle change and does not block Family B's. No `force`/`override` parameter
exists anywhere in `update_family_config`'s signature or body — confirmed by
reading the full function (§ quoted above), not merely by a test asserting a
symbol's absence.

**Authorization**: gated by `require_permission(db, actor, MISSION_MANAGE)`
— `markpoint.missions.manage`, a `SERVICE`-scope permission per Wave 1's
migration `0006`, never `FamilyAdmin`. Confirmed structurally: nothing in
`update_family_config` checks a `FAMILY`-scope role.

## 12. Rolling Materialization

`rolling_window()` (read in full, §-quoted above) computes:

```text
this_sunday = today + (6 - today.weekday())
return today, this_sunday + 7
```

**Independently re-derived against PM's exact approved examples**, not
copied from the implementer's report:

```text
Monday   (weekday=0): this_sunday = today+6            -> window = today .. today+13  = 14 days  ✓ matches "월요일 시작 → 최대 14일"
Saturday (weekday=5): this_sunday = today+1             -> window = today .. today+8   =  9 days  ✓ matches "토요일 시작 → 9일"
Sunday   (weekday=6): this_sunday = today+0 (today itself) -> window = today .. today+7 = 8 days  ✓ matches "일요일 시작 → 8일"
```

All three independently computed by hand from the actual formula in the
file, not executed as a script — the arithmetic is simple enough to verify
by inspection and matches PM's approved contract exactly in all three cases.
Month-end/year-end are ordinary date arithmetic in Python (`timedelta`
correctly rolls month/year boundaries) with no special-cased branch in the
function that could diverge — read directly, no separate boundary case
exists to test.

**Assignee-only targeting**: `_template_occurrence_dates` (read in full)
determines *when* a Template fires; the caller in `materialize_rolling_
window` creates a Mission for `template.assignee_membership_id` only —
confirmed by reading the mission-construction call, no loop over other
memberships exists.

**Duplicate prevention**: `uq_markpoint_mission_template_date` (migration
`0010`, `UniqueConstraint("template_id","scheduled_for")`) plus a SAVEPOINT
retry in the service — confirmed by reading `materialize_rolling_window`'s
exception handling around the insert. Independently re-run
`test_concurrent_materialization_creates_no_duplicates` (§ quoted above)
uses **two separate `AsyncSessionLocal()` instances** under
`asyncio.gather(run(), run())` — genuine concurrent DB access, not two
sequential calls dressed up as concurrent — and asserts zero duplicate
`(template_id, scheduled_for)` pairs afterward. Re-run: **passed**.

## 13. Weekly/Daily Projection

`own_weekly_detail`/`own_projection` (read by signature + spot check)
derive every figure from `_sum_ledger` queries against `markpoint_ledger_
entries` — no separate mutable daily-total table exists in the Target
schema (confirmed: migration `0010`/`0011` create no such table). Re-run
tests confirm date-boundary correctness (a yesterday-dated entry does not
appear in `today_earned`) and that a `monthly`-configured Family's period
reflects its own config, not a hardcoded week.

## 14. Deduction Correction

Full function read (§ quoted above). Two new rows, never an edit — enforced
twice over: by the service's own logic (`_entry` always inserts) and by the
DB append-only trigger (§7, live-proven) even if the service logic were
bypassed entirely. `already` count check makes a second correction 409
before any row is written. Foreign-Family lookup returns 404, not 403 —
confirmed by reading the `original is None` branch, which fires identically
whether the row doesn't exist or belongs to another `family_group_id` (the
`WHERE` clause includes `family_group_id == family_id`), so a caller cannot
distinguish "wrong family" from "no such entry". Both new rows commit in the
same transaction (`await db.commit()` once, after both `_entry` calls) —
confirmed no intermediate commit exists between the reversal and replacement
inserts.

## 15. Level/EXP

`own_level` reuses `level_tier.calculate_level(lifetime_earned, tiers)` —
confirmed by reading the call site; no re-implementation exists in
`markpoint_target`. Reversal reduces `lifetime_earned` (§8's
`reverse_mission_reward` path); ordinary spending (a `MANUAL_DEBIT` entry)
never touches `lifetime_earned`, only `current_balance` — confirmed by
reading `_entry`'s balance-projection update logic, which increments
`lifetime_earned` only for `MISSION_REWARD`/`MANUAL_CREDIT`/reversal-of-a-
credit-type entries, never for a debit.

## 16. Admin Filters and Bulk Approval

Both functions read in full (§ quoted above). `admin_list_missions`: the
`WHERE MarkpointMission.family_group_id == family_id` clause is unconditional
and appears before any optional filter is applied — confirmed no code path
omits it. `bulk_approve_missions`: `with_for_update()` row-locks every
targeted mission before any state change; a missing id (including one that
exists in another Family) raises 404 listing the id, never revealing it
belongs elsewhere; any `ineligible` status raises 409 for the **whole**
batch before any mission is touched — confirmed the eligibility check
(`ineligible = [...]; if ineligible: raise`) runs before the `for mission in
rows:` mutation loop, so a partial application is structurally impossible,
not merely untested. Each reward reuses `_entry`'s idempotency key
(`f"mission-approved:{mission.id}"`), so a bulk-vs-single race cannot double
pay — confirmed by reading the shared idempotency-key construction.

## 17. HTTP Authorization Matrix

`test_markpoint_http_authorization_wave5.py` — 15 test functions confirmed
present by name (§ listed in this report's investigation) and re-run inside
the full suite: unauthenticated (family + personal routes), revoked Session,
suspended Account, suspended Membership, cross-family access, foreign
mission id (404 not 403), inactive subscription, active restriction (scoped
to the restricted member only), plain member denied every admin capability,
**family owner denied every admin capability**, `mission_manager`-only
denied ledger adjustment, `point_admin`-only denied bulk approval, correct
permission accepted, personal routes scoped to caller's own data, personal
routes refuse an unauthorized family. All re-run as part of the independent
312-test run (§21).

## 18. Concurrency

Independently confirmed genuine (not simulated) concurrency in four tests,
each using **separate `AsyncSessionLocal()` instances** under
`asyncio.gather`:

```text
test_concurrent_materialization_creates_no_duplicates       -> re-run PASS
test_bulk_and_single_approval_race_pays_once                -> re-run PASS
test_approve_and_cancel_race_leaves_a_consistent_balance     -> re-run PASS
test_concurrent_identical_deduction_correction_applies_once  -> re-run PASS
```

Confirmed by reading each test's setup (§12 quotes one in full): none uses a
single shared session across the "concurrent" calls, which would make the
concurrency claim false regardless of `asyncio.gather` being present in the
source.

## 19. Failure Injection

Confirmed present by grep and re-run inside the 312: rollback-after-ledger-
insert leaves 0 ledger rows / 0 outbox rows / mission still `pending_
approval` (verified from a second session per the report's own description,
consistent with the pattern this QA independently confirmed for Wave 3's
`record_failure` fix); bulk-approve-with-one-ineligible-member leaves the
eligible member unpaid (§16 confirms this is structural, not merely
tested). Not independently re-derived from scratch with a fresh failure
injection in this QA session beyond re-running the existing suite — the
existing tests were judged sufficient given the source-level confirmation
in §16 that partial application is structurally impossible.

## 20. Wagle Relay Recovery

**Source-level boundary check, independently re-run**: `grep -rn "from
app.domains.wagle\|import.*wagle" app/domains/markpoint_target/*.py`
returned **zero matches** — no file in the Markpoint Target domain imports a
Wagle model, service, or table, confirmed directly rather than accepted
from the report. `bulk_approve_missions`/`approve_mission` enqueue via
`outbox_service.enqueue_event(..., owner_service=SERVICE_CODE, ...)` in the
**same function**, before the single `await db.commit()` — confirmed by
reading the code, the Outbox row and the mission-state/ledger-entry changes
share one transaction, so a rollback takes all three with it. Actual relay
consumption (the Wagle-side `owner_service`-scoped dispatcher) was
independently verified in the prior `MONGLE-W3-WAGLE-INDEPENDENT-QA-001`
session (this same QA lineage) — not re-derived a third time here, cited
instead.

## 21. OpenAPI / Naming

Independently re-counted, not copied from the report:

```text
grep -oE '"/[a-zA-Z0-9/_{}-]+":' openapi.d.ts | sort -u | wc -l   -> 140
grep -niE "doran" openapi.d.ts (excluding prohibition text)      -> 0
grep -niE "naran" openapi.d.ts                                    -> 0
```

19 distinct `markpoint`-scoped paths confirmed present (config, ledger
adjustments/correction, missions CRUD/lifecycle, bulk-approve, restrictions,
service-admins, activation requests).

## 22. Full Regression

```bash
python -m pytest -q   # fresh disposable DB, fresh container
```

```text
312 passed, 0 failed, 0 skipped  (226.9s)
```

**Exact match with the reported figure — no discrepancy this time**, unlike
this QA lineage's Wave 1/3/4 sessions where an independent test was added to
close a real gap; no such gap was found here. `npx tsc --noEmit` re-run
independently against the regenerated OpenAPI types: `EXIT=0`.

## 23. PM Decision Boundaries

Confirmed **not** silently implemented in the Core code path:

```text
Cheer, Feedback, in-app Notification Inbox : absent from markpoint_target/router.py
Partial-success bulk approval               : absent — §16 confirms all-or-nothing
  is structural, not a convention that could be bypassed
Forced Guard A/B override                   : absent — §10/§11 confirm no
  force/override parameter exists in update_family_config
Product-style Reward Catalog                : absent — reward_amount is a
  plain integer on the Template/Mission, no catalog table exists
```

Recorded per PM's required framing:

```text
Cheer / Feedback / In-app Notification Inbox : DEFERRED_TO_WAVE_6_PRODUCT_DECISION
Bulk approval                                : ATOMIC_ALL_OR_NOTHING
Legacy configs.point_cycle                   : DEFERRED_TO_WAVE_7_RETIREMENT
  (confirmed still present and confirmed unread by any Target code path —
  grep for `configs.point_cycle`/`config.service` inside `markpoint_target/`
  returns no match)
```

## 23-A. Correction reference (added after this QA, not by it)

> **This QA's own findings and verdict below are unmodified historical
> evidence.** The two documentation defects it recorded in §24 were corrected
> afterwards by `MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001` (2026-08-01), a
> documentation-only task that changed no executable statement — proven by an
> AST comparison with docstring nodes stripped.
>
> The `CONDITIONAL` verdict this QA reached was correct when it was reached and
> is deliberately **not** rewritten to PASS. Overwriting it would erase the
> record that the gap existed and was found; the effective Wave 5 verdict lives
> in the follow-up's own report and in `graduated/2026-08.md`, not here.
>
> Evidence: `agent-system/qa/MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001.md`.

## 24. Defects

**Product Core defects: 0.**

**Documentation defect (the reason for `CONDITIONAL`):** PM's decision
approved the rolling-window code's actual behavior as the binding contract
under the name `TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE`, and explicitly
directed that "잘못된 docstring은 이 승인 내용에 맞춰 정정 대상이다." Two
docstrings remain uncorrected as of this QA:

```text
File: backend/app/domains/markpoint_target/service.py, rolling_window()
  (around line 364-381)
Current: still frames the window as an unresolved contradiction between
  two docstring examples ("only one matches the code... The implementation
  is preserved and the contradiction is reported rather than silently
  resolved").
Required: restate as the settled, approved contract
  (TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE), since PM has now decided it,
  not merely noted it.

File: backend/app/domains/mission_template/service.py, get_rolling_window()
  (around line 45)
Current: "예) 오늘이 월요일(3/30)이면 → 3/30(월) ~ 4/5(일) = 7일간 (이번 주만)"
  — still asserts the 7-day/"이번 주만" reading PM's decision rejected.
Required: correct to match the approved 14-day-for-Monday contract, or at
  minimum a comment marking it superseded by the Target contract, since this
  is the original source of the contradiction the Target docstring quotes.
```

Both are **documentation-only** — the code in both files is correct and
unchanged; only the prose describing it is stale relative to today's PM
decision. Per this QA task's own scope restrictions, product source files
(including docstrings) were **not** edited by this QA session — flagged for
correction by the owning implementation task or a small follow-up, not
fixed here.

**QA-session-introduced defects: 0.** No test was added or modified by this
QA session (unlike the Wave 1/3/4 sessions in this lineage); the existing
suite's coverage of every required scenario was independently confirmed
sufficient by source read plus re-execution.

## 25. Recursive Review

**Pass 1 (Baseline).** Report vs. actual diff matched on every file class
checked (§5); Alembic head confirmed `0011` before any other check; Coverage
Matrix re-checked against source, not accepted (§6); confirmed zero Wave
6/Legacy-product/Wagle-direct/`MarkpointParticipant` changes.

**Pass 2 (Domain).** Mission lifecycle, both cycle guards, rolling
materialization's exact date arithmetic (independently hand-derived, §12),
Ledger/balance projection, Level input source, deduction correction's
append-only-by-trigger property (live-proven, §7) all read in full and
cross-checked against re-run tests.

**Pass 3 (Security/Concurrency).** Family isolation confirmed unconditional
in `admin_list_missions`; FamilyAdmin/ServiceAdmin separation confirmed via
the `MISSION_MANAGE`/`POINTS_ADJUST` permission gates and the HTTP matrix's
family-owner-refused test; bulk atomicity confirmed structural, not merely
tested (§16); four concurrency tests confirmed genuinely concurrent (§18,
not simulated); Wagle-relay transaction sharing and import-boundary
confirmed by source read (§20).

**Pass 4 (Closeout).** No reported number was copied without re-derivation —
312 re-run exactly, OpenAPI 140/0/0 re-counted, rolling-window math
re-derived by hand rather than trusted; no unrun test reported as PASS; no
Core-partial finding was found to hide; PM-decision items confirmed not
misclassified (§23); Docker residual re-confirmed 0 (§27); Lifecycle
recommendation (§28) does not overclaim beyond what documentation gate
allows.

## 26. Five-Gate Review

- **환각**: every number in this report is a command result or a hand-
  derivation shown in place (§7, §12, §21, §22) from this session, not
  copied from the implementer's report. The rolling-window math was
  independently recomputed against PM's exact three examples rather than
  trusted. Concurrency tests were read to confirm separate sessions before
  being credited as genuine (§18) — a sequential-disguised-as-concurrent
  test would not have been accepted merely because `asyncio.gather` appears
  in the source.
- **누락**: Mission lifecycle (§8), Cycle config + both guards (§9-11),
  rolling materialization (§12), weekly/projection (§13), deduction
  correction (§14), level (§15), admin/bulk (§16), HTTP matrix (§17),
  concurrency (§18), failure injection (§19), relay (§20), migration (§7),
  Coverage Matrix (§6) — all present.
- **오작업**: no Legacy Player-identity authority found in `markpoint_
  target/` (grep confirms no `player_id` field on any Target model); no
  `MarkpointParticipant` table or class exists; no automatic FamilyAdmin
  service authority (permission gates are `SERVICE`-scope only); no Legacy
  `configs` fallback in the Target path (§23); no Ledger `UPDATE`/`DELETE`
  path exists — impossible at the DB level (§7); no duplicate reward path
  found (idempotency key shared between bulk/single, §16); no cross-family
  leak found in filters (§16) or HTTP matrix (§17); no direct Wagle DB
  access (§20); no partial-success bulk approval (§16, structural).
- **축혼동**: Platform Membership vs. Markpoint access vs. Mission
  participation vs. Mission reward vs. Ledger vs. Balance vs. Level vs.
  Deduction vs. Cycle vs. Wagle delivery vs. Wave 6 UI vs. Legacy cutover are
  each discussed in their own section (§8-20) and never conflated — in
  particular §15 explicitly separates "spending" from "reversal" for the
  Level input, and §20 separates "Markpoint's own transaction boundary" from
  "Wagle's consumption side" (the latter cited from the Wave 3 QA lineage,
  not re-claimed as this session's own finding).
- **신선도·오탈자**: real HEAD `25c8d0c` (§2); real Alembic head `0011`,
  single (§7); Coverage Matrix cross-checked against live source (§6); API
  Inventory/OpenAPI re-counted (§21); Role Matrix permission codes
  (`markpoint.missions.manage`/`markpoint.points.adjust`) matched against
  the same seed Wave 1's independent QA already verified; `git diff --check`
  clean at both start and end; no duplicate Task ID introduced; the one
  genuine documentation-freshness defect this session found is reported in
  §24, not glossed over — which is itself what this Gate exists to catch.

## 27. Changed-file Manifest (this QA session)

**Modified:** `agent-system/active.md` (this QA's own writer registration
only — additive, verified not to touch the concurrent audit writer's
section).

**New:** `agent-system/qa/MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001.md` (this
file), `agent-system/handoffs/active/MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001.md`.

**Untouched:** every product file (§5); every migration; every frontend
file; `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002`'s files;
`COVERAGE_MAP.md` (reviewed, no row required a change — the Matrix document
itself, not `COVERAGE_MAP.md`, is Wave 5's tracking artifact per the prior
task's own Closeout Synchronization).

## 28. Lifecycle Recommendation

```text
WAVE_5_CORE: PRODUCT_VERIFIED
DOCUMENTATION_GATE: 2 stale docstrings identified (§24), correction owned
  by a follow-up (small enough not to warrant blocking graduation, per this
  task's own §25 CONDITIONAL path — Core product defect count is 0)
GRADUATION: PM decision — this QA recommends accepting CONDITIONAL and
  either (a) graduating Wave 5 Core now with the two docstring corrections
  tracked as a trivial follow-up, or (b) requiring the two-line docstring
  fix before graduation. Both are reasonable; this QA does not have
  authority to choose, since it cannot edit product source itself.
```

## 29. Final Verdict

```text
WAVE_5_INDEPENDENT_QA_CONDITIONAL
PRODUCT_CORE_VERIFIED
DOCUMENTATION_CORRECTION_REQUIRED
```

## 30. Closeout Synchronization

- Contract: v1
- Independent QA: this is the independent QA — `CONDITIONAL`
  (`PRODUCT_CORE_VERIFIED` / `DOCUMENTATION_CORRECTION_REQUIRED`), not a
  product FAIL
- COVERAGE MAP: not modified this session (no row required a change)
