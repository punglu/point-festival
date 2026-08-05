# MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001

- Task ID: `MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001`
- author/agent: independent QA session (fresh session; did not author Auth/Family/Markpoint, `281d45a`)
- created_at: 2026-08-06
- git_ref: real repo `dev-newmarkp` HEAD `62c1f23`, clean before and after this task
- environment: macOS/Docker (OrbStack); own isolated stack `qaindep-db-1`/`qaindep-backend-1`
  (ports 15440/18010, built from the real `docker-compose.phase1.yml` shape via a scratch
  compose file) + native `pnpm run dev` Vite frontend (port 5174) against the real current
  source tree; own isolated pytest DB `qaindep-pytest-db` (port 15435); pre-existing persistent
  `mongle-backend-1`/`mongle-db-1` (18001/15434) confirmed running before and after, never
  touched
- evidence: `agent-system/qa/MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001.md`
- secrets_redacted: `true`
- Lifecycle: `COMPLETED`
- Decision: `NOT_REVIEWED` (this task is a verification pass, not a design decision; the two
  confirmed defects below need their own PM/implementation decision before any fix)
- Verification: `CONDITIONAL` (Auth PASS, Family PASS, Markpoint FAIL on one route defect,
  Cross-domain FAIL on one session-integrity defect — see QA Evidence for full per-axis detail)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `62c1f23`
- End HEAD: `62c1f23` (unchanged — no commit/push/merge/rebase/reset/clean/restore/stash anywhere)
- Final Commit: none

## Worktree and changed files

- Changed Files (real repo): only this task's own 2 new documents (this handoff + its paired QA
  Evidence) plus append-only edits to `agent-system/active.md`, `agent-system/relay/current.md`,
  `agent-system/qa/COVERAGE_MAP.md` (see below). **Zero product code touched** — confirmed via
  `git status --short` at task start (empty) and again immediately before writing this handoff
  (still empty except this session's own then-untracked scratch files, all deleted before this
  point).
- Existing Dirty State at session start: none (`git status --short` empty, `git diff --stat`
  empty).
- Scratch material created and fully removed before this report: `docker-compose.qa-indep-
  scratch.yml` (repo root), `tests/e2e/qaindep_script.mjs` through `qaindep_script10.mjs` (10
  disposable Playwright/Node driver scripts, `tests/e2e/`), assorted `/tmp/qaindep-*` screenshot
  and result files. All confirmed gone via `git status --short` (empty) and `ls`/`rm -rf` exit
  codes before this handoff was written.

## Commands and outcomes

- Isolated stack build: `docker compose -p qaindep --env-file .env.phase0.example -f
  docker-compose.qa-indep-scratch.yml up -d` → both containers healthy; `alembic upgrade head`
  ran automatically inside the backend entrypoint (21 migrations, `0000`→`0021`) against
  `database/init.sql`'s legacy schema.
