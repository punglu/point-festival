# MONGLE-W1-INDEPENDENT-QA-001

- Task ID: `MONGLE-W1-INDEPENDENT-QA-001`
- Kind: independent QA / test / minimal defect correction
- Execution Target: `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` (six Wave 1 Backlog tasks)
- author/agent: `Claude Code` (independent QA session — no memory of, and no reuse
  of, the implementing session's process; only its committed artifacts were read)
- observed_at: `2026-08-01`
- git_ref: `da7ea7403aefef33a90d622940724b0c53ee8873` (unchanged start → end)
- environment: local worktree, branch `dev-newmarkp`; migrations and tests run
  against a disposable, volume-less PostgreSQL 16.9-alpine container on
  `127.0.0.1:15435`, torn down at teardown (`docker rm -f`, confirmed zero
  residual container/volume)
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
WAVE_1_INDEPENDENT_QA_PASS
WAVE_1_LIFECYCLE_COMPLETE
READY_FOR_WAVE_2_START_REVIEW
```

Every claim in `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001`'s own report was
independently re-measured from source, not accepted from its log or prose.
All six Wave 1 Backlog tasks' requirements hold under direct code read, live
migration reproduction, and an independently-run test suite (104/104,
reproduced from a **freshly created** disposable database, not the
implementer's leftover environment). No new defect was found; the one defect
the implementing session already found and fixed (§9 below) was independently
confirmed fixed, not merely re-read as claimed.

## 2. Environment / Git Baseline

| Measurement | Start | End |
|---|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` | same |
| `git branch --show-current` | `dev-newmarkp` | `dev-newmarkp` |
| `git rev-parse HEAD` | `da7ea7403aefef33a90d622940724b0c53ee8873` | identical |
| `git diff --check` | clean | clean |
| commit / push / merge / rebase / PR | — | **none performed** |

Start dirty state: 34 modified tracked files (28 pre-existing + the Wave 1
bundle's 6 backend modifications) plus untracked entries, all pre-existing.
None was reset/restored/checked out/cleaned/stashed. This QA session's own
writes: `agent-system/active.md`, `agent-system/relay/current.md`,
`agent-system/qa/COVERAGE_MAP.md` (three Notes cells appended, no other
content altered), and this file.

## 3. Active Writer State

`agent-system/active.md` / `agent-system/relay/current.md` showed no other
open writer for this scope at start (`relay/current.md`'s "Current Task: none"
— the prior bundle had released its claim). This task registered itself in
both files before any code read, declaring the same allowed/forbidden scope
as the implementing bundle plus this QA task's own evidence files.

## 4. Authoritative Inputs

Read directly, not recalled: `AGENTS.md`, `agent-system/rules.md`,
`agent-system/active.md`, `agent-system/relay/current.md`,
`agent-system/qa/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md`,
`agent-system/handoffs/active/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md`,
`engineering/phase2/MONGLE_TARGET_TABLE_DICTIONARY.md`,
`MONGLE_TARGET_API_INVENTORY.md`, `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md`,
`agent-system/qa/TEST_POLICY.md`, `agent-system/qa/COVERAGE_MAP.md`, plus
direct source reads of `family/{models,service,router,schema,auth_service,
dependencies}.py`, `app/dependencies.py`, `app/database.py`, `app/config.py`,
`app/models/all_models.py`, `backend/tests/{conftest.py,
test_account_auth_wave1.py}`, `backend/alembic/versions/{0000,0005,0006}*.py`,
and `database/init.sql`.

## 5. Wave 1 Changed-file Manifest (independently re-extracted)

`git diff --stat -- backend/` measured directly:

```text
backend/app/config.py                 |  11 +
backend/app/domains/family/models.py  |  68 +
backend/app/domains/family/router.py  | 148 ++ (imports widened, no existing route body changed)
backend/app/domains/family/schema.py  |  78 +
backend/app/domains/family/service.py | 128 ++ (one line replaced, in-scope refactor)
backend/app/models/all_models.py      |   5 + (import list only)
6 files changed, 429 insertions(+), 9 deletions(-)
```

Plus new, untracked: `backend/alembic/versions/0005_account_credential_session.py`,
`0006_family_service_separation.py`, `backend/app/domains/family/auth_service.py`,
`backend/app/domains/family/dependencies.py`,
`backend/tests/test_account_auth_wave1.py`. This matches the implementer's
manifest exactly (6 modified + 5 new).

`git diff backend/app/domains/family/router.py | grep '^-' ` shows the only
removed lines are import-list lines (widened, not narrowed) — no existing
route handler body was touched. `models.py`/`config.py` diffs show **zero**
removed lines (pure additions). No Doran, Markpoint, frontend, `init.sql`, or
`0000`–`0004` migration file appears in any diff.

## 6. DB Model Review

Read directly against `MONGLE_TARGET_COLUMN_DICTIONARY.md` and the live
schema (§7): `AccountCredential` and `AccountSession` in
`family/models.py` carry every field the QA task's own checklist requires —
Account FK, normalized login identifier, partial-unique active-credential
constraint, password hash only, status + `is_initial_credential`/
`is_password_change_required`, `failed_attempt_count`/`locked_until`,
`issued_by_account_id`, `revoked_at`, `password_changed_at`,
`created_at`/`updated_at`, soft-delete on the credential (not the session, by
design — a session is revoked, not soft-deleted). No plaintext password
column exists anywhere in the model or the live table (§7). `AccountSession`
carries `refresh_token_hash` (SHA-256, never the raw token), `device_id`,
`issued_at`/`expires_at`/`last_seen_at`/`revoked_at`/`revoked_reason`, and
`rotated_from_session_id` for the rotation chain.

## 7. Migration 0005 Review — independently reproduced, not read

Commands actually run (not paraphrased from the implementer's report):

```bash
docker run -d --name mongle-w1qa-testdb -e POSTGRES_USER=mc_phase2 \
  -e POSTGRES_PASSWORD=phase2-local-only-not-production \
  -e POSTGRES_DB=mc_festival_phase2 -p 15435:5432 postgres:16.9-alpine
docker exec mongle-w1qa-testdb psql -U mc_phase2 -d mc_festival_phase2 -f /init.sql   # legacy baseline (0000 is a no-op stamp)
docker run --rm ... minecraft_points_festivals-backend:latest alembic upgrade head
```

Result: `0000 → 0006` applied cleanly on a database seeded only from
`database/init.sql` (never a legacy dump). `\d account_credentials` and
`\d account_sessions` against the **live** database (not the model source)
show exactly the columns above, plus:

- Indexes: `uq_account_credentials_username` (unique, `WHERE deleted_at IS
  NULL`), `uq_account_credentials_account` (unique, same predicate),
  `uq_account_sessions_refresh_token_hash` (unique), `ix_account_sessions_
  account_device` (btree) — **4 indexes**, matching the implementer's count.
- Check constraints: `ck_account_credentials_status`,
  `ck_account_credentials_failed_attempt_count`,
  `ck_account_sessions_revoked_reason` — **3 CHECK constraints**, matching.
- Seed: `family.members.provision` inserted and granted to exactly `(FAMILY,
  owner)` and `(FAMILY, admin)` — confirmed by direct SQL join, not by reading
  the migration file's SQL string.

## 8. Migration 0006 Review — independently reproduced

Direct SQL before/after, not log inspection:

```text
Before 0006 (pre-existing 0001 seed): FAMILY owner/admin hold
  markpoint.missions.manage / markpoint.points.adjust.
After 0006 (fresh 0000->head): those FAMILY-scope grants are absent;
  only SERVICE-scope mission_manager/point_admin still hold them.
downgrade -1 (0006->0005): the FAMILY owner/admin grants are RESTORED
  (6 rows: 2 FAMILY x 2 permissions + 2 SERVICE rows), confirming
  reversibility restores the pre-existing (contract-violating) state
  by design, not a bug.
upgrade head again: FAMILY grants removed again, 4 rows remain total
  (2 SERVICE + 2 family.members.provision), zero duplicates
  (`GROUP BY ... HAVING count(*) > 1` on permissions: 0 rows).
downgrade all the way to 0004: account_credentials/account_sessions
  tables and the family.members.provision permission row are gone
  (`\dt` returns "Did not find any relation").
upgrade head from 0004: reaches 0006_family_service_separation (head)
  again, byte-for-byte the same seed state as the first fresh upgrade.
```

The revision id `0006_family_service_separation` is 30 characters —
independently counted, under the `alembic_version.version_num varchar(32)`
limit the implementer's report flagged as a prior defect they caught and
fixed. No rollback-on-truncation recurred in this independent run.

`markpoint.own.read` (left alone by design, per the report) is present on
`(FAMILY, member)`, `(FAMILY, restricted_member)`, `(FAMILY, owner)` and
`(SERVICE, participant)`. **Correction to the implementer's report**: it
states this permission remains "on the FAMILY `member`/`restricted_member`
roles" but omits that `owner` also carries it (pre-existing `0001` seed
behavior, unchanged by Wave 1). This is a documentation-precision gap, not a
defect — `owner` already implicitly has broader authority, and this permission
code's placement is explicitly deferred to Wave 4's D5-B decision either way.
Not corrected in this task because D5-B is out of Wave 1's defect-correction
scope and no approved contract is violated.

## 9. Credential QA

Reproduced live (HTTP + DB), not accepted from the report:

- Login with **zero** `legacy_identity_mappings` rows anywhere for the
  account (`test_login_succeeds_with_no_legacy_identity_at_all`, independently
  re-run — passed).
- Wrong password increments `failed_attempt_count`; lockout at
  `ACCOUNT_MAX_LOGIN_ATTEMPTS` returns 423 even with the correct password
  while locked.
- Unknown-username and wrong-password responses are byte-identical (401,
  same `detail` string) — confirmed by direct diff of both JSON bodies in the
  test.
- `password_hash` is bcrypt (`$2` prefix); the raw password is not a substring
  of any column value on the row, checked against every column via
  `mappings().one()`, not just the hash column.
- Duplicate username rejected case-insensitively (409) at the service layer.
- Disabled credential rejected (403) even with the correct password.
- Password change revokes **every** existing Session including the one used
  to make the change (both prior tokens independently confirmed 401 after).

`grep -rniE "print\(.*password|log.*password|logger.*password"` over `app/`
found nothing; the only middleware registered in `app/main.py` is CORS — no
request-body logging middleware exists that could leak a password in transit.

## 10. Session Security QA

- **Refresh rotation + replay rejection**: independently re-run
  (`test_refresh_rotates_and_old_refresh_token_replay_is_rejected`) — rotating
  returns a new token different from the old one; replaying the old token
  returns 401. Code-level confirmation: `refresh_session()` revokes the
  presented row in the same transaction as issuing the new one (single
  `db.commit()`), so no window exists where the old token is still valid
  after a successful rotation.
- **Revoked session rejected while the access token is still unexpired**:
  confirmed both by test and by reading `load_active_session()`, which checks
  the DB `revoked_at` column on every request rather than trusting the JWT's
  own `exp` claim alone — this is what makes the Session durable rather than a
  bare stateless token.
- **Device unlink** revokes every live session for exactly one
  `(account_id, device_id)` pair; a second device is unaffected (confirmed by
  test and by the `unlink_device()` SQL `UPDATE ... WHERE account_id=... AND
  device_id=...`).
- **Token boundary**, confirmed by reading both sides of the code, not just
  one: `auth_service.decode_access_token()` rejects any token whose `role`
  claim is not `"account"` (401). `app/dependencies.py::get_current_user()`
  (the legacy dependency used by every `/api/auth/*`, mission, daily-point,
  etc. route) rejects any token whose `role` is not in `{"player", "admin"}`
  (401). Since an Account-native token carries `role="account"` and a legacy
  token carries `role="player"`/`"admin"`, **neither token type can ever
  satisfy the other's dependency** — verified structurally in both files, and
  the account-token → legacy-route direction (the JWT secret is shared, so
  only the `role` claim is the actual boundary) is not currently covered by
  an executed test; recorded as a minor test-coverage gap, not a defect.
- **Malformed/missing token** rejected (401) — `test_missing_and_malformed_
  tokens_are_rejected`, re-run independently.
- **Expired session** rejected (401) even though only the DB row's
  `expires_at` was mutated, not the JWT.

## 11. AuthorizedFamilySet / Multi-family QA

Independently re-run:

- `test_authorized_family_set_lists_every_active_membership`: an Account with
  ACTIVE memberships in two independently-created families sees both in
  `/api/me`.
- `test_ending_one_membership_keeps_the_account_session_and_other_family`:
  ending Family A's membership removes only Family A from the authorized set;
  the Account's Session and Family B access are untouched — this is the exact
  "one membership ending must not end the Account Session" invariant the QA
  task requires, and it is enforced structurally (`AccountSession` has no FK
  to `FamilyMembership` at all — there is no column to invalidate).
- `test_inactive_family_is_excluded_from_the_authorized_set`: a `closed`
  FamilyGroup drops out of the set even with an otherwise-active membership.
- Cross-family route denial independently re-run (§13).

## 12. ActiveFamilyContext QA

`grep -rniE "active_family|current_family|selected_family|family_context"`
over the entire `backend/app/` tree returned **zero matches**. There is no
column, JWT claim, session field, or request parameter representing a
client-selected "current family" anywhere in the implementation — `family_id`
is read from the route path on every request and revalidated against live
Membership/Role data (`get_family_membership`, `require_family_permission`).
Because no such state exists server-side at all, the multi-tab isolation
requirement is satisfied by construction: two tabs selecting different
families produce two independent requests, each carrying its own path
`family_id`, each independently revalidated — there is nothing for one tab's
selection to leak into the other. This is a Backend-contract-level
verification per the task's own scope note; no frontend "current family"
selector exists yet to test at the browser level (Wave 1 has no FE consumer).

## 13. Scoped RBAC QA

Independently re-run, plus direct SQL:

- Default deny / cross-family deny: `test_family_route_denies_a_non_member`,
  `test_family_route_denies_cross_family_access` (an admin of Family A gets
  403 on Family B by substituting the id) — both re-run, passed.
- Suspended membership denied: `test_family_route_denies_a_suspended_
  membership` — re-run, passed.
- Unauthenticated denied (401): `test_family_route_requires_authentication`.
- **Last-admin protection**: `test_last_owner_cannot_be_deactivated` — the
  sole owner's membership cannot transition to `removed` (409). Code review of
  `update_membership()`/`revoke_assignment()` shows the same
  `_active_owner_count() <= 1` guard, under a `SELECT ... FOR UPDATE` row
  lock on the FamilyGroup, applied to both the membership-termination path and
  the direct role-removal path — a caller cannot bypass the guard by revoking
  the `owner` role assignment instead of terminating the membership.
- **Role ends when Membership ends**: `test_membership_termination_revokes_
  its_role_assignments` — re-run; `revoke_membership_roles()` is called in the
  same transaction as the status transition (`update_membership()`), so this
  is a data-level invariant, not just a gate-time check.
- **FamilyAdmin gets no automatic ServiceAdmin authority**:
  `test_family_admin_gets_no_automatic_service_admin_authority` — re-run;
  independently cross-checked against the live seed in §8 (FAMILY admin holds
  `family.members.provision` but not `markpoint.points.adjust`).
- `family.members.provision` cross-checked as identical across Role Matrix
  doc, migration `0005` SQL, and the live `role_permissions` table (§7) — one
  source of truth, no duplicate hardcoding found via `grep -rn
  "family.members.provision" backend/app/`.
- Audit: `test_role_assignment_records_its_issuer_for_audit` confirms
  `assigned_by_account_id` is populated; `AccountCredential.issued_by_
  account_id` is the equivalent for credential issuance (§14).

## 14. Route Authorization QA

The 8 new routes were exercised at the real HTTP layer (`httpx.AsyncClient`
against the actual ASGI app, not a mocked client) by the independently-run
test suite. Status codes cross-checked against `MONGLE_TARGET_API_INVENTORY.md`:
401 for missing/invalid Session, 403 for a real-but-unauthorized Account
(non-member, wrong family, suspended membership, insufficient permission),
409 for state conflicts (duplicate username, last-owner). No 404 case is
routed through `require_family_permission` (a non-existent `family_id` also
resolves as "no active membership" → 403, which is the deliberate
default-deny choice — it does not leak whether the family exists to a
non-member, which is a stronger information-boundary result, not a policy
violation. `get_family()` used by the pre-existing family CRUD routes returns
404 for a truly missing family, unaffected by Wave 1).

Thin Controller check: every one of the 8 new route handlers in `router.py`
calls into `auth_service` or `service`; **zero** direct `db.execute`/`select`
calls appear inside any of them (confirmed by `grep -n
"select(\|db.execute(" router.py` and manually excluding the two matches,
both of which are in the pre-existing `list_members`/`list_role_assignments`
handlers that Wave 1 did not touch — confirmed via `git diff` showing no
changed lines in that region).

## 15. FamilyAdmin Issuance QA

Independently re-run:

- `test_family_admin_provisions_a_working_independent_account`: the issued
  Account can immediately log in with the returned one-time password, lands
  in exactly the issuing family, and is a distinct Account id from the issuer.
- `test_issued_initial_password_is_only_a_hash_afterwards`: the stored
  `password_hash` is never equal to the plaintext initial password;
  `issued_by_account_id` records the FamilyAdmin.
- `test_plain_member_cannot_provision_accounts`: 403 for a non-admin role.
- `test_duplicate_username_issuance_rolls_back_the_whole_unit`: forcing a
  duplicate-username 409 leaves `accounts`/`family_memberships` row counts
  unchanged — re-run and independently confirmed via the exact `SELECT
  count(*)` before/after pattern in the test. Traced the transaction path in
  `service.py::provision_member_account()`: `Account`/`FamilyMembership` are
  only `flush()`ed (not committed) before `create_credential()` can raise;
  `app/database.py::get_db()` closes the session in a `finally` without an
  explicit commit on the exception path, and `AsyncSession.close()` rolls
  back any uncommitted transaction — so a partial Account-without-credential
  cannot survive even a duplicate-username race, not just the happy path this
  particular test exercises.
- `test_family_admin_cannot_read_a_members_password_or_impersonate`: neither
  the plaintext initial password nor the stored hash appears in any response
  the issuing admin can obtain (`/api/me`, `/api/me/sessions`), and the
  admin's own `/api/me` never resolves to the issued Account's id.
- Cross-family / non-FamilyAdmin denial is the same
  `require_family_permission(FAMILY_MEMBERS_PROVISION)` dependency as §13/§14
  — a caller whose only role is `SERVICE`-scope (e.g. `mission_manager`) has
  no live path to `family.members.provision` at all, since §7/§8 confirm that
  permission is granted only to `(FAMILY, owner)`/`(FAMILY, admin)`. This is
  verified by direct seed inspection rather than a dedicated
  ServiceAdmin-only-actor test; recorded as a minor test-coverage gap, not a
  defect, since the seed data makes the negative case structurally
  unreachable rather than merely untested.

## 16. API Route Inventory (independently extracted from `router.py`)

| Method | Path | Auth | Service fn | Notes |
|---|---|---|---|---|
| POST | `/api/auth/account/login` | anonymous | `auth_service.login` | byte-identical unknown-user/wrong-password errors |
| POST | `/api/auth/account/refresh` | refresh token (body) | `auth_service.refresh_session` | rotates + replay-denies |
| POST | `/api/auth/account/logout` | account session | `auth_service.logout` | revokes only the calling session |
| GET | `/api/me` | account session | `service.authorized_family_set` etc. | server-derived AuthorizedFamilySet |
| POST | `/api/me/password` | account session | `auth_service.change_password` | revokes every session |
| GET | `/api/me/sessions` | account session | `auth_service.list_sessions` | live sessions only |
| DELETE | `/api/me/devices/{device_id}` | account session | `auth_service.unlink_device` | 404 if nothing was revoked |
| POST | `/api/families/{family_id}/member-accounts` | account session + `family.members.provision` in path family | `service.provision_member_account` | 201, one-time initial password |

**8 routes**, matching the implementer's count. `git diff --name-status --
'backend/app/domains/auth/*'` returns nothing — the legacy `/api/auth/*`
router is untouched, confirmed by diff rather than by description.

## 17. Test Environment

Disposable, volume-less `postgres:16.9-alpine` container
(`mongle-w1qa-testdb`), created fresh for this QA session (not reused from the
implementer's environment), seeded from `database/init.sql` and then
`alembic upgrade head` using the repository's own
`minecraft_points_festivals-backend:latest` image. Removed at teardown;
`docker ps -a`/`docker volume ls` confirmed zero residue afterward. The
persistent dev DB `mc-db` (port 5433) was never touched.

**Confirmed environment gap** (matches the implementer's report, independently
re-verified): `find . -iname "docker-compose*.yml"` at repository root returns
`docker-compose.phase1.yml`, `docker-compose.yml`, `docker-compose.prod.yml`
only — `docker-compose.phase2.yml` does not exist, even though
`backend/tests/conftest.py` hardcodes `127.0.0.1:15435`. Classified
`PRE_EXISTING_TEST_INFRASTRUCTURE_GAP`, not a Wave 1 defect. A first attempt
to run the suite against a bare Postgres container (without the
`database/init.sql` legacy baseline) failed with 104 `UndefinedTableError`
setup errors (`relation "players" does not exist") — this is expected
behavior of migration `0000` (an intentional no-op stamp assuming
`init.sql` already ran), not a defect; re-running with the correct two-step
setup produced the results in §18.

## 18. Test Commands and Exact Results

```bash
# 1. fresh disposable DB + init.sql + alembic upgrade head (see §7)
# 2. full suite:
docker run --rm --add-host=host.docker.internal:host-gateway \
  -v "$PWD/backend:/app" -w /app \
  -e DATABASE_URL="postgresql+asyncpg://mc_phase2:***@host.docker.internal:15435/mc_festival_phase2" \
  -e JWT_SECRET="qa-independent-test-secret-not-production" \
  minecraft_points_festivals-backend:latest \
  sh -c "pip install -q pytest pytest-asyncio httpx; python -m pytest -q"
```

| Scope | Result |
|---|---|
| `tests/test_account_auth_wave1.py` (isolated run, `-v`) | **PASS — 33 passed** |
| Full `backend/tests` suite | **PASS — 104 passed, 0 failed** (67.68s) |
| `alembic upgrade head` from empty DB (`0000`→`0006`) | **PASS** |
| `alembic downgrade -1` → `upgrade head` | **PASS**, zero residue by direct SQL |
| `alembic downgrade 0004` → `upgrade head` | **PASS**, tables/permission row confirmed absent then restored |
| Schema/constraint/index/seed introspection | **PASS**, matches Column Dictionary and live seed exactly |
| `git diff --check` | clean, start and end |

No test was skipped, deleted, or weakened by this QA session. No new test
file was added — the existing `test_account_auth_wave1.py` coverage was
judged sufficient against the QA task's own checklist, with two minor gaps
recorded as coverage notes rather than defects (§10 account-token-on-
legacy-route direction, §15 ServiceAdmin-only provisioning actor) since both
are covered structurally by the code/seed rather than by a dedicated test.

## 19. Defects Found

None that required correction. The one defect present in the codebase at
Wave 1 QA start (the pre-existing `0001` seed's FamilyAdmin→ServiceAdmin
auto-grant) was **already fixed** by the implementing session's own migration
`0006`, before this QA task began; this QA session's job on that finding was
to independently confirm the fix, not to make it (§8). No new defect was
found in the six Wave 1 Backlog tasks' scope.

## 20. Corrections Applied

None to product code, migrations, or tests — no defect met the correction
threshold. Documentation-only: `agent-system/qa/COVERAGE_MAP.md` (three Notes
cells appended with independent re-verification evidence, §"Coverage Map"
below), `agent-system/active.md` and `agent-system/relay/current.md`
(this task's own registration/closeout), and this report.

## 21. Regression Result

104/104, including the 71 pre-existing Doran/weekly/service-binding tests,
reproduced from a database this QA session created itself (not reused from
the implementer's teardown). No existing route, model, or migration file
outside Wave 1's declared scope was modified (§5).

## 22. Test Infrastructure Gap

`docker-compose.phase2.yml` is absent from the repository (§17), confirmed
independently. This is `PRE_EXISTING_TEST_INFRASTRUCTURE_GAP`, not attributable
to Wave 1. Recorded here rather than mixed into §19. Follow-up candidate:
`MONGLE-TEST-INFRA-PHASE2-COMPOSE-RESTORE-001` (unopened — PM triage, not
this task's authority to open unilaterally beyond noting it, consistent with
the implementer's own report).

## 23. Recursive Scope Review

**Pass 1 (before):** declared scope = the six Wave 1 Backlog tasks'
`backend/app/domains/family/**`, `0005`/`0006` migrations, `backend/tests/**`;
forbidden = D1–D8 reopening, Doran/Wagle/Markpoint domain code, frontend,
`init.sql`, migrations `0000`–`0004`, the 33 other pre-existing dirty files.

**Pass 2 (after verification/edits):** actual writes this session —
`agent-system/active.md`, `agent-system/relay/current.md`,
`agent-system/qa/COVERAGE_MAP.md` (3 Notes cells only, no other row touched),
this report. Zero product code, migration, or test file was modified — every
finding in §6–§16 was confirmed to already hold, so no defect-correction
edit was needed. No pre-existing dirty file outside this list was touched;
`git status --short` at end shows the same 34 pre-existing modified files
plus this session's 4 additions, nothing else.

**Pass 3 (before close):** every §21–22 rules.md gate requirement addressed;
no test skipped/weakened; documentation (Table/Column Dictionary, API
Inventory, Role Matrix) cross-checked against live schema/seed/routes in §5–8,
§16 and found consistent, with one minor documentation-precision note (§8,
`markpoint.own.read` also present on `owner`) that does not require correction
under this task's scope; two minor test-coverage gaps recorded (§10, §15),
neither rising to a defect; Wave 2 impact — none of this QA's own edits touch
anything Wave 2 depends on beyond confirming Wave 1's security dependency is
sound; Lifecycle for the six Backlog tasks and this QA task is closed out in
§27.

## 24. Five-Gate Review

- **Gate 1 — 환각:** every claim above carries a command, file, or direct SQL
  result produced in this session (§7, §8, §18). Where the implementer's
  report was reused as a starting hypothesis, it was independently
  re-executed rather than copied (fresh container, fresh `database/init.sql`
  load, fresh `docker images`/`docker ps` state, independent `git diff`
  extraction). No unrun test is reported as PASS; the two coverage gaps in
  §10/§15 are explicitly labeled as unverified-by-test rather than claimed
  PASS.
- **Gate 2 — 누락:** Credential, Session, refresh rotation, replay rejection,
  device unlink, AuthorizedFamilySet, multi-family isolation,
  ActiveFamilyContext non-authority, scoped RBAC, last-admin, cross-family
  deny, route authorization, FamilyAdmin issuance, transaction rollback,
  audit, migration, API integration, and documentation are each covered in
  §6–§16 above.
- **Gate 3 — 오작업:** no Legacy backfill (confirmed: `0005`/`0006` create no
  data, `database/init.sql` is the only legacy-adjacent source used and only
  as a baseline, never read by the new tables); `LegacyIdentityMapping` is not
  on the Account-native login path (§9, §12 — `grep` for
  `legacy_identity_mappings` inside `auth_service.py` returns nothing); no
  plaintext password/token storage (§6, §9, §10); no FamilyAdmin
  impersonation or post-hoc password read (§15); the FamilyAdmin→ServiceAdmin
  auto-grant is confirmed removed (§8); `ActiveFamilyContext` is confirmed
  absent as an authorization input (§12); one membership ending is confirmed
  not to end the Account Session (§11); no pre-existing dirty file was
  touched (§23); no test was weakened.
- **Gate 4 — 축혼동:** this report separates current-implementation fact
  (§6–§18), the approved D1–D8 contract (referenced, never re-argued), this
  Wave's actual output (§5, §19–20), the two explicitly-deferred items
  (`markpoint.own.read`/D5-B in §8, `docker-compose.phase2.yml` in §22), and
  legacy reference material (`database/init.sql`, used only as a baseline).
  No Wagle realtime, Push, Markpoint Mission/Ledger, or cutover work was
  touched or evaluated as if it were.
- **Gate 5 — 신선도/오탈자:** Table Dictionary (§6), API Inventory (§16), Role
  Matrix (§8, §13) cross-checked against live schema/seed/routes and found
  consistent bar the one documentation-precision note in §8. `git diff
  --check` clean at both start and end. No duplicate Task ID introduced. No
  Mongle/Wagle/Markpoint naming error found in the files this session touched.

## 25. Changed-file Manifest (this QA session)

**Modified:** `agent-system/active.md`, `agent-system/relay/current.md`,
`agent-system/qa/COVERAGE_MAP.md` (3 Notes cells appended).

**New:** `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md` (this file).

**Untouched:** every backend product/migration/test file from Wave 1 (§5) —
zero corrections were needed, so zero were made.

## 26. Residual Risks

1. **No FE consumer exists yet** — the Account routes remain proven only at
   the API/DB layer, unchanged from the implementer's own §22 risk #3.
2. **`docker-compose.phase2.yml` is still missing** — every future session
   must keep re-deriving the two-step (`init.sql` + `alembic upgrade head`)
   disposable-DB setup by hand until a test-infrastructure task commits it.
3. **Legacy auth remains fully live by design** — unchanged, Wave 7 scope.
4. **`markpoint.own.read` placement** — unresolved, owned by Wave 4's D5-B,
   now additionally noted to also cover `owner` (§8).
5. **Two minor test-coverage gaps** (§10 account-token-on-legacy-route
   direction, §15 ServiceAdmin-only provisioning actor) are covered
   structurally by code/seed but not by a dedicated executed test. Neither
   blocks this PASS verdict since both are verified by direct code/seed
   inspection in this report, but a future session adding Wave 1 regression
   tests should close them.

## 27. Lifecycle / Closeout

All six Wave 1 Backlog tasks (`MONGLE-W1-CREDENTIAL-SESSION-DB-CONTRACT-
CORRECTION-001`, `MONGLE-W1-SCOPED-RBAC-001`, `MONGLE-W1-ACCOUNT-CREDENTIAL-
001`, `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001`, `MONGLE-W1-FAMILY-SCOPED-
ROUTE-AUTHZ-001`, `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001`) and the
`MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` execution bundle are independently
QA-verified `PASS`. Per this task's own §21 exit condition, this QA task's own
Lifecycle is `COMPLETE`; `agent-system/active.md` and `relay/current.md` are
updated accordingly in the same commit-less session (§28 below). PM review of
the `0006` RBAC registry correction remains a separate open item (process
review of an already-verified-correct fix, not a defect), and Wave 2 Start
Review is unblocked by this verdict.

## 28. Final Verdict

```text
WAVE_1_INDEPENDENT_QA_PASS
WAVE_1_LIFECYCLE_COMPLETE
READY_FOR_WAVE_2_START_REVIEW
```

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `NOT_APPLICABLE` — this QA task's own report serves as its record;
  no separate handoff file was created (consistent with how the implementer's
  own bundle was recorded)
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`
- Independent QA: `this is the independent QA` — PASS, this report
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: three existing Wave 1 rows' Notes appended with this
  session's independent re-verification evidence; no row's Coverage Status,
  Confidence, or test count was altered.
- CLOSEOUT GATE: `PASS`
