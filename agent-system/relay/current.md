# Current Relay

Current Task: none — `MONGLE-W1-INDEPENDENT-QA-001` released its write claim
on 2026-08-01 after independently verifying Wave 1.

- Outcome: `WAVE_1_INDEPENDENT_QA_PASS` / `WAVE_1_LIFECYCLE_COMPLETE` /
  `READY_FOR_WAVE_2_START_REVIEW`. 104/104 backend tests reproduced from a
  freshly created disposable Postgres 16.9 container (not the implementer's
  leftover environment); migration `0000`→`0006` fresh-upgrade,
  `downgrade -1`+re-upgrade, and full downgrade-to-`0004`+re-upgrade all
  confirmed by direct SQL introspection (zero residue/duplicates); the 8 new
  API routes exercised at real HTTP level; session/token/RBAC/cross-family/
  last-admin/FamilyAdmin-issuance boundaries independently re-checked against
  source, not accepted from the implementer's report. No new defect found.
  HEAD unchanged at `da7ea74`; no commit, push, merge, rebase or PR.
- Evidence: `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`.

## Next Task

None claimed. Two open PM items, neither blocking:

1. PM review of the `0006` RBAC registry correction on its own merits
   (process review of an already-independently-verified-correct fix).
2. PM decision on graduating `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001`, the
   six Wave 1 Backlog tasks it executed, and `MONGLE-W1-INDEPENDENT-QA-001`
   itself to `graduated/` (same pattern as the still-open
   `MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001` graduation decision).

The five Wave 1 FE slices and Wave 2 are unblocked by this PASS to proceed to
their own Start Gates / Start Review — this relay entry does not itself open
either.

## What Wave 1 changed (still current for the next writer)

- New: `backend/app/domains/family/auth_service.py`,
  `backend/app/domains/family/dependencies.py`,
  `backend/tests/test_account_auth_wave1.py`, migrations
  `0005_account_credential_session` and `0006_family_service_separation`.
- Modified: `backend/app/config.py`,
  `backend/app/domains/family/{models,router,schema,service}.py`,
  `backend/app/models/all_models.py`.
- Alembic head moved `0004_doran_reliable_slice` → `0006_family_service_separation`.
- 8 new routes under `/api/auth/account/*`, `/api/me/*` and
  `/api/families/{family_id}/member-accounts`. No existing route was modified
  (confirmed twice now — implementer's diff and this QA's independent diff
  extraction agree).

## Carried-forward items the next writer must not mistake for settled

- **Security finding, fixed and now independently confirmed fixed:** the
  `0001` seed auto-granted `markpoint.missions.manage`/`markpoint.points.adjust`
  to FAMILY `owner`/`admin`, violating D4 and bypassing the ServiceSubscription
  gate. Removed by `0006`; independently reproduced via fresh migration
  upgrade/downgrade/re-upgrade with direct SQL checks, not log inspection.
  Current impact verified nil (no product route reads those codes yet).
- **`markpoint.own.read`** is on FAMILY `member`/`restricted_member`
  **and `owner`** (the QA independently found `owner` was omitted from the
  implementer's own note) plus SERVICE `participant`. Deliberately left
  alone — self-read, not administration; placement is a D5-B default-access
  question owned by Wave 4.
- **`docker-compose.phase2.yml` still does not exist**, though
  `backend/tests/conftest.py` targets `127.0.0.1:15435`. Independently
  re-confirmed: the suite needs a two-step disposable-DB setup
  (`database/init.sql` baseline, since migration `0000` is an intentional
  no-op stamp, then `alembic upgrade head`) that no committed script performs.
  `mc-db` on 5433 remains `UNSAFE_ON_SHARED_DB` and was not used by this QA
  either. Committing the compose file (and ideally the two-step setup script)
  is a separate test-infrastructure task
  (`MONGLE-TEST-INFRA-PHASE2-COMPOSE-RESTORE-001`, not yet opened).
- **Legacy auth is fully live and untouched by design.** `resolve_current_account`
  and `/api/auth/*` still work through `LegacyIdentityMapping`; the new Account
  path is independent of them (independently confirmed: no
  `legacy_identity_mappings` reference anywhere in `auth_service.py`).
  Retiring legacy is Wave 7, not Wave 1.
- **Two minor test-coverage gaps** recorded by the independent QA, not
  defects: an account-native token's rejection by legacy routes is verified
  by code review of both dependency chains but has no dedicated executed
  test; a ServiceAdmin-only actor's denial from `/member-accounts` is
  verified by direct seed inspection (the permission is granted only to
  FAMILY owner/admin) but has no dedicated executed test either. See QA
  Evidence §10/§15/§26.
- **9 documented-but-unregistered tasks** remain unregistered by PM decision;
  drafts in `agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001.md`.
- **Undocumented external worktree** at `/private/tmp/claude-501/.../scratchpad/
  data-backend-contract-worktree` — Human Gate under `DEC-2026-005`; do not
  clean up unilaterally.
- **`PHASE0-AUTOMATED-GAP-CLOSEOUT-001`** is still `SUSPENDED` with measured
  authorization defects in the legacy mission/daily-point/notification routes.
  Wave 1 did not touch those routes.

## Worktree state

The pre-existing 28 modified tracked files and the untracked document set from
earlier sessions remain uncommitted and unowned by any open task. Do not reset,
restore, checkout, clean or stash them — resolving another owner's dirty
worktree is a Human Gate. This QA session's own writes were limited to
`agent-system/active.md`, `agent-system/relay/current.md`,
`agent-system/qa/COVERAGE_MAP.md` (Notes cells only), and
`agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`.
