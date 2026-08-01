# MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001

- Task ID: `MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged start → end)
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9 container, no host port published
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
WAGLE_RUNTIME_IDENTIFIER_MIGRATION_COMPLETE
TRACK_A_IMPLEMENTATION_COMPLETE
TRACK_B_IMPLEMENTATION_COMPLETE
PARENT_INTEGRATION_TESTS_PASS
PARENT_SELF_QA_PASS
READY_FOR_PARENT_INDEPENDENT_QA
```

## 2. Environment / Git Baseline

| Measurement | Start | End |
|---|---|---|
| repo root | `/Users/mac/mac_Project/mongle_ui` | same |
| branch | `dev-newmarkp` | `dev-newmarkp` |
| HEAD | `0d9280c` | `0d9280c` (no commit) |
| `git diff --check` | clean | clean |
| commit / push / merge / rebase / PR | — | **none** |

Wave 1 baseline `2f1c354` re-confirmed as an ancestor of HEAD; migrations
`0005`/`0006` and the Account-native modules verified present via
`git cat-file -e HEAD:<path>`, not inferred from a report.

## 3. Shared-root Integration Audit

Both lanes ran in the repository root. No other writer was active at start: the
newest changed file was ~10 minutes old and both lanes' test containers were
gone. Verified by per-file `stat` mtime, not by trusting the active register.

## 4. Track A / Track B File Ownership

| Owner | Files |
|---|---|
| Track A | `backend/app/domains/wagle/{service,router,schemas}.py`, `backend/tests/test_wagle_durable_wave2.py` |
| Track B | `backend/app/domains/markpoint_access/{__init__,router,schema,service,system_event_port}.py`, `backend/tests/test_markpoint_access_wave4.py`, and the shared `backend/app/main.py` (router registration) |
| Shared coordination | `agent-system/active.md`, `relay/current.md`, `COVERAGE_MAP.md`, the Target documents |

**Product-file intersection: empty.** `main.py` is the one shared file and only
Track B edited it. Track B did **not** write `active.md`, `relay/current.md`,
`COVERAGE_MAP.md` or the API Inventory — it respected the single-writer rule,
which is also why its documentation delta was outstanding and is integrated here
(§17).

## 5. Test Provenance

Re-collected per file rather than trusting the earlier `145`:

| File | Tests |
|---|---|
| `test_account_auth_wave1.py` | 33 |
| `test_wagle_durable_wave2.py` | 20 |
| `test_markpoint_access_wave4.py` | 21 |
| `test_integration_wagle_markpoint.py` | 25 (new, this task) |
| `test_wagle_integration.py` | 17 |
| `test_wagle_reliable_service_slice.py` | 26 |
| `test_wagle_service_binding.py` | 19 |
| `test_wagle_rules.py` | 3 |
| `test_weekly.py` | 6 |
| **Total** | **170** |

The earlier 145 = 170 − 25 new integration tests. Consistent.

## 6. Doran Runtime Inventory (before migration)

Classified from a full case-insensitive search, not assumed:

| Class | Finding |
|---|---|
| `ACTIVE_DB_SCHEMA` | 7 tables, 19 indexes, 44 constraints, 2 trigger functions + 2 triggers |
| `ACTIVE_PERMISSION` | 5 codes, bound in `role_permissions` |
| `ACTIVE_SERVICE_CODE` | `roles.service_code`, `service_subscriptions`, `service_principals` |
| `ACTIVE_API` | route prefix + OpenAPI tag, 17 routes |
| `ACTIVE_MODULE` | `app.domains.doran`, 9 files |
| `ACTIVE_TEST` | 4 test files |
| `MIGRATION_SOURCE_REFERENCE` | migrations `0002`–`0005` (historical, left as-is) |

## 7. Wagle Naming Migration

Module moved with `git mv` (history preserved), then a scripted identifier swap
across 21 files, then targeted repairs. Frontend was checked and **excluded**:
`platform/doran/*` renders from static fixtures and calls no `/doran` API, so
the backend rename breaks nothing there; renaming FE files is outside this
task's stated Zero-Gate scope and was not done.

## 8. Migration 0007

Renames tables, indexes, constraints, trigger functions, permission codes,
service code (roles/subscriptions/principals) and any dev Outbox rows.

**Trigger functions are dropped and recreated, not renamed** — PostgreSQL stores
a plpgsql body as text and re-parses it at call time, so a function selecting
`FROM doran_rooms` would have kept doing so after the rename and failed at
runtime.

