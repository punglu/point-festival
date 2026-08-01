# MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001

- Task ID: `MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001`
- Kind: independent QA of the parent bundle `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged start → end)
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; QA-created disposable PostgreSQL 16.9 container `mongle-parentqa-db`, no host port published
- secrets_redacted: `true`
- Independent from implementer: `true`
- Verdict: `CONDITIONAL`
- Verdict (full): `PARENT_INDEPENDENT_QA_CONDITIONAL` — the machine-readable
  field above is the Closeout Contract v1 value; this is the descriptive one.
- Verdict disposition (2026-08-01, at graduation): both conditions were resolved
  rather than waived. `FRONTEND_RUNTIME_FIX` was PM-accepted;
  `TRACEABILITY_GAP` was PM-accepted as non-blocking and remains open as an
  uncommitted-worktree item, not as a product gap. This QA's own classification
  of the frontend Doran occurrences as non-blocking was **retracted by PM** and
  discharged by `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`,
  `MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001` and
  `MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001`. The verdict is left at
  `CONDITIONAL` as recorded — it is not retroactively upgraded to PASS.
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
PARENT_INDEPENDENT_QA_CONDITIONAL
WAGLE_RUNTIME_MIGRATION_VERIFIED
TRACK_A_INDEPENDENT_QA_PASS
TRACK_B_INDEPENDENT_QA_PASS
PARENT_INTEGRATION_INDEPENDENT_QA_PASS
FRONTEND_RUNTIME_DEFECT_FOUND_AND_CORRECTED
TRACEABILITY_GAP_RECORDED
NOT_READY_FOR_NEXT_WAVE_UNTIL_PM_ACCEPTS_TWO_ITEMS
```

Every product-contract verification passed when re-derived from a database this
QA created. The verdict is `CONDITIONAL` rather than `PASS` for two reasons that
are **not** environmental gaps:

1. **A real frontend runtime regression caused by migration `0007`** was found
   by this QA, not by the implementation. It is corrected here (§21/§22), but
   the correction is QA-authored code that has not itself been independently
   reviewed.
2. **`TRACEABILITY_GAP`**: Track A, Track B and the Integration task have **no
   commits**. All three exist only as uncommitted working-tree state on top of
   `0d9280c`, so per-lane attribution cannot be reconstructed from Git history
   as §4.2 requires.

Neither blocks the product contract. Both are PM decisions, so this QA does not
graduate the bundle unilaterally.

## 2. Environment / Git Baseline

| Command | Result |
|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` |
| `git branch --show-current` | `dev-newmarkp` (as expected) |
| `git rev-parse HEAD` | `0d9280c3d3a9254f20c09ba958eb3876e957d245` (as expected) |
| `git diff --check` | clean at start and end |
| Wave 1 baseline `2f1c354` | confirmed ancestor of HEAD |
| commit / push / merge / rebase / PR | **none by this QA** |

## 3. Writer State

`relay/current.md` declared `Current Task: none` — the integration task had
released its claim. No other product writer was active: the only running
containers were the long-lived `mc-db`/`mc-backend`/`mc-frontend`/toolchain
(15h uptime), and no Track A/B test container remained. This QA created its own
container and touched no other task's resources.

## 4. Authoritative Inputs

Read directly: `AGENTS.md`, `rules.md`, `active.md`, `relay/current.md`, the
Track A / Track B / Integration QA files and handoffs, `MONGLE_TARGET_*`
dictionaries, API Inventory, Role Matrix, Realtime Contract, Implementation
Backlog, `COVERAGE_MAP.md`, plus the Alembic chain and the product source.

**Handoff truncation check (§5):** the sentence instructing QA to verify via
`pg_proc`/`pg_trigger`/`permissions` rather than the Alembic log is **complete**
in the file (`MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001.md:68`). Only the
console rendering had been clipped. No document defect.

## 5. Track Commit Trace — `TRACEABILITY_GAP`

```
git log --oneline --all --grep="W2-WAGLE|W4-SERVICE|INTEGRATION-COMPLETION"
  -> (empty)
