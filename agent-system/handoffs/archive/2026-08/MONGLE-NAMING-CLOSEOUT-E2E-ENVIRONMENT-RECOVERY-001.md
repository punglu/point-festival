# MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001

- Task ID: `MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- Predecessor QA: `MONGLE-COMBINED-NAMING-AND-FRONTEND-INDEPENDENT-QA-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; isolated Compose project `mc_phase1`; disposable volume-less PostgreSQL 16.9 for the backend seam test; throwaway Docker images with container-only `node_modules` for every frontend build
- evidence: `agent-system/qa/MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.md`
- secrets_redacted: `true`
- Lifecycle: `GRADUATED`
- Decision: `DESIGN_APPROVED` (PM directive, 2026-08-01)
- Verification: `PASS`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- End HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Origin

The combined naming QA passed every static and source-level contract but left
three verifications unexecuted: current-source Playwright, a clean isolated
frontend build, and the focused backend Wagle seam test. Its Playwright run had
exercised a stale frontend image, so its 41 failures described source that no
longer existed and were invalidated. This task recovered the environment and
executed all three.

## Worktree and changed files

- New: `frontend/.dockerignore`, `tests/e2e/scripts/frontend-source-fingerprint.sh`, `tests/e2e/scripts/verify-current-source-frontend.sh`, `backend/requirements-dev.txt`.
- Modified: `frontend/Dockerfile` (fingerprint arg, label, served fingerprint file), `docker-compose.phase1.yml` (build arg), `tests/e2e/scripts/start-mongle-phase1.sh` (fingerprint + `--force-recreate` + guard), `tests/e2e/playwright.mongle.config.ts` (fingerprint into the test process, `reuseExistingServer: false`), `tests/e2e/specs-mongle/01-shell.spec.ts`.
- **Product source changed: none.**
- Existing Dirty State: the Wave 2/4 bundle's uncommitted work was present at start and is untouched. Nothing was reset, restored, checked out, cleaned or stashed.

## Commands and outcomes

```
clean isolated build (no host node_modules, npm ci)  -> PASS, ✓ built in 1.00s
  build context                                      -> 106.98 MB -> 28.18 kB
  tsc --noEmit                                       -> EXIT=0
  eslint                                             -> clean
  tokenContract                                      -> 29 pass / 0 fail
current-source proof (worktree = image = served)     -> PASS, + 5/5 in-browser
playwright (isolated mc_phase1, clean bring-up)      -> 90 collected, 86 passed,
                                                        0 failed, 4 skipped, 0 retries
backend seam (disposable env + disposable Postgres)  -> 3 collected, 3 passed, EXIT=0
stale-image guard negative test                      -> correctly FAILS, EXIT=1
git diff --check                                     -> clean
```

- Tests Run: all of the above.
- Tests Not Run: migrations `0007`/`0008` catalog revalidation, Track A/B full independent QA, the full backend suite — all explicitly out of scope and covered by the parent independent QA.

## Completed / remaining

- **All three predecessor blockers closed.** One predecessor diagnosis was corrected: the "BuildKit stall" was a 54.4 s Docker Hub metadata fetch for the base image, not the build context. The context was nevertheless a real defect for a different reason — see below.
- **Two stale-image paths existed, not one.** The predecessor's `--build` closed the first. `reuseExistingServer: true` was the second and wider one: when anything already answers on the port, Playwright skips the start script entirely, so the rebuild never runs. Now `false`.
- **`COPY . .` was layering the host's darwin-arm64 `node_modules` over the container's `npm ci` tree.** The build survived only because Rollup picks its native binary by platform at runtime and the musl one happened to remain reachable. `.dockerignore` removes the coincidence.
- **The repository declared no test dependencies at all**, while two documents specify `python3 -m pytest -q` as the measured invocation. `backend/requirements-dev.txt` now declares them; `pytest-asyncio` is pinned `0.26.0` because `pytest.ini` sets `asyncio_default_test_loop_scope`, which 0.25.x silently ignores.
- Known Gaps:
  - `TRACEABILITY_GAP` — the whole bundle remains uncommitted working state at `0d9280c`.
  - No frontend component-test framework.
  - `docker-compose.phase2.yml` still absent; the backend fixture DB is stood up by hand.
- QA Status: this task is itself the independent execution of the three blocked verifications.
- Coverage Map Review: `UPDATED` — one row moved from FAIL/ENVIRONMENT to executed PASS, one new row for the harness guard.

## Product findings (not test-harness issues)

Three Playwright failures in the first current-source run were diagnosed against
the live API rather than assumed. Two were bugs in tests written by this task
and were fixed. The third was a **stale expectation that had been pinning a
privilege escalation in place**:

`Mongle platform shell › keeps the legacy dashboard…` asserted that a FAMILY
owner *sees* the "미션 관리" link. That link is gated on
`markpoint.missions.manage`, which migration `0006` removed from every
FAMILY-scope role precisely because auto-granting it violates D4 (a FamilyAdmin
is never automatically a ServiceAdmin). Confirmed against a live
`/api/account-context`: the owner of Synthetic Family Alpha holds `family.*` and
`markpoint.own.read`, and no `markpoint.missions.manage`. The assertion was
**inverted, not deleted**, so a regression that re-grants the permission now
fails here — and a positive assertion on a permission the owner does hold was
added alongside so the test remains a real permission check.

## Risks and Human Gate

- `reuseExistingServer: false` means a leftover `mc_phase1` stack now blocks the next run with a clear error instead of silently reusing it. That is the correct failure direction, but it is a behaviour change.
- Do not inline the retired namespace constants (`'na' + 'ran'`) in `activeFamilyStorageMigration.ts` or `01-shell.spec.ts`; a repository-wide sweep would rewrite them into the canonical key and turn the migration into a no-op.
- Do not remove the single `naran` occurrence from the shipped bundle — it is the migration source, and without it the one-time migration cannot read the old key in a real browser.
- The stale-image guard must keep **recomputing** the worktree fingerprint. If it is ever changed to trust `MONGLE_FRONTEND_FINGERPRINT`, it stops being a guard.
- No commit or push was made. Branch and HEAD unchanged.

## Next agent first action

Next Wave Start Review. The naming bundle is closed; nothing in it is pending.
Before any new implementation task, note that the entire bundle is still
uncommitted at `0d9280c` — PM commit/push is the outstanding traceability item.

## Forbidden Scope

Reintroducing any `/naran/*` route, alias, redirect or fallback; a permanent
retired-storage fallback or dual-write; renaming Naran to Wagle (the platform
axis maps to **Mongle**); rewriting historical/archived documents to remove the
retired names; weakening or skipping any assertion in `01-shell.spec.ts`;
deleting or overwriting the host's `node_modules`; pruning the global Docker
cache or other projects' resources; Wave 3 realtime/Push/PIN; Markpoint
Mission/Ledger; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md` — the seven graduated sections were removed; the records now live in `agent-system/graduated/2026-08.md`.
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.md`
- Independent QA: `self`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `E2E-MONGLE-ROUTE-STORAGE-RETIREMENT-001` moves to an executed PASS; new `E2E-HARNESS-CURRENT-SOURCE-GUARD-001` row.
- CLOSEOUT GATE: `PASS`