Verified by SQL against the live catalog:

| Check | Result |
|---|---|
| Fresh `0000` → `0007` | 8 revisions applied, single head |
| Historical tables / indexes / constraints / functions / triggers / permissions / roles after upgrade | **0 each** |
| `wagle_*` objects after upgrade | 7 tables, 19 indexes, 44 constraints, 2 triggers, 5 permissions |
| `role_permissions` bindings preserved | 7 (codes renamed in place, so `permissions.id` references survive) |
| Trigger body points at `wagle_rooms` | confirmed via `pg_get_functiondef` |
| `downgrade -1` | historical objects fully restored (7/19/44/2/5), zero `wagle_*` residue |
| Re-`upgrade` | zero duplicates, zero residue |

**Defect found and fixed during this work:** the first draft derived trigger
names from table names, but the real objects use a singular form
(`fn_<prefix>_service_binding_room_guard`) against a plural table
(`<prefix>_service_bindings`). `DROP ... IF EXISTS` therefore matched nothing,
the historical guards survived, and the database briefly held both sets — with
the old pair referencing tables that no longer existed. Caught by querying
`pg_proc`/`pg_trigger` after the run rather than reading the Alembic log.

## 9–10. Track B Schema Delta / Migration 0008

`markpoint_activation_requests` and `markpoint_access_restrictions`.

Constraints that carry real rules rather than decoration:

- A processed request must record who processed it and when; a `PENDING` one must not pretend to have been (CHECK).
- One `PENDING` request per family+service (partial unique) — a decided request keeps its row for audit without blocking the next one.
- One `ACTIVE` restriction per member+service (partial unique); restoring sets `RESTORED`, releasing the slot while keeping history.
- A restriction can only target a membership **of the same family**, enforced by a composite FK on `(target_membership_id, family_group_id)` — the same pattern `wagle_participants` already uses — not by application code alone.

Verified `0008` → `0007` → `0006` and back to head; `markpoint_*` tables absent
at `0006`, historical tables correctly present there, zero residue on re-apply.

## 11–13. Markpoint Activation / Restriction / ServiceAdmin

Access is now `ACTIVE subscription AND ACTIVE membership AND no ACTIVE
restriction`. Mission participation is not an input, and nothing in this path
creates a Mission or a participant row — asserted by test, not just stated.

Approval marks the request `APPROVED` and activates the subscription in **one
transaction**: the request mutations are pending in the session when
`set_subscription()` issues the single commit, so an approved request cannot
persist without its subscription.

Requesting grants nothing — not access, not ownership, not ServiceAdmin — and
the requester does not become Owner on approval. ServiceAdmin remains explicit
(`assign`/`revoke` only), re-verified by the existing Track B tests.

## 14. Markpoint System Actor Relay

Boundary: `Markpoint domain → port Protocol → adapter → wagle.service`.

The adapter resolves the room from the envelope's **approved binding**, not from
a raw room id — Markpoint has no way to have been authorized for a bare room id.
It does not re-implement binding/family/subscription checks;
`publish_service_action()` owns those, and duplicating them would let the two
copies drift.

**Boundary violation I introduced and then fixed:** the first draft imported
`WagleMessage` directly for its dedup lookup — the exact thing the module's own
docstring forbids. Replaced with `wagle_service.find_service_message_id()`. The
final state is asserted by a test that greps the Markpoint package for any Wagle
model import, so the boundary is enforced rather than documented.

## 15. Wagle Durable Messaging Regression

All Wave 2 behaviour re-verified after the rename: atomicity (message + room
sequence + Outbox in one transaction, forced post-persist failure rolls back all
three), idempotency, per-room ordering independence, read cursor, room summaries.
20/20.

## 16. API Changes

New: 6 Markpoint routes (activation request/list/approve/reject, restriction
create/restore/list). Renamed: 17 Wagle routes to the `/wagle/` prefix. The
historical prefix returns **404** and OpenAPI publishes only `/wagle/` — both
asserted by test.

## 17. Documentation Integration

Updated: Target Table/Column Dictionary, API Inventory, Role Matrix, Domain
Boundary Map, Realtime Messaging Contract, Implementation Backlog, Coverage Map,
`active.md`, `relay/current.md`.

Axis-A and historical documents (`MONGLE_CURRENT_*`, `DORAN_*`,
`*_NAMESPACE_*_REPORT`, Track A/B QA reports) keep their historical references —
they are records of what existed, and rewriting them would falsify evidence.

