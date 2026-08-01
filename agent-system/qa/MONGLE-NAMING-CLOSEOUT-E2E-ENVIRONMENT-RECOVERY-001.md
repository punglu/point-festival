# MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001

- Task ID: `MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- Predecessor QA: `MONGLE-COMBINED-NAMING-AND-FRONTEND-INDEPENDENT-QA-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged start → end)
- environment: repository root; isolated Compose project `mc_phase1`; disposable volume-less PostgreSQL 16.9 for the backend seam test; all frontend builds in throwaway Docker images with container-only `node_modules`
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
E2E_ENVIRONMENT_RECOVERY_PASS
CURRENT_SOURCE_FRONTEND_IMAGE_CONFIRMED
CLEAN_ISOLATED_PRODUCTION_BUILD_PASS
PLAYWRIGHT_ROUTE_STORAGE_RETIREMENT_PASS
FOCUSED_BACKEND_WAGLE_SEAM_PASS
E2E_HARNESS_STALE_IMAGE_DEFECT_VERIFIED_FIXED
DOCKER_RESIDUAL_ZERO
COMBINED_NAMING_INDEPENDENT_QA_PASS
MONGLE_PARALLEL_W2_W4_PARENT_COMPLETE
READY_FOR_NEXT_WAVE_START_REVIEW
```

All three previously-blocked verifications were executed against the current
worktree. The browser is proven — not assumed — to have been running a build
made from this source.

## 2. Environment / Git Baseline

| Command | Start | End |
|---|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` | same |
| `git branch --show-current` | `dev-newmarkp` | `dev-newmarkp` |
| `git rev-parse HEAD` | `0d9280c3d3a9254f20c09ba958eb3876e957d245` | same |
| `git diff --check` | clean | clean |
| `git stash list` | 0 | 0 |
| commit / push / merge / rebase / PR | none | none |

Both the branch and HEAD matched the values carried forward from the predecessor
QA, so no divergence had to be reconciled.

## 3. Writer State

`relay/current.md` recorded `MONGLE-COMBINED-NAMING-AND-FRONTEND-INDEPENDENT-QA-001`
as `BLOCKED`, holding a claim on its own QA evidence plus a verified in-scope
correction to `start-mongle-phase1.sh`. That task's blockers are this task's
entire scope, so this task takes over the same file and continues rather than
contending for it. No other writer was active on the E2E harness, the frontend
Dockerfile or the Playwright config.

## 4. Authoritative Inputs

Read directly, not summarized from reports: `AGENTS.md`, `CLAUDE.md`,
`agent-system/rules.md`, `active.md`, `relay/current.md`, the three predecessor
reports, `tests/e2e/scripts/*.sh`, `mongle-phase1-teardown.ts`,
`playwright.mongle.config.ts`, `docker-compose.phase1.yml`,
`frontend/Dockerfile`, `frontend/package.json`, `frontend/package-lock.json`,
`backend/Dockerfile`, `backend/requirements.txt`, `backend/pytest.ini`,
`backend/tests/conftest.py`, `tests/README.md`, `engineering/TESTING_GUIDE.md`.

Every blocker below was re-reproduced locally. None of the predecessor's
explanations was carried over on trust — and one of them turned out to be wrong.

## 5. Previous Blocker Reproduction

### 5.1 Stale frontend image — **CONFIRMED, and only half-fixed**

`git diff` shows the predecessor's correction was a single line:
`up -d --wait frontend` → `up -d --build --wait frontend`.

That closes one path. It does not close the other, and the other is the wider
one: `playwright.mongle.config.ts` carried `reuseExistingServer: true`. When
anything already answers on `http://localhost:13001`, Playwright never runs the
webServer command at all — so the rebuild it now requests is skipped along with
everything else. A leftover container from a previous session serves the whole
suite. `--build` cannot help, because the script containing it is never invoked.