- Fixture: `python scripts/phase1_seed_synthetic.py` inside `qaindep-backend-1` →
  `PHASE1_SYNTHETIC_SEED_OK`/`WAVE6_TARGET_FIXTURE_OK`; plus this session's own `UPDATE players
  SET is_locked = true WHERE id = 2` and one additional Account (`noaccess.qa`, id 7) created via
  `family.auth_service.create_credential` inside the container. Full before/after row counts and
  IDs recorded in the QA Evidence's Common Fixture section.
- Auth axis: real UI flow (profile-select → PIN → dashboard) + direct API calls
  (`POST /api/auth/login` for both a locked and unlocked player) at all 3 viewports — full result
  table in QA Evidence. **PASS.**
- Family axis: real UI flow + direct API authorization matrix (member/no-membership/cross-family/
  unauthenticated, all 4 combinations against `GET /api/families/1/members`) + route-inventory
  spot-check across all 7 `/family/*` sub-routes — full result table in QA Evidence. **PASS.**
- Markpoint axis: real UI flow + `03-target-ui.spec.ts` (4 passed/11 failed) +
  `04-w75-data-wiring.spec.ts` (8 passed/1 failed-Wagle-only/1 self-skipped) both run for real via
  `playwright.mongle-manual.config.ts` against the isolated stack. Root-caused all 11 failures in
  the first spec down to two causes: `SPEC_STALE` (7, heading text + family-switch locator) and a
  confirmed `PRODUCT_DEFECT` (5 with 1 overlap, `/markpoint/admin` unregistered route). **FAIL**
  on the confirmed defect; member surface alone would be PASS.
- Cross-domain axis: continuous session, legacy-PIN → bridged Account → multi-family Family
  selection → `GET /api/me/notifications` 401 → global forced logout, reproduced 3 times,
  root-caused to a missing entry in `httpClient.ts`'s existing `OPTIONAL_ACCOUNT_ENDPOINTS`
  allow-list (which already has 2 prior, structurally identical fixes for other endpoints).
  **FAIL.**
- Backend regression (Auth/Family/Markpoint-relevant subset only, this session's own execution):
  `python3.11 -m pytest` across 12 test files → **213 passed, 0 failed**, 197.16s, isolated
  `postgres:16.9-alpine` port 15435. Full-suite re-run explicitly **not** performed this session
  (see QA Evidence Regression section for the exact `LATEST_FULL_BACKEND_SUITE` vs
  `THIS_QA_FULL_BACKEND_SUITE` framing — not blended into one number).
- Frontend regression: `pnpm run lint` clean; `pnpm run build` (`tsc -b && vite build`)
  succeeded, 666 modules, pre-existing chunk-size advisory only. Docker image build:
  **NOT IN SCOPE** (pre-confirmed broken, out of this task).
- `git diff --check`: exit 0. `python3 agent-system/tools/check_all.py`: clean, all warnings
  pre-existing (0 new).
- Tests Not Run / Not Applicable: full backend `pytest -q` (see above, reasoned skip, backend
  diff genuinely zero); frontend Docker image build (explicitly out of scope per task brief);
  physical-device evidence for iPhone/iPad/Android (task brief scoped this task to Chromium
  viewport emulation only, same as the Admin/Wagle sibling precedent — no device claim made).

## DB and runtime cleanup (see QA Evidence for full detail)

- `qaindep-db-1`/`qaindep-backend-1`: `docker compose ... down -v` — containers, network, volume
  all removed.
- `qaindep-pytest-db`: `docker stop && docker rm`.
- Native Vite dev server (port 5174): killed.
- All 11 scratch files (1 compose + 10 `.mjs`) and all `/tmp/qaindep-*` artifacts: removed;
  `git status --short` confirmed empty afterward.
- Pre-existing `mongle-backend-1`/`mongle-db-1`: confirmed running, unmodified, same container
  IDs, before and after this task.
- No shared/persistent database was ever written to.

## Scope and boundaries

- Read-only for all product code (`backend/app/`, `frontend/src/`) throughout — every file this
  session wrote was either a disposable QA driver script (deleted) or this documentation pair.
- No test-assertion edit, deletion, skip, or weakening. The one skip present in the results
  (`04-w75-data-wiring.spec.ts`'s `2t`) is that spec's own pre-existing guard, unrelated to this
  session.
- No CSS/route/API/migration/RBAC change. No commit, push, merge, rebase, cherry-pick, reset,
  clean, restore, or stash — anywhere, real repo or otherwise (this task used no scratch
  worktree; all isolation was via disposable Docker containers/volumes instead).
- Out of scope, confirmed still in their pre-existing deferred state, not counted as failures:
  `1j`/`1j-1` (PIN-recovery stub), `2s` (4-digit Screen vs 6-digit-capable backend PIN policy,
  `HUMAN_GATE`), Wagle and Admin (already closed by the sibling Independent QA tasks this task's
  brief names), the `/__wave6/*` canonical preview routes, Markpoint's `1x` (주간 리포트, deferred
  stub).

## Closeout Synchronization

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001.md`
- QA Evidence Path: `agent-system/qa/MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-INDEPENDENT-QA-001.md`

Detail: ACTIVE — appended a `COMPLETED` entry for this Task ID to `agent-system/active.md`
(append-only, read-before-edit). HANDOFF — this document. QA EVIDENCE — the paired evidence file
above. COVERAGE MAP — appended a new row (`FE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-GENUINE-
INDEPENDENT-QA-001`) recording that Auth/Family/Markpoint now have a genuinely independent QA
pass on record, with its CONDITIONAL/FAIL result and the two newly-confirmed defects, so a future
task does not re-propose this exact verification as new work per Invariant 9. CLOSEOUT GATE PASS
here means only that these four documentation obligations are synchronized — it does **not**
mean `Lifecycle: COMPLETED` implies product correctness, independent QA PASS at the product
level, PM approval, or graduation: two of the four axes are FAIL on confirmed, currently-live
defects, per Verification above. This CLOSEOUT GATE PASS is not itself described anywhere in
this document as an Independent QA PASS.

## Next action

See QA Evidence's own "Next action" section for the full 5-point list. Summary: (1) register the
missing `/markpoint/admin` route, (2) add `/api/me/notifications` to the existing
`OPTIONAL_ACCOUNT_ENDPOINTS` allow-list (or fix its backend dependency to accept the legacy
bridge, a PM decision), (3) a future *separate* Independent QA session re-verifies both after a
fix, (4) `03-target-ui.spec.ts`'s two stale assertions are a test-maintenance item for whoever
owns that spec, (5) a Branch Integration task commits this evidence/handoff pair — this session
performed no commit/push itself, matching the Admin/Wagle lineage convention.
