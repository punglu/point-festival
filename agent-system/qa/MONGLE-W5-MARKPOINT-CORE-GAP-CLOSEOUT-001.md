# MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001

- Task ID: `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`
- Predecessors: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001`, `MONGLE-W5-MARKPOINT-FUNCTIONAL-COVERAGE-GAP-COMPLETION-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840` (unchanged start → end)
- environment: repository root; disposable volume-less PostgreSQL 16.9; throwaway backend image with container-only dependencies
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
WAVE_5_CORE_GAP_CLOSEOUT_PASS
MARKPOINT_APPROVED_CORE_COMPLETE
LEGACY_FUNCTIONAL_COVERAGE_CLASSIFIED
READY_FOR_WAVE_5_INDEPENDENT_QA
```

All seven Core gaps are closed by implementation and executed test:

```text
MARKPOINT_CYCLE_CONFIG_COMPLETE          MARKPOINT_ADMIN_FILTER_BULK_COMPLETE
MARKPOINT_CYCLE_GUARD_A_PASS             MARKPOINT_HTTP_AUTHORIZATION_MATRIX_PASS
MARKPOINT_CYCLE_GUARD_B_PASS             MARKPOINT_FAILURE_INJECTION_MATRIX_PASS
MARKPOINT_ROLLING_MATERIALIZATION_COMPLETE   MARKPOINT_WAGLE_RELAY_RECOVERY_PASS
MARKPOINT_WEEKLY_CAPABILITY_COMPLETE     MISSING_REQUIRED_IN_WAVE_5: 0
MARKPOINT_DAILY_WEEKLY_PROJECTION_COMPLETE   PARTIALLY_COVERED_WAVE_5_CORE: 0
MARKPOINT_DEDUCTION_CORRECTION_COMPLETE  WAVE_5_FULL_REGRESSION_PASS
MARKPOINT_LEVEL_BOUNDARY_MATRIX_PASS     WAVE_5_SELF_QA_PASS
```

## 2. Git Baseline

| | Start | End |
|---|---|---|
| branch | `dev-newmarkp` | `dev-newmarkp` |
| HEAD | `25c8d0c` | same |
| `git diff --check` | clean | clean |
| stash | 0 | 0 |
| commit/push/merge/rebase/PR | none | none |

The preceding Wave 5 and audit tasks' uncommitted work was present at start and
is preserved; nothing was reset, restored, cleaned or stashed.

## 3. Writer State

Registered as the continuation of the Wave 5 writer, which already owned
`backend/app/domains/markpoint_target/**`, the next Alembic revision,
`all_models.py` and the Markpoint records. No other writer was active on those
files.

## 4. Authoritative Inputs

Read directly: the Coverage Matrix, the two predecessor QA reports and handoffs,
`MONGLE_MARKPOINT_ON_MONGLE_CONTRACT`, the Target dictionaries and API
inventory, `TEST_POLICY.md`, migration `0010`, the current `markpoint_target`
and `markpoint_access` source, the Wagle relay/outbox source, and — decisively —
the **legacy** `config/service.py`, `mission/service.py`,
`mission_template/service.py` and `level_tier/service.py`, because the Matrix's
"preserve existing behaviour" rows can only be settled from the code that
implements that behaviour.

## 5. Initial Coverage State

`PARTIALLY_COVERED` Core: MP-M03, MP-M04, MP-P02, MP-P03, MP-L01, MP-A01.
`MISSING_REQUIRED_IN_WAVE_5`: MP-S04. Each row's claim was re-checked against
the code rather than taken from the Matrix; all seven were confirmed genuinely
incomplete.

## 6–8. Cycle Configuration and its two Guards (MP-S04)

New table `markpoint_family_configs`, **per Family**. The legacy global
`configs.point_cycle` row is deliberately not reused: on Mongle a FamilyGroup
owns its own Markpoint instance, so one Family changing its cycle must not move
another Family's period boundaries. A test asserts exactly that from the second
Family's side.

