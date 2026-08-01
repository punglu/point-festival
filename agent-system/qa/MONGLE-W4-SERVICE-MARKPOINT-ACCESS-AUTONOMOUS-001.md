# MONGLE-W4-SERVICE-MARKPOINT-ACCESS-AUTONOMOUS-001

- Task ID: `MONGLE-W4-SERVICE-MARKPOINT-ACCESS-AUTONOMOUS-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001` (Lane B)
- Kind: execution bundle — one working session implementing the
  implementable-without-schema-change slice of Wave 4 (service ownership /
  activation and Markpoint access). Not a new product Task ID; it targets the
  existing Backlog task `MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001` plus the
  D5-C system-actor sub-scope of `MONGLE-W4-MARKPOINT-SYSTEM-EVENT-RELAY-001`.
- author/agent: `Claude Code`
- observed_at: 2026-08-01
- environment: `/Users/mac/mac_Project/mongle_ui` (repository root — Lane A
  was explicitly instructed to run here too; this lane proceeded here after
  the user accepted the concurrent-root risk in place of a separate
  worktree, and touched no Lane A file), branch `dev-newmarkp`, HEAD
  `0d9280c3d3a9254f20c09ba958eb3876e957d245` unchanged start-to-end. Tests run
  against a disposable, volume-less PostgreSQL 16.9-alpine container
  (`mongle-w4-testdb`, port 15435, `database/init.sql` baseline +
  `alembic upgrade head`), torn down at teardown — zero residue confirmed.
- secrets_redacted: true
- Closeout Contract: v1

## 1. Executive Verdict

```text
TRACK_B_WAGLE_NAMING_CONTRACT_PASS
TRACK_B_IMPLEMENTATION_COMPLETE
TRACK_B_PARTIALLY_COMPLETE
SCHEMA_DELTA_REQUIRED
TRACK_B_TESTS_PASS
TRACK_B_SELF_QA_COMPLETE
PARENT_BUNDLE_IN_PROGRESS
INTEGRATION_QA_PENDING
```

The implementable-without-migration slice of Wave 4 is complete and tested:
FamilyAdmin direct Markpoint activation, default-access resolution, explicit
Markpoint ServiceAdmin assignment/revocation (registrant/FamilyAdmin never
auto-admin), and the D5-C system-actor event port contract. The
member-request → admin-approval activation flow and per-member restriction
are `SCHEMA_DELTA_REQUIRED` — both need new persisted state the existing
schema does not have (§9). No migration was created or modified, per the
parallel-execution rule that Alembic is Lane A's.

## 2. Environment / Git Baseline

| Measurement | Value |
|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` |
| `git branch --show-current` | `dev-newmarkp` |
| `git rev-parse HEAD` | `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged) |
| `git diff --check` | clean, start and end |
| commit / push / merge / rebase / PR | none performed |

## 3. Wave 1 Baseline Verification

Confirmed directly, not inferred from the QA report's wording:
`git cat-file -e HEAD:backend/alembic/versions/0005_account_credential_session.py`
and `...0006_family_service_separation.py` both resolve (committed at HEAD,
inside commit `2f1c354`), as do `family/auth_service.py`,
`family/dependencies.py`, and `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`.
Working tree was clean (no dirty files) at this lane's own start, before Lane
A began its own work.

## 4. Actual Wave 4 Task Inventory (from `MONGLE_IMPLEMENTATION_BACKLOG.md`)