Confirmed by observation: with the stack left running, a second Playwright
invocation under the corrected config refused to start
(`http://localhost:13001 is already used`) — which is the *new* behaviour. Under
the old `true` setting the same situation was silent reuse.

### 5.2 BuildKit stall — **REPRODUCED, and the predecessor's cause is wrong**

A clean `--no-cache` build of `frontend/Dockerfile` was run and timed. It
completed in ~66 s. The breakdown is in the build log:

```
#3 [internal] load metadata for docker.io/library/nginx:alpine
#3 DONE 54.4s
...
#9 [internal] load build context
#9 transferring context: 106.98MB 0.7s done
```

54.4 s of a 66 s build was a **Docker Hub metadata fetch for the base image** —
network, not BuildKit, and not the build context. The context transfer, the
thing the predecessor blamed, took 0.7 s. Once the metadata is cached the same
build takes ~10 s.

So: the stall was an unpinned dependency on registry reachability. It is not
reproducible as a permanent blocker and is not a defect in this repository.

That said, the 106.98 MB / ~7 592-file context **is** a real defect for a
different reason — see §9.

### 5.3 Host `pytest_asyncio` — **CONFIRMED, and it is a repository gap**

```
python3 -V                          -> Python 3.9.6  (/usr/bin/python3, macOS system)
python3 -c "import pytest"          -> 8.3.4
python3 -c "import pytest_asyncio"  -> ModuleNotFoundError
grep pytest backend/requirements.txt -> (no match)
```

The repository declares **no test dependencies at all**, while
`tests/README.md` and `engineering/TESTING_GUIDE.md` both document
`cd backend && python3 -m pytest -q` as the measured invocation. That command
has been depending on whatever the host happened to have. `backend/pytest.ini`
sets `asyncio_mode = auto`, which makes `pytest-asyncio` mandatory, not
optional.

This is not a product failure. It is a missing declared environment, and the
collection error it produces reads exactly like a product failure — which is how
it was reported.

## 6. Docker / BuildKit Inspection

```
Server:   linux/arm64, engine 29.4.0 (OrbStack)
buildx:   v0.33.0     builder "orbstack" (docker driver), BuildKit v0.29.0, running
info:     driver overlay2, Arch aarch64, NCPU 10, MemTotal 8.39 GB
system df: Images 86 / 8.798GB   Containers 18   Volumes 73   Build Cache 5.691GB
```