`cycle_type` repeats the legacy six values (`daily`, `weekly`, `biweekly`,
`monthly`, `quarterly`, `yearly`) as one SSOT across the Enum, the DB CHECK and
the API schema. A seventh value is refused, because `get_cycle_range` — reused,
not re-implemented — could not compute its period.

**Guard A** blocks a cycle change while the current period is still running.
This is the legacy `validate_cycle_change` rule (`today <= cycle_end` → refuse),
re-expressed against the Family's own stored period, and it keeps the
remaining-days detail that makes the refusal actionable. A non-cycle field
(`display_name`) is deliberately *not* blocked: a label cannot move a period
boundary, and blocking it would make the guard feel arbitrary without making
anything safer.

**Guard B** blocks a cycle change while an ACTIVE recurring Template exists,
scoped by `family_group_id`. Tested from both sides: A's template blocks A, and
does **not** block B.

**No force override.** No approved contract defines one, so none exists — not
for FamilyAdmin, not for ServiceAdmin. A test asserts the module exposes no
`force`/`override` symbol, because an override is the natural place for a guard
to quietly stop meaning anything.

Authority is `markpoint.missions.manage`, not FamilyAdmin — D4, and the reason
migration `0006` stripped the permission from every FAMILY-scope role. The HTTP
matrix proves a family **owner** is refused.

## 9. Migration

`0011_markpoint_family_config`, id kept short (`alembic_version.version_num` is
`varchar(32)`; a 36-char id silently rolled back in Wave 1).

```text
alembic heads         -> 0011_markpoint_family_config (single)
fresh 0000 -> head    -> PASS
downgrade -1          -> 0010; residual table count 0
re-upgrade            -> 0011
legacy backfill       -> 0 rows (asserted after upgrade)
constraints           -> 1 unique (family), 2 CHECK (cycle set, date range),
                         1 composite FK (same-family actor), 1 index
```

## 10. Rolling Materialization (MP-M03)

**A legacy contradiction found and reported rather than silently resolved.**
`mission_template.service.get_rolling_window`'s docstring gives two examples and
only one matches its own code:

```text
Saturday 4/4  -> 4/4 .. 4/12  (9 days)   docstring agrees with the code
Monday   3/30 -> 3/30 .. 4/12 (14 days)  docstring claims 7 days, "이번 주만"
```

The code always adds a further 7 days past this week's Sunday, so a Monday
yields a fortnight. **The implementation is preserved** and the contradiction is
raised as a PM decision item (§26) — adopting the docstring would change how
many missions every Monday generates, which is a product decision, not a
cleanup.