| Task ID | Status at start | This session's disposition |
|---|---|---|
| `MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001` | `BLOCKED_BY_DEPENDENCY` → Wave 1 now satisfied | `PARTIALLY_COMPLETE` — direct activation, default access, restriction-aware access read, ServiceAdmin assign/revoke, registrant-not-auto-admin: **implemented and tested**. Member-request/approve/reject and per-member restriction: **SCHEMA_DELTA_REQUIRED** (§9) |
| `MONGLE-W4-MARKPOINT-SYSTEM-EVENT-RELAY-001` | `BLOCKED_BY_DEPENDENCY` (needs `MONGLE-W2-WAGLE-REALTIME-001`, Wave 3, not started) | Port **contract only** implemented and tested (§8); no adapter, since Wave 3's dispatcher does not exist and Lane A's own Wagle durable-messaging interface is still `INDEPENDENT_QA_PENDING` in this same session window |
| `MONGLE-FAMILY-SERVICE-OWNERSHIP-001` | `BLOCKED_BY_DEPENDENCY` | Satisfied structurally by the Markpoint implementation: `ServiceSubscription` is already FamilyGroup-owned regardless of registrant (existing Wave 1 schema); no new work needed, no new physical table introduced per D5-A1's own instruction not to invent one |
| `MONGLE-FAMILY-SERVICE-REGISTRATION-001` | `BLOCKED_BY_DEPENDENCY` | Registrant/Owner/User/ServiceAdmin/ServicePrincipal kept distinct in the Markpoint implementation (§7); no automatic ServiceAdmin grant proven by test (§10). Treated as satisfied by the concrete Markpoint instance per Track B's own instruction not to over-build a generic abstraction |
| `MONGLE-SERVICE-OWNERSHIP-LIFECYCLE-001` | `BLOCKED_BY_DEPENDENCY` | Partially covered: registrant leave/suspension does not delete the `ServiceSubscription` (no code path does so); membership termination revokes ServiceAdmin roles (§10, reuses Wave 1's `revoke_membership_roles`). Retention/archive/export policy is **not** addressed — out of this session's scope |
| `MONGLE-SERVICE-DEFINITION-POLICY-001`, `MONGLE-PERSONAL-SERVICE-OWNERSHIP-001`, `MONGLE-SERVICE-ACCESS-POLICY-001` | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | Untouched — each needs its own named-service PM decision, not in this session's scope |

## 5. Parallel Safety / Track A Interaction

- `agent-system/active.md`, `agent-system/relay/current.md`: **not modified**
  by this session (confirmed by final `git status`, §14).
- Alembic migrations: **none created or modified**. `alembic current` at the
  end of this session's own DB setup still reports
  `0006_family_service_separation (head)` — single head, unchanged.
- Files this session touched: `backend/app/domains/markpoint_access/**` (new),
  `backend/tests/test_markpoint_access_wave4.py` (new),
  `backend/app/main.py` (2 lines added: router import + registration).
- Files Lane A touched (`backend/app/domains/doran/{router,schemas,service}.py`,
  `backend/tests/test_wagle_durable_wave2.py`, `agent-system/active.md`,
  `agent-system/relay/current.md`, `agent-system/qa/COVERAGE_MAP.md`,
  `engineering/phase2/{MONGLE_IMPLEMENTATION_BACKLOG,
  MONGLE_TARGET_API_INVENTORY,MONGLE_REALTIME_MESSAGING_CONTRACT}.md`): **not
  touched by this session**, confirmed by `git diff --name-only` showing no
  overlap with the file list above.
- `backend/app/main.py` was touched by both lanes conceptually (both add a
  router registration) but the actual diff shows Lane A added no lines there
  — its two `doran_router` references are pre-existing context lines, not
  Lane A's addition either (§13). No line-level collision occurred.

## 6. Wagle Naming Contract Correction (mid-session PM directive)

A PM directive mid-session required removing `Doran`/`doran`/`도란` from
every Track-B-owned file, since `Wagle` is the current Target product name.

**Search performed:** per-file `grep -niE 'doran|도란'` over every file this
session created (`backend/app/domains/markpoint_access/*.py`,
`backend/tests/test_markpoint_access_wave4.py`) and the two added lines in
`backend/app/main.py`.

**Found:** 3 occurrences, all in `system_event_port.py` docstrings/comments
(`CURRENT_TARGET_CONTRACT` prose explaining the port imports no Doran/Wagle
repository) — zero as a runtime identifier, constant, enum, API field, or
test assertion value. No envelope field was ever set to a literal `"doran"`
value (the envelope has no `owner_service`/`service_code`-style field at
all — see §8).

**Corrected:** all 3 reworded to say "Wagle" instead of "Doran/Wagle",
without changing any behavior (docstring/comment-only diff).

**Not touched, deliberately:** `backend/app/main.py`'s two `doran_router`
import/registration lines are the actual existing physical module name
(`app.domains.doran`), owned by Lane A / prior sessions, outside this task's
scope and outside this diff (confirmed pre-existing via `git diff -U0`, §13).
Renaming the real module is a Human Gate decision this session does not have
authority to make, and the naming directive itself instructs against
"무차별 rename" of pre-existing physical module names.

**Naming Gate:**

```text
TRACK_B_TASK_OWNED_LIVE_DORAN_COUNT: 0
TRACK_B_RUNTIME_DORAN_IDENTIFIER_COUNT: 0
TRACK_B_CURRENT_TARGET_DORAN_REFERENCE_COUNT: 0
WAGLE_RUNTIME_IDENTIFIER_CONFIRMED: yes — the System Actor Port's field names
  (`family_group_id`, `service_principal_id`, `approved_room_binding_id`) are
  product-neutral by design (no service-name literal anywhere), and every
  prose description of the target messaging capability says "Wagle".
```

Re-verified after correction: `git diff --check` clean; all 21 targeted tests
re-run and passed (§11); full 145-test suite re-run and passed (§12).

## 7. Service Ownership — D5-A1/A2/A3 Framework, as Instantiated by Markpoint

No new generic `ServiceDefinition`/`ServiceInstance` abstraction was built —
per Track B's own instruction not to over-engineer a generic layer when
PERSONAL/FAMILY scope already exists in the current model
(`ServiceSubscription.family_group_id`, `Role.scope_type`,
`Role.service_code`). Markpoint is the concrete `FAMILY`-owner-scope instance:

- **Registrant**: the calling Account (never persisted as a distinct role).
- **Owner**: `FamilyGroup`, via `service_subscriptions.family_group_id`.
- **Human identity**: `FamilyMembership` (existing table).
- **ServiceAdmin**: `SERVICE`-scope `roles` (`mission_manager`, `point_admin`,
  seeded in `0001`, unchanged by this session).
- **ServicePrincipal**: out of this session's write scope (existing Doran
  `service_principals` table, owned by Lane A/prior work); the System Actor
  Port (§8) references it only by an opaque `service_principal_id: int`.

