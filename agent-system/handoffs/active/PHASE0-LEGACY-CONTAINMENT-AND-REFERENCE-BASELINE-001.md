# PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001

- Task ID: `PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001`
- author/agent: `Codex`
- created_at: `2026-07-26`
- git_ref: `96274c0546b3e133eb8ca3bae24f37080cb5792d`
- environment: `local macOS workspace; isolated mc_phase0 runtime`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `PASS`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev`
- Start HEAD: `96274c0546b3e133eb8ca3bae24f37080cb5792d`
- End HEAD: `documentation/evidence commit amended to include independent QA; final hash is reported outside this self-referential record`
- Final Commit: `self-reference intentionally omitted; implementation and test commits are recorded below`
- Implementation Commit: `5a6ac98582f4da045878006724cd2eb35677ec0b`
- Test Commit: `773fb92c49f67e4136019362f67d6b6d405f8ba5`

## Scope

Contain measured legacy unauthenticated/cross-user API exposure within the existing
player/admin model. Create a complete source-backed route security matrix and
legacy-reference baseline. Preserve database schema, calculations, tenant/room
models, external Docker projects, and user-owned worktree changes.

## Worktree and changed files

- Changed Files: shared dependency and bounded legacy router/service guards; `tests/api/legacy_auth_boundary_test.py`; updated 87-case synthetic scenario; legacy security/reference documentation; engineering status notes; and task records.
- Existing Dirty State: user-owned `CLAUDE.md` modification and root/docs deletions; starting unstaged SHA-256 `eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`.

## Commands and outcomes

- Tests Run: Python compile; backend pytest (6 passed); frontend lint/build; weekly API suite (6/6); new authorization/DB-invariant suite; synthetic scenario (87/87); and Playwright (9 passed), all exit 0 against isolated `mc_phase0`.
- Tests Not Run: physical-device/PWA/Push and operating-DB work are Human Gates and excluded.

## Completed / remaining

- Known Gaps: `LEGACY REFERENCE / NOT FULLY VALIDATED`; family tenancy, a room participant model, idempotency, complete calculation/lifecycle proof, physical-device/PWA/Push, and operating-DB rehearsal are not claimed.
- QA Status: writer self-check succeeded; independent read-only security QA completed with `PASS` against the implementation/test candidate. It confirmed all 91 matrix/OpenAPI operations, no unexpected anonymous sensitive 2xx, A-to-B denial with DB invariants, administrator preservation, chat pair isolation, and all listed suites.
- Drive Evidence: not requested.
- Coverage Map Review: UPDATED for executable authorization/DB-invariant evidence and legacy reference classification.

## Risks and Human Gate

Any remaining unauthenticated sensitive endpoint, cross-user access, administrator regression, or rejected-request DB mutation blocks closeout and push. Independent QA found none in the scoped containment model.

## Next agent first action

PM may review the completed containment and task-authorized push. Do not infer that the legacy product is fully validated; the documented Human Gates and unvalidated areas remain.

## Forbidden Scope

Schema/migration work, tenant/role/room/idempotency models, API response retrofit, frontend restructuring, calculation rewrites, operating resources, existing Docker projects/volumes, user dirty paths, and push before independent QA PASS.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md`
- Independent QA: `complete — PASS`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `new authorization/ownership executable evidence and legacy-reference classification were added`
- CLOSEOUT GATE: `PASS`
