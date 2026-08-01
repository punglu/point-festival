# MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001

- Task ID: `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001`
- Kind: execution bundle — an identifier for one single-writer session, not a new product task. It executes six existing Wave 1 Backlog tasks and does not replace their IDs.
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `da7ea7403aefef33a90d622940724b0c53ee8873` (unchanged start → end)
- environment: local worktree, branch `dev-newmarkp`; tests executed against a disposable, volume-less PostgreSQL 16.9 container on `127.0.0.1:15435`
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
WAVE_1_IMPLEMENTATION_COMPLETE
WAVE_1_TESTS_PASS
WAVE_1_QA_CONDITIONAL
NOT_READY_FOR_WAVE_2
```

All six Wave 1 Backlog tasks are implemented and pass their own tests: 33 new
tests, 104/104 across the whole backend suite, zero regressions. Account-native
login, persistent Session with refresh rotation, device unlink, scoped RBAC and
FamilyAdmin account issuance all work with **no legacy identity involved** —
the central D8 RESET requirement, asserted directly rather than argued.

The verdict is `CONDITIONAL` rather than full `QA_PASS` for two honest reasons,
neither of which is a defect in the delivered code:

1. **Independent QA has not run.** `rules.md` Invariant 6 is explicit that an
   implementing session cannot award its own final QA PASS. Everything below is
   self-check evidence.
2. **A real security defect was found in pre-existing seed data and fixed**
   (§6). That fix changes the RBAC registry, which is exactly the class of
   change the repository requires independent review for.

## 2. Environment / Git Baseline

| Measurement | Start | End |
|---|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` | same |
| `git branch --show-current` | `dev-newmarkp` | `dev-newmarkp` |
| `git rev-parse HEAD` | `da7ea7403aefef33a90d622940724b0c53ee8873` | identical |
| `git diff --check` | clean | clean |
| commit / push / merge / rebase / PR | — | **none performed** |

## 3. Starting Dirty Preservation

28 modified tracked files and 65 untracked entries existed at start, owned by
prior sessions. None was reset, restored, checked out, cleaned or stashed. The
only pre-existing dirty file this bundle wrote to is
`agent-system/qa/COVERAGE_MAP.md`, where three rows were **appended** without
altering the other task's in-flight content — required by `TEST_POLICY.md`
because this bundle added real tests.

## 4. Authoritative Inputs

`MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 APPROVED/FROZEN),
`MONGLE_TARGET_TABLE_DICTIONARY.md`, `MONGLE_TARGET_COLUMN_DICTIONARY.md`,
`MONGLE_TARGET_API_INVENTORY.md`, `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md`,
`MONGLE_IMPLEMENTATION_BACKLOG.md`, `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`,
`MONGLE_DOD_AND_TEST_MATRIX.md`, `MONGLE_DATA_NAMING_CONTRACT_V0_1.md` (§3
naming principles), `engineering/BACKEND_GUIDE.md`,
`agent-system/qa/TEST_POLICY.md`, `tests/README.md`, plus direct reads of
`family/models.py`, `family/service.py`, `auth/models.py`, `auth/service.py`,
`auth/dependencies.py`, `app/models/base.py`, `backend/tests/conftest.py` and
migrations `0000`–`0004`.

## 5. Phase 1B — DB Contract Result

Converted the historical Credential/Session sketches into a real schema. Key
decisions and why:

- **Placement in the `family` domain.** `Account` already lives in
  `family/models.py`; this avoids creating a new directory, keeps the existing
  one-directional `family → auth` import graph acyclic, and satisfies
  BACKEND_GUIDE's "one `router.py` per domain". `family/router.py` already
  serves the non-family path `/api/account-context`, so Account-level routes
  there follow existing practice.
- **Device as a column, not an aggregate.** `account_sessions.device_id` with an
  `(account_id, device_id)` index makes unlink a bulk revoke. A separate
  `account_devices` table would have been the larger structure the prompt warns
  against, and nothing is foreclosed: a future Wagle PIN or Push-subscription
  table can attach to the same stable key.
- **Partial unique indexes on `deleted_at IS NULL`** for both one-live-credential
  -per-Account and username uniqueness, so a *revoked* username stays reserved
  rather than becoming re-registrable by someone else.
- **`refresh_token_hash` globally unique** across live and revoked rows, so a
  replayed token resolves to its revoked row and is explicitly rejected instead
  of silently not matching.
- **Config SSOT.** Hashing, lockout threshold, lock duration, token TTLs and
  initial-password length are all in `backend/app/config.py`; no literal is
  duplicated in domain code.

Naming follows `MONGLE_DATA_NAMING_CONTRACT_V0_1` §3 throughout: `id` PK,
`<entity>_id` FKs, `is_*` booleans, `*_at` timestamps with `locked_until` as the
documented deadline exception, `status` as a CHECK-constrained string rather
than a native enum, `TimestampMixin`/`SoftDeleteMixin`.

## 6. Phase 1C — Scoped RBAC Result, including a real defect found

Most of the RBAC surface already existed and was correct
(`effective_permissions` with subscription gating, `get_active_membership`,
`_active_owner_count` + `_lock_family_for_owner_change`, issuer audit columns).
Two things were genuinely missing or wrong:

**Added — roles now end when the Membership ends.** `update_membership()` now
revokes the membership's live role assignments in the same transaction as a
transition to `suspended`/`left`/`removed`. The gate already denied such a
membership, so this is defence in depth — but it makes the invariant durable in
the data rather than dependent on every future caller going through one gate.

**Fixed — FamilyAdmin was silently a Markpoint ServiceAdmin.** The `0001` seed
granted `markpoint.missions.manage` and `markpoint.points.adjust` to the
FAMILY-scope `admin` role directly, and to `owner` via a `CROSS JOIN` over every
permission. That violates D4/D5 ("ServiceAdmin authority exists only where
explicitly assigned"). Worse, because the grants hung off *FAMILY*-scope roles,
`effective_permissions()` skipped the Markpoint `ServiceSubscription` check,
which it applies only to SERVICE-scope roles — so the authority also bypassed
the entitlement gate.

Found by this Wave's own separation test, not by inspection. Removed in
migration `0006_family_service_separation`.

Impact was **verified nil rather than assumed**: `grep` over `backend/app/`
confirms no product code references either permission code today — every
Markpoint route still authorizes through legacy
`require_admin`/`get_current_player`. The defect would have become a live
privilege escalation at the Wave 4/5 Markpoint authorization TRANSFORM.
`markpoint.own.read` on `member`/`restricted_member` was deliberately **left
alone** and flagged for Wave 4: it is self-read, not administration, and
whether a family role should carry it is a D5-B question this Wave does not own.

## 7–10. Credential / Session / Route AuthZ / Issuance Results

- **Credential (1D):** bcrypt hashing, normalized case-insensitive username,
  status + lockout, initial-credential state, `password_changed_at`, issuer
  audit. Unknown-username and wrong-password responses are byte-identical to
  block user enumeration.
- **Session (1E):** Account-scoped persistent Session; rotation revokes the
  presented row and issues a new one in one transaction; a revoked Session is
  rejected immediately even while its access token is still within TTL, because
  the dependency validates the Session row per request. Access tokens carry
  `role="account"`, which the legacy dependencies reject and which the Account
  dependency requires — neither token type works against the other's routes.
- **Route AuthZ (1F-1):** `require_family_permission()` resolves the Account,
  revalidates ACTIVE membership **in the path family**, then checks the
  permission. `ActiveFamilyContext` has no representation anywhere — no column,
  no parameter, no input to any decision.
- **Issuance (1F-2):** Account + Membership + Credential in one transaction, so
  a duplicate username leaves no stranded Account. Initial password returned
  exactly once and stored only as a bcrypt hash.

## 11. Migration Manifest

| Revision | Parent | Contents |
|---|---|---|
| `0005_account_credential_session` | `0004_doran_reliable_slice` | `account_credentials`, `account_sessions`, 4 indexes, 3 CHECK constraints, seeds `family.members.provision` and grants it to FAMILY `owner`/`admin` |
| `0006_family_service_separation` | `0005_account_credential_session` | Removes `markpoint.missions.manage`/`markpoint.points.adjust` from every FAMILY-scope role |

Both create **no** operational data and read **no** legacy row (D8 RESET).

Verified by execution, not by reading: `0000→0006` applies to a fresh database;
`downgrade -1` then `upgrade` leaves zero residue (both tables absent and the
seeded permission gone after downgrade, restored after upgrade).

**A migration defect was caught by measuring rather than trusting the log.**
The first `0006` revision id was 36 characters, exceeding
`alembic_version.version_num varchar(32)`. Alembic printed `Running upgrade
0005 -> 0006` and then rolled the whole transaction back at the version update.
Checking the actual `alembic_version` row and the actual permission rows — not
the log line — exposed it. Renamed to `0006_family_service_separation` (30
chars) with an inline comment recording the limit.

## 12. API Manifest

8 new routes: `POST /api/auth/account/{login,refresh,logout}`,
`GET /api/me`, `POST /api/me/password`, `GET /api/me/sessions`,
`DELETE /api/me/devices/{device_id}`,
`POST /api/families/{family_id}/member-accounts`. No existing route was
modified; legacy `/api/auth/*` is untouched.

## 13. Test Changes

One new file, `backend/tests/test_account_auth_wave1.py`, 33 tests. **No
existing test was deleted, skipped, disabled, or weakened**; the pre-existing 71
were run unmodified.

## 14. Test Commands and Exact Results

```
docker run --rm --network container:mongle-w1-testdb -v $PWD/backend:/app -w /app \
  -e DATABASE_URL=postgresql+asyncpg://mc_phase2:***@127.0.0.1:5432/mc_festival_phase2 \
  <backend-image> sh -c "pip install -q pytest pytest-asyncio httpx; python -m pytest -q"
```

| Scope | Result |
|---|---|
| `tests/test_account_auth_wave1.py` | **PASS — 33 passed** |
| Full `backend/tests` suite | **PASS — 104 passed, 0 failed** (33 new + 71 pre-existing) |
| `alembic upgrade head` from empty DB (`0000`→`0006`) | **PASS** |
| `alembic downgrade -1` → `upgrade head` | **PASS**, zero residue verified by direct SQL |
| Schema/constraint/index/seed introspection | **PASS**, matches the Column Dictionary exactly |

Two failures occurred during development and were resolved before this report:
one was the real seed defect in §6; one was my own over-broad assertion
(`"password" not in response`, which the legitimate field name
`is_password_change_required` trips). The assertion was made **more** precise —
it now asserts the actual secret values and hashes are absent — not weakened.

## 15. Not-run Tests and Reasons

| Test | Status | Reason |
|---|---|---|
| Frontend lint / build | `NOT_RUN` | No frontend source was touched by this bundle. |
| Playwright E2E (`specs-mongle`) | `NOT_RUN` | Exercises legacy PIN login screens; no FE consumer of the new Account routes exists yet (that is Wave 1's FE slices, still `BLOCKED_BY_DEPENDENCY`). Running it would prove nothing about this change. |
| `tests/api/*.sh`, `e2e_scenario_test_v2.py` | `NOT_RUN` | Target the `mc_phase0` legacy runtime and legacy routes; unrelated to Account-native auth. |
| Physical device / PWA / Push | `NOT_RUN` | `HUMAN_GATE`, unchanged. |

**Environment note, reported rather than worked around:**
`backend/tests/conftest.py` targets `127.0.0.1:15435` (`mc_phase2`) but
`docker-compose.phase2.yml` **does not exist in this repository** — the suite has
no committed way to start its own database. The running `mc-db` on 5433 is the
default Compose dev runtime with a persistent volume, so `TEST_POLICY.md`
classifies it `UNSAFE_ON_SHARED_DB` and it was **not** used. This bundle
provisioned its own disposable volume-less container instead. Committing a
`docker-compose.phase2.yml` is a real gap but belongs to a test-infrastructure
task, not to this one.

## 16. Self-QA Findings and Fixes

| # | Finding | Disposition |
|---|---|---|
| 1 | FamilyAdmin auto-granted Markpoint ServiceAdmin authority (pre-existing `0001` seed) | **Fixed** — migration `0006`; impact verified nil today |
| 2 | Revision id exceeded `varchar(32)`, silently rolling back `0006` | **Fixed** — renamed; caught by checking DB state, not the log |
| 3 | Roles survived Membership termination in the data | **Fixed** — revoked in the same transaction |
| 4 | Own test assertion too broad (`"password"` substring) | **Fixed** — made stricter, not weaker |
| 5 | `markpoint.own.read` still on FAMILY member roles | **Not fixed, flagged** — D5-B default-access question owned by Wave 4 |

## 17. Regression Result

104/104 pass. The 71 pre-existing tests (Doran integration, service binding,
reliable service slice, weekly) were run unmodified and all pass. No existing
route, model, or migration was altered.

## 18. Recursive Scope Review

- **Pass A (before):** planned `family/**`, new migrations, `all_models.py`, `config.py`, `backend/tests/**`, and the Target dictionaries — declared in `relay/current.md`.
- **Pass B (after implementation):** `git diff --stat` shows exactly 6 modified + 5 new files, all inside the declared scope. No Doran, Markpoint, frontend, `init.sql`, or existing-migration file was touched.
- **Pass C (after tests):** no test-driven shortcut was taken; documentation matches the shipped schema (verified by introspecting the live DB against the Column Dictionary); no TODO left behind.

## 19. Five-Gate Review

- **Gate 1 — 환각:** every claim carries a file, migration, command or SQL result. The one place a log message contradicted reality (the `0006` rollback) was caught by measuring the database. No unrun test is reported as PASS.
- **Gate 2 — 누락:** Credential, Session, refresh rotation, device unlink, AuthorizedFamilySet, ActiveFamilyContext non-authority, scoped RBAC, last-admin, cross-family denial, route authorization, FamilyAdmin issuance, audit, migration, tests and documentation are each addressed above.
- **Gate 3 — 오작업:** no legacy backfill; `LegacyIdentityMapping` is not on any Target login path; no plaintext password or token is stored; FamilyAdmin cannot impersonate or re-read a password; the FamilyAdmin→ServiceAdmin auto-grant was **removed**; `ActiveFamilyContext` is not an authorization source; one membership ending does not end the Account Session; no dirty file was cleaned.
- **Gate 4 — 축혼동:** current-implementation fact, approved contract, this Wave's output, deferred policy and legacy reference are labelled separately throughout. Only Platform Account/Auth/Family/RBAC was implemented — no Wagle, Markpoint, cutover or PIN work.
- **Gate 5 — 신선도:** Table/Column Dictionary, API Inventory, Role Matrix, Implementation Backlog and Coverage Map updated to match the shipped code; `git diff --check` clean; no duplicate Task ID introduced (the bundle id is registered as a bundle, not a product task).

## 20. Changed File Manifest

**Modified (6):** `backend/app/config.py`,
`backend/app/domains/family/{models,router,schema,service}.py`,
`backend/app/models/all_models.py`

**New (5):** `backend/alembic/versions/0005_account_credential_session.py`,
`backend/alembic/versions/0006_family_service_separation.py`,
`backend/app/domains/family/auth_service.py`,
`backend/app/domains/family/dependencies.py`,
`backend/tests/test_account_auth_wave1.py`

**Docs/records:** `engineering/phase2/MONGLE_TARGET_{TABLE,COLUMN}_DICTIONARY.md`,
`MONGLE_TARGET_API_INVENTORY.md`, `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md`,
`MONGLE_IMPLEMENTATION_BACKLOG.md`, `agent-system/qa/COVERAGE_MAP.md`,
`agent-system/active.md`, `agent-system/relay/current.md`, this file.

## 21. Existing Dirty / Other-task Files

The 28 pre-existing modified files and 65 untracked entries remain exactly as
found. `COVERAGE_MAP.md` was appended to (three rows) as required by
`TEST_POLICY.md`; no other task's content in it was altered.

## 22. Residual Risks

1. **Independent QA has not run** on a security-boundary change. Mandatory before any completion or push claim.
2. **The RBAC seed correction (`0006`) changes an existing registry.** Verified to have no current product impact, but it should be reviewed on that basis specifically.
3. **No FE consumer exists**, so the Account routes are proven only at the API/DB layer — real browser behaviour is unverified.
4. **`docker-compose.phase2.yml` is missing**, so the test suite cannot start its own DB from the repository alone.
5. **Legacy auth remains fully live.** `resolve_current_account` and the legacy `/api/auth/*` routes are untouched by design; retiring them is Wave 7, not Wave 1.
6. **`markpoint.own.read` on FAMILY member roles** is unresolved and flagged for Wave 4.

## 23. Follow-up Tasks

- Independent QA of Wave 1 (security/DB/authorization boundaries).
- A test-infrastructure task to commit `docker-compose.phase2.yml`.
- Wave 4: decide `markpoint.own.read`'s placement under D5-B default access.
- The five Wave 1 FE slices, each at its own Start Gate.

## 24. Final Verdict

```text
WAVE_1_IMPLEMENTATION_COMPLETE
WAVE_1_TESTS_PASS
WAVE_1_QA_CONDITIONAL
NOT_READY_FOR_WAVE_2
```

Wave 2 requires independent QA of this Wave first: it authorizes every
subsequent Wave against the security dependency built here.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/qa/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: three new source-backed rows for real executed tests.
- CLOSEOUT GATE: `PASS`

`CLOSEOUT GATE: PASS` means the four documentation obligations are
synchronized. It is not independent QA, PM approval, graduation, or push
authorization.
