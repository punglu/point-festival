# PHASE1-ACCOUNT-FAMILY-RBAC-FOUNDATION-001 Implementation Evidence

- Task ID: `PHASE1-ACCOUNT-FAMILY-RBAC-FOUNDATION-001`
- author/agent: `Codex`
- observed_at: `2026-07-26`
- git_ref: `fa6fb65d1a79a01342da9695a9156f08a0e5f1fb`
- environment: `local macOS workspace; isolated synthetic database only`
- secrets_redacted: `true`
- Verification: `QA_PENDING`
- Self-check only: `true`
- Independent QA: `pending — required for schema, migration, RBAC, boundary, and adapter changes`
- Git repository is SSOT.

## Planned verification

- Alembic baseline stamp/upgrade/downgrade/upgrade against an isolated database.
- API + DB matrix for membership lifecycle, multirole union, default deny,
  multiple-owner invariant, path-based cross-family denial, service subscription
  gating, stale JWT-role resistance, and legacy mapping ambiguity.
- Existing legacy authorization, scenario, frontend lint/build, and Playwright
  regression checks.

## Boundary

No operating DB access or migration, no legacy JWT cutover, and no actual user
mapping. Writer self-check cannot issue final PASS; independent security/DB QA is
required before push.

## Writer self-check results

- PM RBAC decision was re-read directly from Drive. Approved decisions are
  reflected as `APPROVED` in `engineering/phase1/*`.
- Isolated `mc_phase1` uses its own database volume/network and host ports
  15434/18001/13001; existing `outlook-hub` and `mc_phase0` were not stopped.
- Alembic baseline marker and Foundation revision completed upgrade, downgrade to
  `0000`, explicit `stamp 0000`, and re-upgrade against the synthetic DB.
- Synthetic seed uses explicit IDs only; it creates no operating mappings and
  preserves one ambiguous unmapped identity fixture.
- `backend/scripts/phase1_legacy_bootstrap_report.py` ran against the isolated
  database and emitted only aggregate inventory (`4` active players, `5` linked
  mappings, `1` ambiguous mapping, and `0` PlayerAuth orphans). It performs no
  writes and requires reviewed operational mapping input.
- `tests/api/phase1_rbac_api_test.py`: exit 0; verifies default deny,
  cross-family path denial, multi-role union, inactive subscription suppression,
  administrator self-escalation denial, last-Owner invariant/DB count, and
  ambiguous mapping preservation.
- Frontend lint/build: exit 0. Backend pytest: 6 passed. Existing Phase 0
  weekly suite: 6/6; legacy authorization suite: PASS; synthetic scenario:
  87/87; Playwright: 9 passed.
- `check_closeout.py`, `check_all.py`, and Git diff checks remain required for
  final self-check after the evidence commit. Independent QA remains pending.

## Independent QA Correction In Progress

The first independent QA pass blocked the candidate for Family lifecycle
authorization, inactive-Family context exposure, soft-deleted legacy identity
adapter validation, and a Phase 1 API+DB suite default-environment mismatch.
The original self-check above is retained as historical implementation evidence.
Writer correction and independent re-verification are required; this is not a
final PASS claim.

## Correction Self-check

The writer corrected only the four blocked items and reran the isolated suite
without DB override variables. The API+DB suite passed `30` reported checks,
including Admin lifecycle denial, Owner lifecycle persistence, inactive Family
context omission, closed-family path denial, cross-family membership-ID denial,
and soft-deleted legacy Player adapter denial. Frontend lint/build, backend
pytest (`6 passed`), Agent checks, and Git whitespace checks also passed.
Independent QA re-verification remains required.

## Independent QA Final Verdict

- Verdict: `PASS`
- Candidate verification covered the initial four blockers and confirmed:
  Admin lifecycle denial with DB status unchanged; Owner lifecycle persistence;
  suspended/closed Family context omission and path denial; current Player and
  Admin soft-delete rechecks for previously issued JWTs; default Compose DB
  execution of the API+DB suite; cross-Family membership-ID denial; Owner,
  subscription, and ambiguous-mapping invariants.
- Additional regressions: frontend lint/build, backend pytest (`6 passed`),
  weekly API (`6/6`), legacy authorization suite, synthetic scenario (`87/87`),
  Playwright (`9 passed`), Agent checks, and Git whitespace checks passed.
- Independent from implementer: `true`
- Git repository is SSOT. Operating DB schema stamp and reviewed identity
  mapping are intentionally unperformed Human Gates.