## 8. System Actor Port (D5-C) — Contract Only

`backend/app/domains/markpoint_access/system_event_port.py`:

- `MarkpointSystemEventEnvelope` (frozen dataclass): `source_event_id`,
  `event_type`, `family_group_id`, `service_principal_id`,
  `approved_room_binding_id`, `occurred_at`, `payload`, `payload_version`.
  `__post_init__` rejects a missing/zero required field, in particular
  `approved_room_binding_id` — no envelope can represent unbound or
  cross-family delivery.
- `idempotency_key` = `f"{event_type}:{source_event_id}"` — one source event
  can never double-publish under retry, even across different in-process
  callers.
- `MarkpointSystemEventPort` (`Protocol`): the abstract `publish()` contract a
  future adapter implements. No implementation in this module talks to a real
  transport.
- `InMemoryMarkpointSystemEventPort`: a contract test double proving dedup and
  required-field behavior with zero DB access and zero Wagle import.

**Why no adapter:** `MONGLE-W2-WAGLE-REALTIME-001` (Wave 3 dispatcher) does
not exist, and Lane A's own Wagle durable-messaging/Outbox extension in this
same session window is `INDEPENDENT_QA_PENDING` — wiring against either would
be building on an unconfirmed interface, which Track B's own instructions
explicitly forbid. A real adapter (Outbox row insert via Lane A's confirmed
interface, or a dispatcher call once Wave 3 lands) is future work.

**Track A dependency:** the eventual adapter task depends on (a) Lane A's
Wagle durable-messaging interface passing independent QA, and (b) Wave 3's
realtime dispatcher (`MONGLE-W2-WAGLE-REALTIME-001`) landing.

## 9. Schema Delta Required

### 9.1 Markpoint activation request (member request → admin approval)

```text
Table: markpoint_activation_requests
Columns:
  id                     integer PK
  family_group_id        integer FK -> family_groups(id) ON DELETE RESTRICT, NOT NULL
  requested_by_membership_id integer FK -> family_memberships(id) ON DELETE RESTRICT, NOT NULL
  status                 varchar(20) NOT NULL DEFAULT 'pending'
  decided_by_account_id  integer FK -> accounts(id) ON DELETE RESTRICT, NULLABLE
  decided_at             timestamptz NULLABLE
  created_at / updated_at timestamptz NOT NULL DEFAULT now()
Constraints:
  CHECK status IN ('pending','approved','rejected')
  Partial UNIQUE (family_group_id) WHERE status = 'pending'
    -- exactly one pending request per family at a time; makes duplicate
    -- request idempotent by returning the existing pending row instead of
    -- inserting a second one.
Why: ServiceSubscription's own state model (D5-A) is only
  INACTIVE/ACTIVE/SUSPENDED -- adding a fourth "pending" value there would
  reopen the frozen D5-A contract. A request is a distinct, audited,
  actor-attributed fact (who asked, when, who decided, when), which the
  existing tables have no column for.
Blocks: the request/approve/reject sub-scope of
  MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001.
Does not block: direct activation, default access, ServiceAdmin
  assign/revoke, System Actor Port contract -- all implemented in this
  session without this table.
```