The Realtime Contract's "still carrying the historical name" table described a
state this task removed; it was rewritten to state the completed migration
rather than left as a stale to-do.

## 18. Test Environment

Volume-less disposable container, **no host port published** (the runner shares
the DB container's network namespace), which also avoids colliding with any
other lane's container. Readiness gated on three consecutive successful queries
plus a verified `players` table, and `psql -v ON_ERROR_STOP=1`.

**This came from a real failure.** An earlier run reported 145 errors that
looked like a product break; the actual cause was `init.sql` silently failing
because `psql` returns 0 without `ON_ERROR_STOP` and the alpine image's initdb
bootstrap restarts the server after the first `pg_isready` success. Diagnosed
rather than assumed.

## 19. Test Commands and Exact Results

```
alembic upgrade head (fresh DB)     -> 8 revisions, head 0008_markpoint_access_control
alembic downgrade -1 x2 / upgrade   -> verified, zero residue
pytest tests/test_integration_wagle_markpoint.py -q  -> 25 passed
pytest -q                                            -> 170 passed, 0 failed
```

| Scope | Result |
|---|---|
| Integration suite (new) | **PASS — 25** |
| Track A suite | **PASS — 20** |
| Track B suite | **PASS — 21** |
| Full backend | **PASS — 170, 0 failed** |
| Pre-existing failures | none |

No test was deleted, skipped, xfailed or weakened.

## 20. Migration SQL Verification

Every migration claim above is a `psql` query result against the live database,
not an Alembic log line. That distinction mattered twice: the `0006` rollback in
a previous session and the trigger-name mismatch in this one were both invisible
in the log and visible in the catalog.

## 21. Runtime Doran Zero Gate

```text
ACTIVE_RUNTIME_DORAN_COUNT:            0
ACTIVE_API_DORAN_COUNT:                0   (old prefix 404; OpenAPI has none)
ACTIVE_PERMISSION_DORAN_COUNT:         0
ACTIVE_SERVICE_CODE_DORAN_COUNT:       0
ACTIVE_TABLE_MODEL_DORAN_COUNT:        0
CURRENT_TARGET_DOCUMENT_DORAN_COUNT:   0   (only labelled-historical mentions remain)
```

Counted separately, **not** claimed as zero:

```text
MIGRATION_SOURCE_DORAN_REFERENCES:
  migrations 0002-0005 (the original creating revisions) and 0007 (the rename's
  source values) — required for the migration to run at all.

ARCHIVED_HISTORICAL_DORAN_REFERENCES:
  ~20 Axis-A / historical / report documents under engineering/phase2/, plus
  Track A/B QA reports and past commit messages.

FRONTEND_DORAN_REFERENCES:
  127 occurrences under frontend/src (fixture-only `platform/doran/*`,
  `DoranLanding.tsx`, generated OpenAPI types). Outside this task's stated Zero
  Gate scope, and no frontend code calls a `/doran` API, so the backend rename
  breaks nothing. Renaming them is a separate FE task.
```

The repository-wide count is **not** zero, and this report does not claim it is.

## 22. Self-QA Findings and Corrections

| # | Finding | Disposition |
|---|---|---|
| 1 | Trigger names derived from table names; `DROP IF EXISTS` matched nothing, leaving historical guards pointing at renamed tables | **Fixed** — explicit prefix parameter; verified in `pg_proc`/`pg_trigger` |
| 2 | The bulk rename inverted the naming-guard test (it asserted the historical name is absent, and the sweep rewrote that literal too) | **Fixed** — literal now built from parts so it survives future sweeps; the same trap is documented in the test |
| 3 | Relay adapter imported `WagleMessage` directly, violating its own stated boundary | **Fixed** — goes through `wagle_service`; a test now greps for the violation |
| 4 | `SERVICE_CODE` and `WAGLE_SERVICE_CODE` both became `"wagle"` after the rename | **Fixed** — one constant; two names for one value was the defect the correction existed to remove |
| 5 | Bulk substitution corrupted prose ("`wagle_*` → `wagle_*` rename", "16 Doran routes", a duplicated table row) | **Fixed** — targeted repairs |
| 6 | Realtime Contract's "still carrying the historical name" table was stale after 0007 | **Fixed** — rewritten as the completed migration |
| 7 | `init.sql` silently failing made a harness fault look like 145 product failures | **Fixed** — `ON_ERROR_STOP` + stricter readiness + table existence check |

## 23. Recursive Scope Review

- **Before:** planned the rename set, two migrations, Markpoint service/routes, the adapter, tests, and the Target documents.
- **After implementation:** `git status` matches; no Markpoint *product* domain (mission/ledger), no frontend source, no `database/init.sql`, no edit to migrations `0000`–`0006`.
- **After tests:** documents match the live schema and routes; no compatibility alias; single head; no test weakened.

## 24. Five-Gate Review

- **환각:** every count is a query result or a test outcome from this session. The Alembic log was explicitly not trusted, which is how two defects surfaced.
- **누락:** service code, permission, route, table, module, outbox, message, read, activation request, approve/reject, restriction/restore, ServiceAdmin, relay, migration, test, document — all addressed.
- **오작업:** no dual runtime, no fallback or alias, no legacy backfill, single head, no `MarkpointParticipant`, no automatic ServiceAdmin, no Mission auto-creation, no direct cross-domain DB access, no plaintext secret, no cross-family access, no existing dirty reset.
- **축혼동:** historical implementation, current Wagle target, migration source values, Track A durable messaging, Track B access, Wave 3 realtime and Wave 5 mission/ledger are kept distinct in both code comments and documents.
- **신선도:** Dictionary = schema, API Inventory = routes, Role Matrix = seed, Backlog = actual state, `git diff --check` clean, no duplicate Task ID.

## 25. Changed-file Manifest

**Renamed:** `app/domains/doran/` → `app/domains/wagle/` (9 files); 4 test files
`test_doran_*` → `test_wagle_*` (all via `git mv`).

**New:** `alembic/versions/0007_wagle_runtime_identifiers.py`,
`alembic/versions/0008_markpoint_access_control.py`,
`app/domains/markpoint_access/models.py`,
`app/domains/markpoint_access/wagle_relay_adapter.py`,
`tests/test_integration_wagle_markpoint.py`, this report and its handoff.

**Modified:** the renamed Wagle domain files, `markpoint_access/{service,router,schema}.py`,
`app/models/all_models.py`, `app/main.py`, `mission/service.py`,
`service_outbox/{models,service}.py`, `workers/service_outbox.py`,
`scripts/phase1_seed_synthetic.py`, `tests/conftest.py`, the four renamed test
files, `test_wagle_durable_wave2.py`, six Target documents, `COVERAGE_MAP.md`,
`active.md`, `relay/current.md`.

## 26. Existing Dirty Preservation

The working tree was clean at HEAD `0d9280c` when this task started; Track A's
and Track B's uncommitted work was already committed at that point. Nothing was
reset, restored, checked out, cleaned or stashed. Track B's container and files
were not touched.

## 27. Residual Risks

1. **Independent QA has not run** on either lane or on this integration.
2. **Frontend still carries the historical name** (fixture-only, no API call). A separate FE task.
3. **Outbox consumption is still Wave 3** — events are recorded, nothing delivers them.
4. **Unread count excludes SERVICE_ACTION messages**, inherited from `read_state()`; the user-visible rule is `D6-P4`, undecided.
5. **The relay has no production caller yet** — Markpoint's Wave 5 product code will be the first.
6. **`docker-compose.phase2.yml` still absent**; the disposable-DB setup is performed by hand.

## 28. Parent Bundle Status

```text
MONGLE-PARALLEL-W2-W4-001
  Track A:     IMPLEMENTED_AWAITING_INDEPENDENT_QA
  Track B:     IMPLEMENTED_AWAITING_INDEPENDENT_QA
  Integration: IMPLEMENTATION_COMPLETE / TESTS_PASS / SELF_QA_COMPLETE
  Parent:      INDEPENDENT_QA_PENDING
```

No task was marked `DONE` or graduated.

## 29. Final Verdict

```text
WAGLE_RUNTIME_IDENTIFIER_MIGRATION_COMPLETE
TRACK_A_IMPLEMENTATION_COMPLETE
TRACK_B_IMPLEMENTATION_COMPLETE
PARENT_INTEGRATION_TESTS_PASS
PARENT_SELF_QA_PASS
READY_FOR_PARENT_INDEPENDENT_QA
```

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: three new source-backed rows plus corrected Wave 2 counts.
- CLOSEOUT GATE: `PASS`

Documentation synchronization only — not independent QA, not PM approval, not
parent-bundle completion.