```

| Required | Found |
|---|---|
| Track A materialization commit | **none** |
| Track B materialization commit | **none** |
| Integration start commit | **none** |

All three lanes exist only as uncommitted working-tree changes on `0d9280c`.
Ownership was therefore reconstructed from `git status` rename detection, file
content and the task records — not from history. Recorded as
`TRACEABILITY_GAP`; the code results are not discarded on this basis, but
per-lane attribution is weaker than a committed history would give.

## 6. Changed-file Ownership (reconstructed independently)

`git status` reports 30 tracked changes + 20 untracked. Rename detection (`RM`)
independently confirms the module move rather than a delete/add pair:

| Class | Files |
|---|---|
| `INTEGRATION_PRODUCT` (rename) | 8 × `app/domains/doran/*` → `app/domains/wagle/*` (all `RM`) |
| `INTEGRATION_TEST` (rename) | 4 × `test_doran_*` → `test_wagle_*` (all `RM`) |
| `INTEGRATION_MIGRATION` | `0007_wagle_runtime_identifiers.py`, `0008_markpoint_access_control.py` |
| `TRACK_B_PRODUCT` | `markpoint_access/{__init__,router,schema,service,system_event_port}.py` + `models.py`, `wagle_relay_adapter.py` (latter two added by Integration) |
| `TRACK_A_TEST` / `TRACK_B_TEST` / `INTEGRATION_TEST` | `test_wagle_durable_wave2.py` / `test_markpoint_access_wave4.py` / `test_integration_wagle_markpoint.py` |
| `SHARED_FILE` | `app/main.py` (router registration only), `app/models/all_models.py`, `tests/conftest.py` |
| `INTEGRATION_DOC` | 7 Target documents, `COVERAGE_MAP.md`, `active.md`, `relay/current.md` |

**Product-file intersection between Track A and Track B: empty** — verified from
the actual paths, not copied from the implementation's claim. `main.py` is the
single shared product file.

## 7. Test Provenance (re-collected, not copied)

| File | Collected |
|---|---|
| `test_account_auth_wave1.py` | 33 |
| `test_integration_wagle_markpoint.py` | 25 |
| `test_markpoint_access_wave4.py` | 21 |
| `test_wagle_durable_wave2.py` | 20 |
| `test_wagle_integration.py` | 17 |
| `test_wagle_reliable_service_slice.py` | 26 |
| `test_wagle_rules.py` | 3 |
| `test_wagle_service_binding.py` | 19 |
| `test_weekly.py` | 6 |
| **Total** | **170** |

Independently matches the implementation's reported figures.

## 8. Test Environment

QA-created container, **no host port published** (runner shares the DB
container's network namespace). Readiness gated on three consecutive successful
queries **plus** a verified `players` table and a 15-table baseline count;
`psql -v ON_ERROR_STOP=1` throughout. No shared/persistent-volume DB was used.

## 9. Migration Graph

Parsed independently from the revision files:

```
0000(27) → 0001(24) → 0002(31) → 0003(26) → 0004(25) → 0005(31) → 0006(30) → 0007(30) → 0008(29)
HEADS: ['0008_markpoint_access_control']  -> single head
```

All revision IDs ≤ 32 chars, so `alembic_version.version_num varchar(32)`
cannot silently roll back an update (the failure mode a prior session hit).

## 10–11. Migration 0007 + PostgreSQL Catalog Verification

**0006 baseline captured first**, then `0007` applied:

| Object | at 0006 (doran) | after 0007 (doran) | after 0007 (wagle) |
|---|---|---|---|
| tables | 7 | **0** | 7 |
| indexes | 19 | **0** | 19 |
| constraints | 44 | **0** | 44 |
| functions | 2 | **0** | 2 |
| triggers | 2 | **0** | 2 |
| permissions | 5 | **0** | 5 |
| roles (`service_code`) | 2 | **0** | 2 |

Exact 1:1 correspondence — no object lost, none duplicated. Independently
matches the implementation's reported counts.

**Relations preserved:** `permissions` 16, `role_permissions` 29, `roles` 9 —
identical before and after. `role_permissions` bindings to the renamed codes: 7
before (doran), 7 after (wagle). **FK orphans: 0** on both
`role_permissions→permissions` and `role_permissions→roles`.

**Function bodies (the check the implementation specifically flagged):**

```
fn_wagle_room_binding_integrity_guard  | refs_doran_table=no | refs_wagle_table=yes
fn_wagle_service_binding_room_guard    | refs_doran_table=no | refs_wagle_table=yes
pg_get_triggerdef() containing 'doran' : 0
```

**Triggers bound correctly:** `trg_wagle_service_binding_room_guard ON
wagle_service_bindings`, `trg_wagle_room_binding_integrity_guard ON
wagle_rooms`.

**Functional trigger test (beyond static inspection).** Inserting a binding
against a non-SERVICE room was **blocked**:

```
RESULT: PASS - blocked: wagle_service_bindings.room_id ... must reference a
SERVICE Room (found GROUP)
```

The guard therefore still fires after the rename and reports the new table
name — static body inspection alone would not have proven this.

**Downgrade `0007 → 0006`:** doran restored to exactly 7/19/44/2/2/5/2, wagle
residue **0** across all six object classes, relations still 16/29/9 with 7
doran bindings, and both function bodies restored to doran references.

**Re-upgrade:** 2 revisions applied to head, `doran_all=0`, `wagle` 7 tables /
5 permissions, `markpoint` 2 tables. No duplicates, no residue.

## 12. Migration 0008

Both tables exist with every reported column. The constraints are **real DB
objects, not application-level checks** — §10.2 required this explicitly:

```
uq_markpoint_activation_request_pending  UNIQUE (family_group_id, service_code) WHERE status='PENDING'
uq_markpoint_access_restriction_active   UNIQUE (target_membership_id, service_code) WHERE status='ACTIVE'
ck_markpoint_activation_requests_status / _processed
ck_markpoint_access_restrictions_status / _restored
fk_markpoint_restriction_target_family   (composite FK — same-family enforcement)
```

**Enforcement tested directly against the DB, bypassing application code:**

| # | Case | Result |
|---|---|---|
| T1 | duplicate PENDING request | **PASS** — blocked by partial unique index |
| T2 | PENDING carrying `processed_at` | **PASS** — blocked by CHECK |
| T3 | restriction targeting another family's membership | **PASS** — blocked by composite FK |
| T4 | duplicate ACTIVE restriction | **PASS** — blocked by partial unique index |
| T5 | re-restrict after RESTORED | **PASS** — allowed, as designed |
| T6 | RESTORED without `restored_at` | **PASS** — blocked by CHECK |

**Downgrade `0008 → 0007`:** markpoint tables/indexes/constraints all 0; the
0007 wagle structure (7 tables) intact. **Fresh `0000 → 0008`** on a
newly-created container: 9 revisions, `doran_all=0`, wagle 7, markpoint 2, wagle
triggers 2.

**Prohibited structures absent:** no `MarkpointParticipant` table or model;
`missions` row count 0 after access-control operations.

## 13. Runtime Wagle Zero Gate

```text
EXECUTABLE_RUNTIME_DORAN_COUNT:        0
ACTIVE_ROUTE_DORAN_COUNT:              0
ACTIVE_PERMISSION_DORAN_COUNT:         0
ACTIVE_SERVICE_CODE_DORAN_COUNT:       0
ACTIVE_TABLE_MODEL_DORAN_COUNT:        0
ACTIVE_MODULE_IMPORT_DORAN_COUNT:      0
ACTIVE_TEST_EXPECTATION_DORAN_COUNT:   0
CURRENT_TARGET_DOCUMENT_DORAN_COUNT:   0   (as an active name)
```

Counted separately, and **not** claimed as zero:

```text
COMMENT_OR_PROHIBITION_REFERENCE_COUNT: 1
  wagle_relay_adapter.py:43 — "no `doran` fallback and no translation map"
  (explicitly permitted by §3)

MIGRATION_SOURCE_REFERENCE_COUNT:       162
  migrations 0002-0005 (original creating revisions) + 0007 (rename source)

HISTORICAL_ARCHIVE_REFERENCE_COUNT:     ~20 documents
  Axis-A / historical / namespace reports, Track A/B QA files

FRONTEND_REFERENCE_COUNT:               127 (see §18)
```

Two `backend/tests` hits were examined and are **not** expectations: they are
the guard test's own function name and a docstring line. The assertions
themselves build the historical literal from parts (`"do" + "ran"`) and assert
its **absence** plus `owner_service == "wagle"` — a genuine guard, correctly
oriented.

**Module:** `app.domains.doran` does not exist; no compatibility package.

**Routes (from the live app object):** wagle 16, historical **0**, markpoint 11
operations across 9 paths. No alias, fallback or redirect.

## 14. Track A Durable Messaging QA

Re-run against the QA database: **20/20**. Verified behaviours include
message + room-sequence + Outbox committing as one transaction with a forced
post-persist failure rolling back all three (checked from a second session),
`client_message_id` idempotency with no second event, same-id-different-body
409, per-room sequence independence (which is what rules out a global counter),
forward-only read cursor, per-membership read isolation, cross-family denial,
and the room-summary read model including deleted-message body suppression.

`SERVICE_ACTION` exclusion from unread is documented as inherited from
`read_state()` with `D6-P4` explicitly undecided — it is **not** presented as a
final policy. Correct.

## 15. Track B Markpoint Access QA

Re-run: **21/21**, plus the integration suite's Markpoint coverage. Verified:
activation request (ACTIVE member only, duplicate PENDING blocked, already-active
conflict), approve/reject by FamilyAdmin only, plain-member denial, cross-family
denial in both directions, no re-processing of a decided request, direct
activation idempotent granting no role, restriction removing default access,
restore returning it, restriction idempotency with history retained,
ServiceAdmin explicit assign/revoke.

**Access formula confirmed in source and behaviour:** ACTIVE subscription AND
ACTIVE membership AND no ACTIVE restriction. Mission participation, assignment,
ledger and reward state are **not** inputs.

Migration `0006`'s FamilyAdmin/ServiceAdmin separation is not bypassed —
activation and approval grant no service role.

## 16. Markpoint–Wagle Relay QA

**Cross-domain boundary read in source, not only greped:**
`markpoint_access/` imports exactly one Wagle symbol —
`from app.domains.wagle import service as wagle_service` — a module reference
called through dotted access. **No Wagle model, table or repository import.**
The adapter resolves the room from the envelope's *approved binding* via
`wagle_service.resolve_binding_room_id()` rather than accepting a raw room id.

Verified by the integration suite: publishes as `ServicePrincipal` with
`sender_participant_id IS NULL`; source-event dedup leaves exactly one message;
unapproved binding, cross-family binding and mismatched principal all rejected;
envelope validation refuses a missing actor/binding.

**Delivery semantics:** no `exactly-once` claim appears in `backend/app` for
message delivery. The five `exactly once` hits found are all about a **secret
being returned to its caller once** (initial password, service credential) — a
different meaning, correctly used.

## 17. HTTP API QA

Routes enumerated from the live application: 16 wagle, 11 markpoint, **0
historical**. The integration suite exercises the historical prefix returning
404, the wagle prefix answering 200, OpenAPI publishing only `/wagle/`, and the
authorization failure matrix (no session, non-member, suspended membership,
cross-family, missing permission).

## 18. Frontend Doran Inventory — **DEFECT FOUND**

127 occurrences. Classification:

| Class | Count | Assessment |
|---|---|---|
| generated OpenAPI types | 41 | stale artifact; regenerating is a separate task |
| preview fixtures (`platform/doran/*`) | 42 | fixture-only, no API call |
| component/page filenames | 36 | naming only |
| **runtime service-code comparison** | **2** | **DEFECT — see below** |

**Active `/doran` API calls: 0** — no `fetch`/`axios`/`httpClient` call targets a
`/doran` route. That condition of §17 passes.

**The second condition of §17 — "현재 frontend build/runtime에서 Doran service
code를 사용하지 않음" — FAILED as delivered:**

```
MongleAppShell.tsx:86   const doranState = serviceStatus('doran');
DoranLanding.tsx:134    ...find((service) => service.service_code === 'doran')
```

These read **real API data**, not fixtures: `useFamilyContextStore` →
`getAccountFamilyContext` → `httpClient.get('/api/account-context')`. Migration
`0007` renamed `service_subscriptions.service_code` to `wagle` (confirmed in the
QA database: `SELECT DISTINCT service_code FROM roles` → `wagle`, `markpoint`).

**Impact:** every family with an active Wagle subscription would report
`unavailable`. `MongleAppShell.tsx:155` gates a user-visible notice on
`doranState !== 'active'`, so the `/wagle` screen would permanently announce
"와글와글은 아직 사용할 수 없는 서비스입니다". A genuine runtime regression
introduced by the parent's own migration, missed because the implementation
classified all 127 frontend hits as fixture-only without separating the two that
consume live API values.

Corrected in §22. Remaining frontend references stay for
`MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001` (not yet opened); no frontend
rename campaign was performed here.

## 19. Documentation Consistency

| Check | Result |
|---|---|
| Role Matrix permission codes vs live seed | **exact match** (5/5 `wagle.*`) |
| Table Dictionary vs live schema | match |
| API Inventory vs live routes | match |
| Backlog status | `IMPLEMENTED_AWAITING_INDEPENDENT_QA` on all six W2/W4 rows — correctly not `DONE` |
| Handoff truncation | none |
| Current Target docs using doran as an **active** name | **0** |

One factual error found and corrected (§22): the Domain Boundary Map cited
`platform/wagle/components/*`, a path that does not exist — the integration's
bulk substitution had rewritten a frontend path that was never renamed.

## 20. Test Commands and Exact Results

```
alembic heads / history parse        -> single head 0008, all IDs <= 32 chars
fresh init.sql + 0000 -> 0008        -> 9 revisions, head 0008
0006 baseline capture                -> 7/19/44/2/2/5/2
0007 upgrade                         -> doran 0 across all classes; wagle 1:1
pg_get_functiondef / pg_get_triggerdef -> 0 doran; guards bound to wagle tables
functional trigger test              -> PASS (non-SERVICE room binding blocked)
0007 -> 0006 downgrade               -> exact restore, wagle residue 0
0006 -> 0008 re-upgrade              -> no duplicates, no residue
0008 -> 0007 downgrade               -> markpoint 0, wagle intact
6 × direct DB constraint tests       -> all PASS
pytest tests/test_wagle_durable_wave2.py       -> 20 passed
pytest tests/test_markpoint_access_wave4.py    -> 21 passed
pytest tests/test_integration_wagle_markpoint.py -> 25 passed
pytest tests/test_account_auth_wave1.py        -> 33 passed
pytest -q (full)                     -> 170 passed, 0 failed
tsc --noEmit (frontend)              -> EXIT=0, no errors
check_closeout.py                    -> no warning attributable to this bundle
git diff --check                     -> clean
```

**NOT_RUN:**

| Scope | Reason | Verdict impact |
|---|---|---|
| Frontend `npm run build` | rollup native binding `MODULE_NOT_FOUND` inside the toolchain container — a pre-existing environment fault, not caused by any change here. `tsc --noEmit` passed clean instead, which type-checks the corrected files. | none — type safety verified by other means |
| Playwright E2E | targets legacy PIN screens; no FE consumer of the new routes exists | none |
| WebSocket / Push / PIN | Wave 3, not implemented by contract | none |

## 21. Defects Found

| # | Severity | Finding |
|---|---|---|
| 1 | **HIGH** | Frontend compared `service_code === 'doran'` against live API data in two places; migration `0007` renamed that value to `wagle`, so an active Wagle subscription would always render as unavailable. Found by this QA; the implementation had classified all frontend hits as fixture-only. |
| 2 | LOW | `MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md` cited `platform/wagle/components/*`, a path that does not exist — collateral from the integration's bulk substitution. |

No defect was found in the migrations, the durable-messaging contract, the
Markpoint access rules, the relay boundary or the API authorization matrix.

## 22. Corrections Applied

**Defect 1 (minimal, 3 lines across 2 files):**
`MongleAppShell.tsx` — `serviceStatus('doran')` → `serviceStatus('wagle')`, the
variable renamed `doranState` → `wagleState` at both its definition and its one
use; `DoranLanding.tsx` — `service_code === 'doran'` → `'wagle'`. Each carries a
comment explaining that the value comes from live API data and why the
historical code silently missed.

This is defect correction within the parent's own scope (§19), not the
prohibited frontend rename campaign: no file, directory, component or fixture
was renamed, and the other 125 frontend references are untouched.

**Defect 2:** path corrected to the real `platform/doran/components/*`, with an
explicit note that these frontend paths still carry the historical name and that
renaming them belongs to a separate task.

**Verification after correction:** `tsc --noEmit` EXIT=0; runtime
`service_code === 'doran'` comparisons now **0**; full backend suite re-run
**170 passed**.

## 23. Regression Results

170/170 after the corrections, identical to before them (the changes are
frontend-only). No test was deleted, skipped, xfailed, weakened, or mocked
around.

## 24. Recursive Scope Review

- **Before:** planned read-only verification plus minimal in-scope correction.
- **After verification:** every claim re-derived from a QA-created database, the live app object, or the source — no implementation figure accepted without independent reproduction.
- **After correction:** QA touched exactly 3 files (2 frontend, 1 document) plus its own records. No migration, backend product code, or test was modified. No Wave 3/Wave 5 work, no legacy backfill, no alias.

## 25. Five-Gate Review

- **환각:** no implementation figure was copied — the 0006 baseline, the rename counts, the test collection and the route counts were each re-derived. The Alembic log was never accepted as migration evidence; the catalog and a functional trigger test were used instead.
- **누락:** 0007, 0008, Zero Gate, message/outbox/ordering/read/room-summary, activation/approve/reject/direct, restriction/restore, ServiceAdmin, relay, dedup, family isolation, API, tests, documents — all covered.
- **오작업:** no dual runtime, no alias/fallback, no legacy backfill, single head, no `MarkpointParticipant`, no automatic ServiceAdmin, no Mission auto-participation, no Markpoint→Wagle DB access, no `exactly-once` claim, no cross-family access, no existing dirty reset.
- **축혼동:** historical Doran, migration-source Doran, current Wagle runtime, Track A durable, Track B access, Wave 3 realtime, Wave 5 ledger, and the frontend follow-up are kept distinct throughout.
- **신선도:** schema = dictionary, routes = inventory, seed = role matrix, backlog = actual state; no broken path (one was found and fixed); no duplicate Task ID; `git diff --check` clean; no truncated handoff sentence.

## 26. Changed-file Manifest (QA-owned)

```
frontend/src/platform/shell/MongleAppShell.tsx      (defect 1)
frontend/src/platform/pages/DoranLanding.tsx        (defect 1)
engineering/phase2/MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md (defect 2)
agent-system/qa/MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001.md (this file)
agent-system/active.md, agent-system/relay/current.md (QA state)
```

No backend product file, migration or test was modified by this QA.

## 27. Residual Risks

1. **The QA's own correction is unreviewed.** Three lines of frontend code written by this QA have not been independently checked by anyone else.
2. **`TRACEABILITY_GAP`** — no lane has a commit; the entire bundle is uncommitted working state.
3. **125 frontend references remain**, including 41 stale generated OpenAPI paths that still describe `/doran` routes the backend no longer serves. Regenerating them is a separate task.
4. **Frontend `npm run build` could not run** (pre-existing rollup native fault). Type checking passed, but a production bundle was not produced.
5. **Outbox consumption is Wave 3**; the relay has no production caller yet.
6. `D6-P4` still governs whether SERVICE_ACTION messages should raise unread.

## 28. Lifecycle / Graduation

**No task graduated by this QA.** The product contract is verified, but two
items are PM decisions:

- accepting the QA-authored frontend correction, and
- accepting the `TRACEABILITY_GAP` (or requiring the lanes be committed first).

Current recorded state:

```text
MONGLE-PARALLEL-W2-W4-001
  Track A:     INDEPENDENT_QA_PASS (product contract)
  Track B:     INDEPENDENT_QA_PASS (product contract)
  Integration: INDEPENDENT_QA_PASS (product contract)
  Parent:      CONDITIONAL — awaiting PM acceptance of the two items above
```

## 29. Final Verdict

```text
PARENT_INDEPENDENT_QA_CONDITIONAL
PRODUCT_CONTRACT_VERIFIED
FRONTEND_RUNTIME_DEFECT_FOUND_AND_CORRECTED
TRACEABILITY_GAP_RECORDED
NOT_READY_FOR_NEXT_WAVE_UNTIL_PM_ACCEPTS
```

The migration, runtime-zero, relay and API verifications all ran and all
passed — none was skipped, so this is not the "environmental gap" form of
CONDITIONAL. The condition is that a real defect existed and was corrected by
the verifier rather than the implementer, and that lane traceability cannot be
reconstructed from Git.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/qa/MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001.md`
- Independent QA: `complete` — this file is the independent QA
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: this QA added no test and changed no coverage claim; it re-executed existing suites and corrected two non-test defects.
- CLOSEOUT GATE: `PASS`

`CLOSEOUT GATE: PASS` means the documentation obligations are synchronized. It
is not PM approval and not graduation.

## 30. PM Correction Addendum (2026-08-01)

PM reviewed this report and **retracted one of its judgements**. Recorded here
rather than by editing the original text.

### Accepted

- The frontend fix in §22 — correct in direction. Requires re-verification by a
  session other than its author before graduation, but not a repeat of the full
  migration/backend QA.
- `TRACEABILITY_GAP` — accepted as **non-blocking**. The absence of per-lane
  commits is a predictable consequence of every execution prompt forbidding
  commit/push, not a work failure. Substitute evidence: the shared start HEAD,
  per-lane changed-file manifests, git rename detection, Task-ID-bearing QA and
  handoff records, and start/end dirty manifests. Commits must **not** be
  manufactured now merely to create traceability.

### Retracted — §18's classification was wrong

This report classified the ~125 remaining frontend occurrences as a
non-blocking follow-up task. **PM retracted that.** The standing decision is
that Doran must not be used in the current product *at all*, not merely in the
backend runtime. This report's own §22 — patching `DoranLanding.tsx` — was
itself evidence that active frontend code still carried the name, and that
should have driven the classification rather than being noted beside it.

Corrected gate status:

```text
BACKEND_WAGLE_ZERO_GATE:        PASS
FULL_PRODUCT_WAGLE_NAMING_GATE: FAIL — FRONTEND REMAINED
PARENT_COMPLETE:                NO
```

### Resolution

`MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001` was executed in response and
brought all four frontend target metrics to 0; see
`agent-system/qa/MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001.md`. That task
found that a bulk sweep had broken the `/naran/doran` legacy redirect, and
recorded that `naran` — also deprecated — remains in two categories already
classified as approved keeps by `MONGLE_NARAN_REMAINING_ALLOWLIST.md`: the URL
route contract and a persisted browser storage key.

The parent bundle stays `IN_PROGRESS` pending independent QA of that frontend
task.