### 9.2 Per-member Markpoint access restriction

```text
Table: markpoint_access_restrictions
Columns:
  id                integer PK
  family_group_id   integer FK -> family_groups(id) ON DELETE RESTRICT, NOT NULL
  membership_id     integer FK -> family_memberships(id) ON DELETE RESTRICT, NOT NULL
  status            varchar(20) NOT NULL DEFAULT 'restricted'
  reason            text NULLABLE
  actor_account_id  integer FK -> accounts(id) ON DELETE RESTRICT, NOT NULL
  created_at / updated_at timestamptz NOT NULL DEFAULT now()
Constraints:
  CHECK status IN ('restricted','lifted')
  Partial UNIQUE (family_group_id, membership_id) WHERE status = 'restricted'
    -- at most one live restriction per membership; restoring means
    -- flipping status to 'lifted', not deleting the audit row.
Why: D5-B explicitly requires "필요한 구성원별 이용 제한만 명시 정책으로
  적용" (explicit per-member restriction) as a policy distinct from
  ServiceSubscription/Membership state, with its own actor/reason/audit --
  no existing table carries this.
Blocks: individual-restriction sub-scope of
  MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001. `get_access_status()`'s
  `has_default_access` computation in this session does not check
  restriction (there is nothing to check yet) -- this is a known,
  documented gap, not a silent omission.
Does not block: everything else in this session.
```

Both deltas: **no migration was created**, per the parallel-execution rule
that Alembic is Lane A's for this bundle. Recorded here as
`SCHEMA_DELTA_REQUIRED` / `TRACK_B_BLOCKED` for Lane A or a follow-up task to
pick up.

## 10. What Was Implemented and Tested

New domain `backend/app/domains/markpoint_access/` (router/service/schema/
system_event_port), plus `backend/tests/test_markpoint_access_wave4.py` (21
tests) and a 2-line `main.py` router registration.

| Capability | Route / function | Test |
|---|---|---|
| Default access resolution | `GET /api/families/{id}/markpoint/access` | active/inactive subscription, active/suspended membership, unauthenticated denial |
| FamilyAdmin direct activation | `POST /api/families/{id}/markpoint/activate` | success, idempotent (no duplicate subscription row), non-admin denied (403), cross-family denied (403) |
| Registrant/FamilyAdmin not auto-ServiceAdmin | (structural — no code path grants it) | activating admin's own access shows `is_service_admin: false` after activation |
| No Mission-participation side effect | (structural) | activation writes only `service_subscriptions`, asserted directly |
| Explicit ServiceAdmin assign | `POST /api/families/{id}/markpoint/service-admins` | requires ACTIVE subscription (409 before, 201 after), invalid role code rejected (422), non-admin denied (403) |
| Explicit ServiceAdmin revoke | `DELETE /api/families/{id}/markpoint/service-admins/{id}` | access reflects revocation |
| Membership termination revokes ServiceAdmin | (reuses Wave 1 `update_membership`) | `is_service_admin` false after `update_membership(..., "left")` |
| System Actor Port envelope validation | `MarkpointSystemEventEnvelope` | missing source_event_id/family_group_id/service_principal_id/approved_room_binding_id all rejected |
| System Actor Port dedup | `InMemoryMarkpointSystemEventPort.publish` | duplicate `(event_type, source_event_id)` deduplicated; different event types for the same source event are distinct |

## 11. Test Commands and Exact Results

```bash
docker run -d --name mongle-w4-testdb -e POSTGRES_USER=mc_phase2 \
  -e POSTGRES_PASSWORD=*** -e POSTGRES_DB=mc_festival_phase2 \
  -p 15435:5432 postgres:16.9-alpine
# database/init.sql baseline, then:
docker run --rm ... minecraft_points_festivals-backend:latest alembic upgrade head
docker run --rm ... minecraft_points_festivals-backend:latest \
  python -m pytest -q tests/test_markpoint_access_wave4.py -v
```

| Scope | Result |
|---|---|
| `tests/test_markpoint_access_wave4.py` (isolated, `-v`) | **PASS — 21 passed** |
| `alembic current` after setup | `0006_family_service_separation (head)` — single head, unchanged |
| `git diff --check` | clean |

## 12. Regression Result