Also implemented and tested: occurrences bounded by the Template's own
`start_date`/`end_date` (a window may reach past a Template's life);
weekday-pinned templates generate only on that weekday; inactive templates
generate nothing; **only the Template's named assignee** gets a Mission — never
every ACTIVE membership, never everyone with Markpoint access, never the
FamilyAdmin; and no other Family is touched.

Duplicate prevention is the `uq_markpoint_mission_template_date` constraint plus
a SAVEPOINT retry, **not** check-then-insert. Proven by two concurrent
`materialize_rolling_window` calls in separate sessions: zero duplicate
`(template, date)` pairs.

## 11–12. Weekly Capability and Projection (MP-M04, MP-P02)

`GET /me/markpoint/weekly` returns a per-date breakdown across the **configured**
cycle period, with empty days present explicitly rather than inferred from a gap.

`GET /me/markpoint/projection` returns `today_earned`, `today_deducted`,
`weekly_earned`, `weekly_deducted`, `current_balance`, `lifetime_earned`,
`lifetime_spent`, `remaining_missions`, `expected_points`, plus the period it
used. Every figure is derived from the Ledger; there is no separate mutable
daily total, which is precisely what let legacy `daily_points` disagree with its
own history. Debits are stored negative and reported as positive magnitudes so a
caller never has to remember the sign convention.

Tested: date boundaries (a yesterday-dated entry leaves `today_earned` alone),
reversal, and a `monthly` Family getting its month rather than a hardcoded week.

## 13. Deduction Correction (MP-P03)

A correction is **two new rows**, never an edit:

```text
original debit  -100   untouched, forever
reversal        +100   reversal_of_entry_id -> original
replacement      -80   only when a new amount is given
```

Both commit in one transaction, so a balance can never be observed with the
reversal applied but not its replacement. `new_amount=None` cancels outright.

The test re-reads the **original row** afterwards and asserts its amount and
reason unchanged — a new row appearing is not by itself evidence the old one
survived. Double correction → 409; a mission reward is not correctable as a
deduction → 409; another Family's entry → **404**, because confirming an id
exists elsewhere is itself a disclosure. A concurrent double-correction collapses
on the idempotency key, leaving exactly one reversal.

**Discovered while testing:** append-only is enforced by DB triggers
(`markpoint_ledger_no_update`, `markpoint_ledger_no_delete`), not only by the
service. A test that tried to backdate an entry with a raw `UPDATE` was refused
by the database. The test was changed; the guard was not.

## 14. Level and EXP (MP-L01)

Input is **`lifetime_earned`**, not current balance — the two diverge the moment
anything is spent, and using the balance would make a child's level fall when
they spend their points. Asserted directly: spending leaves `lifetime_earned`
untouched while a **reversal** reduces it (the reward is being undone, not
spent).

The legacy `calculate_level` is reused, not re-implemented, and pinned by a
10-case boundary matrix: 0, negative, just-below, exact tier match, between,
just-below-last, **exact last tier** (keeps its curated title — `excess == 0` is
its own branch), half a gap past, one and two full gaps past (auto-extension by
`excess // last_gap`), and 10,000,000. Progress is asserted clamped to 0–100 and
thresholds strictly ordered at every point.

## 15–16. Admin Filters and Bulk Approval (MP-A01)

Filters: assignee, status, template, date range, limit. `family_group_id` is
applied unconditionally and is **not** one of the optional filters — a caller
cannot widen the query to another Family by omitting a parameter, which is the
usual way this kind of endpoint leaks. Asserted with a second Family present.

Bulk approval is **all-or-nothing**. No approved contract defines partial
success, so inventing it would be inventing policy — and a half-applied batch is
the harder failure to reason about, because the balance does not say which half
landed. An ineligible mission raises and the whole transaction rolls back;
tested by asserting the *eligible* mission was also left unpaid. A foreign
mission id → 404. Duplicate ids in one request collapse. An already-completed
mission is skipped, not re-paid.

The bulk-vs-single race is run in separate sessions: the reward is paid exactly
once and the balance is exact.

## 17. HTTP Authorization Matrix

Run over **real HTTP requests**, in `test_markpoint_http_authorization_wave5.py`
(15 tests). A service-level test proves the service checks something; it cannot
prove the route is wired to that check, and every finding this file targets —
a missing dependency, a `/me` route reachable without a family, a 404-vs-403
leak — lives in the wiring.

| Actor | Result |
|---|---|
| no Session | 401/403 on every Markpoint route and every `/me` route |
| revoked Session | 401 immediately, not when the access token expires |
| suspended Account | 403 everywhere |
| suspended Membership | 403 |
| cross-family ServiceAdmin | 403/404 on every resource |
| foreign mission id | **404**, never 403 |
| inactive subscription | 403 for the whole service |
| ACTIVE restriction | 403 for that member; the unrestricted member is unaffected |
| plain member | 403 on every admin capability |
| **family owner** | 403 on config write, materialize, bulk approve, ledger adjust |
| mission manager | 403 on ledger adjustment |
| point admin | 403 on bulk approval |
| correct permission | 200 — the negatives are only meaningful with this |

## 18. Transaction / Failure Injection

Executed, not reasoned about:

```text
concurrent materialization of one Template   -> 0 duplicate (template, date)
concurrent approve x2                        -> 1 reward
bulk approve vs single approve               -> 1 reward, exact balance
approve vs cancel                            -> <=1 reward; balance == rewards + reversals
concurrent identical deduction correction    -> 1 reversal
rollback after ledger insert                 -> 0 ledger rows, 0 outbox rows,
                                                mission still pending_approval
                                                (verified from a second session)
bulk approve with an ineligible member        -> full rollback, eligible one unpaid
```

## 19. Wagle Relay Recovery

Markpoint's side of the boundary, which is all Markpoint owns:

- The Outbox enqueue shares the mission-approval transaction — a rollback leaves no mission change, no ledger entry, no balance change and no outbox row.
- A relay failure is **not** a data-loss event: `record_failure` leaves the row `PENDING` with `attempt_count=1` and no lease, while the reward, the ledger entry and the `completed` mission all stand.
- Repeated failure to `MAX_ATTEMPTS` reaches `DEAD` and still does not reverse the reward.
- The event is deduplicated by `source_event_id`: approving twice produces one outbox row.
- A source-level assertion proves no file under `markpoint_target/` imports a Wagle model or names a Wagle table.

## 20. Coverage Matrix Final State

```text
COVERED_TARGET                : 10  (MP-M01..M04, P01..P03, L01, A01, S04)
PARTIALLY_COVERED Wave 5 Core :  0
MISSING_REQUIRED_IN_WAVE_5    :  0
UNCLASSIFIED                  :  0
DEFERRED_TO_WAVE_6_UI         :  1  (MP-U01)
PM_DECISION_REQUIRED          :  3  (MP-S01, MP-S02, MP-S03)
REPLACED_BY_*                 :  2  (MP-S05, MP-S06)
```

`MP-U01` uses `DEFERRED_TO_WAVE_6_UI` legitimately — every backend capability
the dashboard needs is implemented and tested; only the rendering is Wave 6.
The three `PM_DECISION_REQUIRED` rows are **unchanged, not retired, not
reclassified**.

## 21. Full Regression

```text
backend collected : 312
backend passed    : 312   (0 failed, 0 skipped)   [was 238 before this task]
  new Core gap tests        : 54
  new HTTP authorization    : 15
migration                   : single head 0011, fresh/downgrade/re-upgrade PASS
OpenAPI regenerated         : 140 paths, doran 0, naran 0
frontend tsc --noEmit       : EXIT=0
git diff --check            : clean
```

Wave 1 Account/Session/RBAC, Wave 2 durable Wagle, Wave 3 realtime, Wave 4
Markpoint access and Wave 5 Mission/Ledger all pass inside the 312.

## 22. Defects Found / Corrected

**No product defect was found in the Wave 5 code under closeout.** Five test
failures occurred during development and all five were mine, not the product's:

1. **Level boundary expectations wrong (3 cases).** I expected 400→L4, 500→L5, 10M→48601. The legacy rule is `extra_levels = excess // last_gap` with `last_gap = 200`, giving 400→L3, 500→L4, 10M→50001. My arithmetic, not a defect; the real values are now pinned.
2. **Backdating a ledger entry with `UPDATE`.** Refused by the DB trigger — the product working correctly. The test now inserts a past-dated row instead.
3. **Reading an ORM attribute after a rollback** (`good.id`) raised `MissingGreenlet`. Same trap as the Wave 3 `record_failure` defect; ids are now captured before the rollback.
4. **Wrong column names on `MarkpointAccessRestriction`** (`family_membership_id`/`active` instead of `target_membership_id`/`ACTIVE`) — I guessed from neighbouring tables instead of reading the Wave 4 model.

Remaining known product defects: **0**.

## 23. Recursive Review

**Pass 1 (before).** Re-checked each Matrix row against the code; all seven were
genuinely incomplete. Read the legacy cycle/level/rolling sources — which is
where the rolling-window contradiction surfaced. Confirmed Alembic head `0010`.

**Pass 2 (after cycle/materialization).** Guard scopes verified per Family from
both sides; rolling window preserved as implemented; duplicate prevention moved
to a DB constraint rather than a pre-check; assignee targeting asserted with a
bystander present; concurrency run.

**Pass 3 (after projection/admin/relay).** Ledger confirmed as sole source for
every figure; deduction correction confirmed append-only by re-reading the
original; level input confirmed as lifetime earned; bulk approval atomicity
asserted by checking the *eligible* item stayed unpaid; relay failure confirmed
isolated from Markpoint state.

**Pass 4 (after tests).** No partial implementation was marked `COVERED`; no
unexecuted test is reported as PASS; the HTTP matrix covers every actor and
resource in §13 of the brief; failure injection covers every row in §14;
Matrix and code agree; lifecycle left at `IMPLEMENTED_AWAITING_INDEPENDENT_QA`.

## 24. Five-Gate Review

- **환각** — every number is a command result from this session; legacy behaviour was read from the legacy source, not assumed; the 312 figure was re-collected, not copied; no concurrency or relay test is claimed without having been run.
- **누락** — cycle config, Guard A, Guard B, rolling materialization, weekly detail, daily/weekly projection, deduction correction, level, admin filter, bulk approval, HTTP authorization, failure injection, relay recovery: all present.
- **오작업** — legacy global config not reused; no all-members auto-generation; no Ledger UPDATE/DELETE (DB-enforced); no direct balance writes; no automatic FamilyAdmin authority; no cross-family exposure; no Wagle DB access; no Wave 6 UI; no legacy backfill.
- **축혼동** — kept distinct: Mission cycle vs Template vs occurrence; Ledger vs balance projection vs level; deduction correction vs reversal vs replacement; admin bulk operation vs single; Wagle delivery vs Markpoint state; Wave 6 UI vs backend capability; PM-decision rows vs Core.
- **신선도·오탈자** — HEAD `25c8d0c`, Alembic single head `0011`, OpenAPI regenerated (140 paths, doran 0, naran 0), `tsc` EXIT=0, Matrix consistent with code, `git diff --check` clean.

## 25. Changed-file Manifest

**New (3)** — `backend/alembic/versions/0011_markpoint_family_config.py`,
`backend/tests/test_markpoint_core_gap_wave5.py`,
`backend/tests/test_markpoint_http_authorization_wave5.py`
**Modified (6)** — `markpoint_target/models.py` (cycle config model),
`markpoint_target/service.py` (+~570 lines across the seven gaps),
`markpoint_target/router.py` (9 routes), `markpoint_target/schemas.py`,
`backend/app/models/all_models.py`, `frontend/src/generated/openapi.d.ts`
**Docs/records** — `MONGLE_MARKPOINT_FUNCTIONAL_COVERAGE_MATRIX.md`,
`COVERAGE_MAP.md`, `active.md`, `relay/current.md`, this report and its handoff.

No frontend product code was written — Wave 6 is out of scope; only the
generated API types were refreshed.

## 26. PM Decision Items

1. **The legacy rolling-window docstring contradicts its code.** The code gives a Monday a 14-day window; the docstring says 7 ("이번 주만"). The code is preserved. If the docstring is the intended contract, that is a behaviour change to approve explicitly, not a cleanup.
2. **MP-S01 Cheer, MP-S02 Feedback, MP-S03 in-app Notification** remain `PM_DECISION_REQUIRED` — untouched, not retired, and they did not block this closeout.
3. **Bulk approval is all-or-nothing** because no contract defines partial success. If per-item results are wanted, that is a contract to approve.
4. The legacy global `configs.point_cycle` row still exists and is now unused by Markpoint Target. Retiring it belongs to the Wave 7 cutover, not here.

## 27. Residual UI / Cutover Dependencies

`MP-U01` — the Wave 6 dashboard. Backend capability is complete;
`MONGLE-W5-TARGET-UI-001`'s own Start Gate forbids claiming integration while
rendering from fixtures, so no UI claim is made here. Legacy table retirement
(`configs`, `daily_points`, `mission_templates`) is Wave 7.

## 28. Lifecycle

`IMPLEMENTED_AWAITING_INDEPENDENT_QA`. Nothing graduated.

## 29. Final Verdict

```text
WAVE_5_CORE_GAP_CLOSEOUT_PASS
MARKPOINT_APPROVED_CORE_COMPLETE
LEGACY_FUNCTIONAL_COVERAGE_CLASSIFIED
READY_FOR_WAVE_5_INDEPENDENT_QA
```

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: two new source-backed rows for the Markpoint Core capabilities and the HTTP authorization matrix.
- CLOSEOUT GATE: `PASS`