`docker buildx ls` also lists a `desktop-linux` builder in `error` state
(Docker Desktop's socket is absent). It is not the active builder — `orbstack`
is — and it played no part in any build here.

## 7. Harness Audit

| Question | Answer as found |
|---|---|
| How does the harness start frontend? | `docker compose -p mc_phase1 -f docker-compose.phase1.yml up -d --build --wait frontend`, after db+backend are up and seeded |
| Was `--build` present? | Yes, added by the predecessor QA |
| Is that sufficient? | **No** — `reuseExistingServer: true` bypasses the script entirely |
| Can a stale *container* survive a successful rebuild? | **Yes** — `up` without `--force-recreate` leaves a running container on its old image |
| `.dockerignore`? | **None anywhere in the repository** |
| Is the DB disposable? | Yes — dedicated `phase1_pg_data` volume, `down -v` at teardown |
| Readiness? | db healthcheck + backend `/api/health` + synchronous seed before frontend starts; frontend URL is therefore a genuine readiness signal |

The readiness design was already sound and was left alone.

## 8. Corrections Applied

1. **`frontend/.dockerignore`** (new) — excludes `node_modules`, `dist`, build/test output, `.git`, logs, `.env*`.
2. **`frontend/Dockerfile`** — accepts `ARG BUILD_FINGERPRINT`, writes `dist/build-fingerprint.txt` (fingerprint + entry bundle name) and stamps `LABEL org.mongle.build-fingerprint`.
3. **`tests/e2e/scripts/frontend-source-fingerprint.sh`** (new) — deterministic SHA-256 over the frontend working tree.
4. **`tests/e2e/scripts/verify-current-source-frontend.sh`** (new) — the regression guard; compares worktree ⇄ image ⇄ served, and re-checks the `.dockerignore` exclusion.
5. **`tests/e2e/scripts/start-mongle-phase1.sh`** — computes/inherits the fingerprint, adds `--force-recreate` to the frontend bring-up, and runs the guard before returning.
6. **`docker-compose.phase1.yml`** — passes `BUILD_FINGERPRINT` through to the frontend build.
7. **`tests/e2e/playwright.mongle.config.ts`** — computes the fingerprint in the Playwright process so tests have something to compare against, and sets `reuseExistingServer: false`.
8. **`tests/e2e/specs-mongle/01-shell.spec.ts`** — new `Current-source runtime proof` describe, new Wagle seam test, new canonical-only-write test, `/admin/*` regression, three corrected expectations (§15/§16), and three stale `Doran` references in titles/comments renamed.
9. **`backend/requirements-dev.txt`** (new) — declares the backend test environment.

No product source file was modified.

## 9. Docker Context / `.dockerignore`

Measured before and after:

| | Context transferred | Files |
|---|---|---|
| Before | 106.98 MB | ~7 592 |
| After | **28.18 kB** | — |

The size was never the stall. The real problem is what was inside it. The
Dockerfile does `RUN npm ci` and *then* `COPY . .`, so the host's
darwin-arm64 `node_modules` was layered on top of the linux-arm64/musl tree the
container had just installed. Verified in the image:

```
before: node_modules/@rollup/ -> rollup-darwin-arm64 present (from the host)
after : node_modules/@rollup/ -> rollup-linux-arm64-gnu, rollup-linux-arm64-musl
        (darwin count: 0)
```

The build previously survived only because Rollup selects its native binary by
platform at runtime and the musl one happened to still be reachable alongside.
That is a coincidence, not a contract — and it is the same
`rollup-darwin-arm64` symptom that an earlier task recorded as a mount problem.
The image now depends on `package-lock.json` alone, which is what "clean
isolated build" has to mean.

## 10. Source Fingerprint

Hashes the **working tree**, deliberately not git: the files under verification
here are uncommitted (the storage-migration module is untracked), so anything
derived from `git ls-files` or HEAD would fingerprint source that is not what
gets built.

```
worktree fingerprint: cf5ed0acb2781201f845009a63dfdb6cc3cf983f1ca12b00675a80d1ca04e736
(recomputed twice, identical)
```

The value is published two ways — image label and a file the browser can
fetch — and the built entry bundle name is recorded next to it as a second,
independent witness: Vite content-hashes that name, so a page loading a
different one is not this build regardless of what the sidecar file claims.

## 11. Clean Isolated Build

Environment: throwaway Docker image, `linux/arm64`, npm (repository has
`package-lock.json` only — no pnpm/yarn lockfile), `npm ci`, container-only
`node_modules`. The host's `node_modules` was never mounted, deleted or
overwritten (verified afterwards: unchanged, `rollup-darwin-arm64` still
present, mtime untouched).

```
docker build --no-cache -> context 28.18kB, npm ci: 227 packages in 4s
npm run build           -> ✓ built in 1.00s
                           dist/assets/index-T37xMgOL.js   409.56 kB │ gzip: 132.39 kB
                           dist/assets/index-Bu7Rs38z.css  152.72 kB │ gzip:  27.45 kB
npx tsc --noEmit        -> EXIT=0
npm run lint (eslint)   -> clean
node --test tokenContract.test.mjs -> 29 pass / 0 fail
```

```text
CLEAN_ISOLATED_PRODUCTION_BUILD_PASS
```

## 12. Build Artifact Inspection

Run against the served document root of the built image:

```text
active doran                 : 0
naran (js)                   : 1
naran (css + html)           : 0
"/naran…" route literal      : none
canonical mongle key present : yes  (`return `mongle.activeFamily.${n}``)
wagle identifiers            : 17
```

The single `naran` occurrence, in full context:

```js
function Kc(n){return`mongle.activeFamily.${n}`}
const tA="naran";
function Em(n){return`${tA}.activeFamily.${n}`}
```

That is the constant-folded migration source. It **must** ship — without it the
one-time migration cannot read the old key in a real user's browser. It is
reachable only as a storage-migration/logout-cleanup input; it is not a route,
a service code, a navigation target or a component identifier. Classified
`STORAGE_MIGRATION_SOURCE`, not an active identifier.

## 13. Playwright Environment

- Compose project `mc_phase1`, dedicated network `mc_phase1_network`, dedicated volume `mc_phase1_phase1_pg_data`, removed by `down -v` at teardown. No shared/operating database was touched.
- Ports 13001/18001/15434 — confirmed free of both Docker and host listeners before bring-up.
- Readiness: db healthcheck → backend `/api/health` healthcheck → synchronous `phase1_seed_synthetic.py` → frontend built and started last → current-source guard.

## 14. Current-source Image Proof

```text
worktree fingerprint : cf5ed0acb2781201f845009a63dfdb6cc3cf983f1ca12b00675a80d1ca04e736
image fingerprint    : cf5ed0acb2781201f845009a63dfdb6cc3cf983f1ca12b00675a80d1ca04e736
served fingerprint   : cf5ed0acb2781201f845009a63dfdb6cc3cf983f1ca12b00675a80d1ca04e736
image id             : 64579ec23581983876bb57b997afb8ac3336c46893ad165c42d5e99a7d7e2cc6
served entry bundle  : /assets/index-T37xMgOL.js   (matches the built entry)
```

And from inside the browser, on all five projects:

```text
Current-source runtime proof › the browser is served the build made from this worktree
  5 passed
```

```text
CURRENT_SOURCE_FRONTEND_IMAGE_CONFIRMED
```

## 15. Playwright Route Results

Final run — clean bring-up, teardown enabled, **no retries configured and none
occurred**:

```text
collected : 90
passed    : 86
failed    : 0
skipped   : 4
duration  : 1.1m
```

The 4 skips are one desktop-only test (`internal Dock/nav clicks…`) declining on
the four non-desktop projects via a pre-existing `test.skip`. Nothing was
excluded, filtered or grep-inverted.

Route outcomes:

- `/naran`, `/naran/doran`, `/naran/family` (with query + hash): URL unchanged — **no redirect, no alias** — and the not-found page renders. ✓ ×5 projects
- Canonical `/`, `/dashboard`, `/wagle`, `/family` all resolve; `/admin/*` is registered and guarded (a non-admin is redirected away, which is a *different* outcome from the not-found page an unregistered path gives — that difference is the proof the route still exists). The path list was read from `frontend/src/App.tsx`, not copied from a report.
- Internal nav/Dock clicks produce canonical URLs only.

## 16. Playwright Storage Results

All five migration contracts pass on all five projects:

| Scenario | Result |
|---|---|
| Legacy key only → selection preserved, canonical created, retired key purged | ✓ |
| Retired + canonical both present, different values → canonical wins, retired purged | ✓ |
| Retired value points at an inaccessible Family → not adopted, asks instead, purged | ✓ |
| Malformed retired value → no crash, no selection, purged, not copied to canonical | ✓ |
| Idempotency — reload twice after migration → stable, retired key not recreated | ✓ |
| Changing active Family → **only** the canonical key is written, retired never recreated | ✓ |
| Explicit logout → both keys cleared, no resurrection on next login | ✓ |

## 17. Playwright Wagle Seam

New test, asserting payload and rendered consequence together — asserting only
the payload would still pass if the frontend compared the historical code:

```text
GET /api/account-context (bearer token read from sessionStorage)
  Synthetic Family Alpha services -> [ markpoint: active, wagle: active ]
  historical messaging code       -> absent
UI: /wagle renders "와글와글"; "와글와글을 사용할 수 없어요" count = 0
5 passed
```

## 18. Focused Backend Seam Test

Host Python was left untouched. A disposable environment was built instead:
`backend/requirements-dev.txt` (new) installed into a throwaway image, against a
volume-less PostgreSQL 16.9 container seeded with `database/init.sql`
(`psql -v ON_ERROR_STOP=1`, readiness proven by three consecutive successful
queries, not `pg_isready`) and migrated with `alembic upgrade head` →
`0008_markpoint_access_control`.

```
pytest 8.3.4, pytest_asyncio 0.26.0
pytest tests/test_frontend_service_code_contract.py --collect-only -q -> 3 tests collected
pytest tests/test_frontend_service_code_contract.py -v                -> 3 passed, EXIT=0

  test_account_context_emits_the_service_code_the_frontend_compares PASSED
  test_no_historical_service_code_reaches_the_frontend               PASSED
  test_subscription_rows_carry_the_target_service_code               PASSED
```

Measured here, not copied: the first attempt pinned `pytest-asyncio==0.25.0` and
produced **3 passed + 1 teardown ERROR**. Cause: `backend/pytest.ini` sets
`asyncio_default_test_loop_scope = session`, which 0.25.x does not recognise —
pytest reported it as an unknown config option, kept the per-test loop scope, and
the session fixture was then finalized against a loop that had moved on. Pinning
`0.26.0`, the version that honours the option, removes the error entirely. The
error was in the environment I chose, not in the product or the test.

```text
FOCUSED_BACKEND_WAGLE_SEAM_PASS
```

## 19. Naming Regression

Active — all zero:

```text
frontend active Doran runtime identifier   : 0
frontend active doran import/file          : 0
frontend 'doran' service-code literal      : 0
generated OpenAPI doran path               : 0
built bundle doran                         : 0
active /naran route registration           : 0
active Naran storage write                 : 0
active Naran component/import/file         : 0
backend active naran                       : 0
frontend Wagle service comparison present  : 2 (MongleAppShell.tsx, WagleLanding.tsx)
```

Allowed, enumerated rather than claimed absent:

```text
storage migration source (2)
  frontend/src/shared/storage/activeFamilyStorageMigration.ts:32
  tests/e2e/specs-mongle/01-shell.spec.ts:136
  (+1 constant-folded in the shipped bundle)
negative route input (1)
  01-shell.spec.ts:195 — retired paths built from the constant, as test input
prohibition / before-value strings (3)
  App.tsx:85 (comment recording the removal), and two test names describing
  what must not exist
frozen IDs and historical reports
  E2E-NARAN-SHELL-001 (Coverage Map row ID, cited by past QA), archived docs
```

## 20. Harness Regression

The guard was verified by making it fail, not by reading its PASS output.

A frontend image was built with a deliberately wrong fingerprint, tagged as the
Compose image name, and the container recreated from it:

```text
served: fingerprint=stale-image-negative-test
guard : STALE_FRONTEND_GUARD: FAIL — image was built from different source:
        worktree=cf5ed0acb278…e736 image=stale-image-negative-test
guard EXIT=1  (expected 1)
```

Restored immediately afterwards; the guard then returned PASS with all three
fingerprints equal.

Worth recording: the **first** attempt at this negative test appeared to show the
guard passing against a planted stale image. Investigating rather than accepting
it showed the plant had not actually taken — the container had not been
recreated, so the guard was correctly reporting on the good image. Had that
first result been written down, this report would claim a verified guard on the
strength of a test that never ran.

The guard is authoritative in a way the env var is not: it **recomputes** the
worktree fingerprint itself rather than trusting `MONGLE_FRONTEND_FINGERPRINT`,
so a forced or inherited variable cannot make it agree with a wrong image.

## 21. Self-QA

| # | Failure mode | Result |
|---|---|---|
| 1 | `--build` present but cache serves stale source | Closed — fingerprint is a build arg, so a source change changes the arg and busts the layer; the guard re-checks regardless |
| 2 | Host `node_modules` in the Docker context | Closed and measured (§9); guard fails if the exclusion is removed |
| 3 | Browser serving cached/old assets | Entry bundle is content-hashed and compared; fingerprint fetched with `cache: 'no-store'` |
| 4 | Fingerprint mismatch between worktree/image/browser | All three compared, in the guard and again in-browser |
| 5 | Playwright baseURL pointing at a different container | Guard curls the same `MONGLE_PLAYWRIGHT_BASE_URL` Playwright uses |
| 6 | New DB but stale frontend | `--force-recreate` on frontend + guard after `--wait` |
| 7 | Legacy key seeded after app init | Seeded via `page.evaluate` then `page.reload()`, so migration runs on a fresh load |
| 8 | Canonical assertion reading the wrong account's key | Keys are enumerated by prefix and the accountId is derived from the observed canonical key |
| 9 | Retries hiding flakiness | No retries configured; `retry`/`flaky` count in the final log: 0 |
| 10 | Backend test silently using host Python | Ran only in a throwaway container; host Python untouched and still lacks `pytest_asyncio` |
| 11 | Teardown removing another task's containers | Teardown is scoped to `-p mc_phase1`; QA-created extras removed by explicit name |
| 12 | Guard that only prints PASS | Falsified by the §20 negative test |

## 22. Recursive Scope Review

**Pass A — before changes.** Reproduced all three blockers. Predicted the files
needing change: `.dockerignore` (absent), `frontend/Dockerfile`, the harness
script, the Compose file, the Playwright config, and a backend test-dependency
declaration. One prediction was wrong in a useful way: I expected the context
size to be the stall and it was the registry metadata fetch.

**Pass B — after changes.** `git status` shows exactly the nine predicted files
and no product source. No global Docker cache was pruned; no other project's
container, image, volume or network was removed; the host `node_modules` is
byte-identical.

**Pass C — before closing.** Clean build evidence captured; current-source image
proven three ways plus in-browser; Playwright executed with real counts; backend
seam executed with real counts; Docker residuals zero; lifecycle updated.

## 23. Five-Gate Review

- **환각:** every number here came from a command run in this session. The predecessor's BuildKit explanation was re-tested and **contradicted** rather than repeated; the 41-failure figure is treated as invalidated, not restated. No PASS is claimed for anything unexecuted.
- **누락:** clean install, typecheck, lint, unit/contract, production build, artifact inspection, image proof, browser proof, route tests, storage tests, Wagle seam, backend seam, harness negative test, teardown — all present.
- **오작업:** host `node_modules` untouched; no global cache prune; no other project's resources removed; no assertion weakened, skipped or grep-excluded; no Naran alias or storage fallback reintroduced; no product code edited.
- **축혼동:** kept separate — product naming contract vs harness defect vs Docker environment; stale-image results vs current-source results; host build vs isolated clean build; my own test bugs vs product findings vs stale test expectations.
- **신선도·오탈자:** scripts match documented behaviour; Coverage Map rows updated to the executed state; `git diff --check` clean; fingerprints and image ids recorded.

## 24. Changed-file Manifest

**New (4):** `frontend/.dockerignore`,
`tests/e2e/scripts/frontend-source-fingerprint.sh`,
`tests/e2e/scripts/verify-current-source-frontend.sh`,
`backend/requirements-dev.txt`

**Modified (5):** `frontend/Dockerfile`, `docker-compose.phase1.yml`,
`tests/e2e/scripts/start-mongle-phase1.sh`,
`tests/e2e/playwright.mongle.config.ts`,
`tests/e2e/specs-mongle/01-shell.spec.ts`

**Records:** this report, `active.md`, `relay/current.md`, `COVERAGE_MAP.md`,
`graduated/2026-08.md`, and the archived handoffs.

Product source files changed: **none**.

**A useful accident in `active.md`.** Removing the seven graduated sections left
the file byte-identical to `HEAD` — `git diff -- agent-system/active.md` is
empty. That is the expected result and it doubles as a check: every section
removed was uncommitted content added by this bundle's own tasks, so if a
committed section had been deleted by mistake, the diff would show it. It does
not.

## 25. Docker Cleanup

```text
mc_phase1 containers : none
mc_phase1 volumes    : none
mc_phase1 networks   : none
mongle-seam-db       : removed
mongle-seam-net      : removed
QA build images      : mongle-repro-nodi:qa, mongle-frontend-clean:qa,
                       mongle-frontend-checks:qa, mongle-backend-test:qa — removed
```

`mc_phase1-frontend:latest` remains, carrying the **correct** fingerprint
(verified after the negative test, so the planted stale image is not left
behind). Other projects (`mc-*`, `outlook-*`, `viblot-*`, `mongle-wave5-qa-*`,
`mongle-frontend-toolchain`) were left exactly as found.

## 26. Lifecycle / Graduation

All §19 PASS conditions are met, so the naming bundle graduates:

| Task | Outcome |
|---|---|
| `MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001` (Track A) | GRADUATED |
| `MONGLE-W4-SERVICE-MARKPOINT-ACCESS-AUTONOMOUS-001` (Track B) | GRADUATED |
| `MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001` | GRADUATED |
| `MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001` | GRADUATED |
| `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001` | GRADUATED |
| `MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001` | GRADUATED |
| `MONGLE-COMBINED-NAMING-AND-FRONTEND-INDEPENDENT-QA-001` | GRADUATED |
| `MONGLE-PARALLEL-W2-W4-001` (parent bundle) | GRADUATED / COMPLETE |
| `MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001` (this) | GRADUATED |

Stated plainly so the basis is not overread: Track A, Track B and the migration
`0007`/`0008` catalog work were **not** re-verified here — that was explicitly
out of scope. Their graduation rests on
`MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001`, which passed the product
contract and left exactly three unexecuted verifications. Those three are what
this task executed. The bundle is complete because that gap is now closed, not
because everything was re-run.

## 27. Final Verdict

```text
E2E_ENVIRONMENT_RECOVERY_PASS
COMBINED_NAMING_INDEPENDENT_QA_PASS
WAGLE_FRONTEND_IDENTIFIER_LIFECYCLE_COMPLETE
NARAN_RUNTIME_RETIREMENT_LIFECYCLE_COMPLETE
MONGLE_STORAGE_KEY_MIGRATION_LIFECYCLE_COMPLETE
PARENT_INDEPENDENT_QA_PASS
MONGLE_PARALLEL_W2_W4_PARENT_COMPLETE
READY_FOR_NEXT_WAVE_START_REVIEW
```

Carried forward as known, not as blockers:

1. `TRACEABILITY_GAP` — the entire bundle is still uncommitted working state at `0d9280c`. PM performs commit/push.
2. `reuseExistingServer: false` means a leftover `mc_phase1` stack now blocks the next run with a clear error instead of silently reusing it. Loud is the correct direction, but it is a behaviour change for anyone used to the old flow.
3. Still no frontend component-test framework; screen behaviour is pinned at contract seams and by E2E.
4. `docker-compose.phase2.yml` still does not exist; the backend fixture DB is stood up by hand.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md` — the seven graduated sections were removed; the records now live in `agent-system/graduated/2026-08.md`.
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.md`
- Independent QA: `self` (this task is itself the independent execution of the three blocked verifications)
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `E2E-MONGLE-ROUTE-STORAGE-RETIREMENT-001` moves from FAIL/ENVIRONMENT to an executed PASS, and a new row records the harness current-source guard.
- CLOSEOUT GATE: `PASS`