```bash
docker run --rm ... minecraft_points_festivals-backend:latest python -m pytest -q
```

**145 passed, 0 failed** — 104 Wave 1 + 19 Lane A (Wave 2 Wagle durable
messaging) + 21 this session (Wave 4), plus 1 pre-existing test not previously
recounted in this session's arithmetic (exact figure taken from the actual
run, not derived by addition). No existing test was modified, skipped, or
weakened. No file outside this session's own scope (§5) was touched.

## 13. Self-QA Findings and Fixes

| # | Finding | Disposition |
|---|---|---|
| 1 | Initial design reused the existing generic `/families/{id}/members/{id}/roles` route for ServiceAdmin assign/revoke, assuming it would accept the new Account-native token. It does not — that route still requires a legacy player/admin token (`get_current_user`, pre-dating Wave 1) and returned 401 for an Account-native caller. | **Fixed** — added two new Markpoint-scoped, Account-native-authenticated routes (`POST`/`DELETE /markpoint/service-admins[/{id}]`) that wrap the same underlying `assign_role`/`revoke_assignment` writers. This also matches the parent task's own explicit API list, which names ServiceAdmin assign/revoke as one of Wave 4's minimum routes rather than assuming reuse. |
| 2 | Mid-session PM directive: 3 `Doran`-worded comments in `system_event_port.py`'s current-Target-contract prose. | **Fixed** — reworded to "Wagle"; zero behavior change (docstring/comment-only diff); re-verified by grep and full re-test (§6, §11–12). |
| 3 | A draft test used a dead `if False else None` branch. | **Fixed** before first run — replaced with a direct structural assertion. |

## 14. Recursive Scope Review

**Pass 1 (before):** planned scope = `backend/app/domains/markpoint_access/**`
(new), `backend/tests/test_markpoint_access_wave4.py` (new), `main.py`
(router registration only); explicitly not `active.md`/`relay/current.md`/
migrations/Doran domain code/frontend, per the parallel-execution rules this
session read from `active.md` before starting.

**Pass 2 (after implementation/naming correction):** actual `git status`
shows this session's writes are exactly `backend/app/domains/
markpoint_access/{__init__,router,service,schema,system_event_port}.py`
(new), `backend/tests/test_markpoint_access_wave4.py` (new), and 2 added
lines in `backend/app/main.py`. No Lane A file, no `active.md`, no
`relay/current.md`, no migration file appears in this session's diff.

**Pass 3 (before close):** `git diff --check` clean; naming gate 0/0/0
(§6); 21/21 targeted + 145/145 full-suite tests passed after every edit,
including after the naming correction; DOC_DELTA recorded below rather than
editing shared documents directly; schema blockers recorded rather than
worked around with a migration or a mock.

## 15. Five-Gate Review

- **Gate 1 — 환각:** every claim above carries a file, route, or executed
  test-command result from this session. The naming-gate counts (§6) are
  from an actual re-run `grep`, not asserted from memory.
- **Gate 2 — 누락:** Registrant/Owner/User/ServiceAdmin/ServicePrincipal
  (§7), activation request/approve/reject (blocked, §9.1), direct activation
  (§10), default access (§10), individual restriction (blocked, §9.2), audit
  (`issued_by`/`assigned_by_account_id` reused from Wave 1, unchanged),
  cross-family isolation (§10), System Actor Port (§8) are each addressed.
- **Gate 3 — 오작업:** no `MarkpointParticipant` introduced; no automatic
  FamilyAdmin/registrant ServiceAdmin grant (§10, tested); no Mission
  participation auto-created (§10, tested); no human Membership represented
  as the system actor in the port envelope (§8 — the envelope has no
  Account/Membership field at all); no Wagle DB access, direct or indirect,
  from Markpoint code (`markpoint_access` imports only `app.domains.family`);
  no parallel Alembic head (§5, confirmed by `alembic current`); no Legacy
  data backfill (none of this session's code reads a legacy table).
- **Gate 4 — 축혼동:** this report separates current implementation (§10),
  the approved D5 contract (§7–§9, cited not re-argued), the SCHEMA_DELTA
  blockers (§9) from what is actually built, and explicitly does not build
  Markpoint Mission/Ledger (Wave 5), Wagle realtime/Push (Wave 3), or Legacy
  cutover (Wave 7).
- **Gate 5 — 신선도/오탈자:** `git diff --check` clean; the Markpoint
  ServiceAdmin role codes used (`mission_manager`, `point_admin`) match the
  live `0001` seed exactly (verified by the same names Wave 1's independent
  QA already cross-checked against the Role Matrix); no duplicate Task ID
  introduced; no Doran/doran/도란 in Track-B-owned files (§6).

## 16. Changed-file Manifest

**New:** `backend/app/domains/markpoint_access/__init__.py`,
`backend/app/domains/markpoint_access/router.py`,
`backend/app/domains/markpoint_access/service.py`,
`backend/app/domains/markpoint_access/schema.py`,
`backend/app/domains/markpoint_access/system_event_port.py`,
`backend/tests/test_markpoint_access_wave4.py`,
`agent-system/qa/MONGLE-W4-SERVICE-MARKPOINT-ACCESS-AUTONOMOUS-001.md` (this
file), `agent-system/handoffs/active/MONGLE-W4-SERVICE-MARKPOINT-ACCESS-AUTONOMOUS-001.md`.

**Modified:** `backend/app/main.py` (2 lines: router import + registration).

**Untouched by this session:** everything Lane A touched (§5); `active.md`;
`relay/current.md`; every Alembic migration; every Markpoint product domain
(`mission`, `daily_point`, `deduction`, `cheer`, `feedback`, `notification`,
`level_tier`, `admin` — Wave 5 scope, not this session's); all frontend
source; `database/init.sql`.

## 17. DOC_DELTA (for Lane A or a follow-up integration task to apply)

```text
Table Dictionary:
No new table exists yet (both proposed tables are SCHEMA_DELTA_REQUIRED, §9).
When a migration is authorized, add `markpoint_activation_requests` and
`markpoint_access_restrictions` per the exact columns/constraints in §9.

Column Dictionary:
Same — no live columns to document yet.

API Inventory:
Add three new routes under the Markpoint/service-ownership section:
  GET    /api/families/{family_id}/markpoint/access
  POST   /api/families/{family_id}/markpoint/activate
  POST   /api/families/{family_id}/markpoint/service-admins
  DELETE /api/families/{family_id}/markpoint/service-admins/{assignment_id}
All four: Account-native auth (`get_current_account`/`require_family_permission`),
family-scoped per D7, `family.services.manage` permission for activate/
service-admins routes, ACTIVE-membership-only for the access read.

Role Matrix:
No new role/permission code was added. Existing `mission_manager`/
`point_admin` (SERVICE, service_code=markpoint) are the only ServiceAdmin
roles this session's routes accept; both already exist in the live `0001`
seed, unchanged.

Implementation Backlog:
MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001 -> suggest `PARTIALLY_IMPLEMENTED`
(not `DONE`): direct activation/default access/ServiceAdmin done; request/
approve/reject and restriction blocked on SCHEMA_DELTA (§9).
MONGLE-W4-MARKPOINT-SYSTEM-EVENT-RELAY-001 -> suggest recording the port
contract as `CONTRACT_DEFINED_ADAPTER_PENDING`, still `BLOCKED_BY_DEPENDENCY`
on Wave 3.

DoD/Test Matrix:
Record the 21 new tests in `test_markpoint_access_wave4.py` against
MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001's DoD row; note request/approve/reject
and restriction test cases remain unwritten pending the schema delta.

Coverage Map:
Suggested new row: `API-W4-MARKPOINT-ACCESS-001` | API/DB | Markpoint direct
activation, default access, ServiceAdmin assign/revoke | Family service
access | Critical | L4 | COVERED (partial scope) | `backend/tests/
test_markpoint_access_wave4.py` | 2026-08-01 | PASS: 21/21 (suite total
145/145) | CONFIRMED | SCHEMA_DELTA_REQUIRED (activation-request/restriction
sub-scope) | Wave 4. No MarkpointParticipant; no auto ServiceAdmin; System
Actor Port is contract-only pending Wave 3.
```

## 18. Final Verdict

```text
TRACK_B_WAGLE_NAMING_CONTRACT_PASS
TRACK_B_IMPLEMENTATION_COMPLETE
TRACK_B_PARTIALLY_COMPLETE
SCHEMA_DELTA_REQUIRED
TRACK_B_TESTS_PASS
TRACK_B_SELF_QA_COMPLETE
PARENT_BUNDLE_IN_PROGRESS
INTEGRATION_QA_PENDING
```

Parent-bundle completion is not claimed. Both lanes require independent QA
before `MONGLE-PARALLEL-W2-W4-001` can graduate.
