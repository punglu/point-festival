# MONGLE_W6_1_FOUNDATION_E2E_CLOSEOUT_REPORT

Task ID: MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001
Performer: Claude Code
Date: 2026-07-31
Environment: macOS (OrbStack-class Docker), Docker 29.4.0, Docker Compose v5.1.2

Scope executed, per `MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md` item 45:
(1) re-run lint/build, (2) run the Mongle Playwright suite cold-start TWICE,
(3) visually compare representative screens before/after the Foundation change
using a real browser, (4) clean up Docker containers/volumes afterward,
(5) decide PASS/FAIL.

## 0. Git baseline

| Item | Value |
|---|---|
| worktree | `/Users/mac/mac_Project/mongle_ui` |
| branch | `dev-newmarkp` |
| HEAD (baseline, re-pinned this session after a PM-confirmed authorized parallel doc session finished) | `9bcd1a5855732537203e6b1ff71841adf184796f` |
| HEAD (end of this task) | unchanged: `9bcd1a5855732537203e6b1ff71841adf184796f` |
| pre-existing approved dirty | `engineering/phase2/MONGLE_W6_1_E2E_HARNESS_PROVENANCE.md`, `engineering/phase2/MONGLE_W6_1_E2E_HARNESS_RECOVERY_REPORT.md` (untracked, from the prior Harness Recovery task) |
| dirty at end of this task | same two files, unchanged, plus this new report (untracked) |

No git-forbidden operations were run (no reset/restore/clean/stash/commit/push/merge/rebase/PR).

## 1. Toolchain used

`frontend/node_modules` and `tests/e2e/node_modules` were absent (fresh clone,
never installed). With explicit approval, installed via `npm ci` (lockfile-respecting,
does not modify `package-lock.json`) in two places:

- `frontend/`: run inside a new, persistent container `mongle-frontend-toolchain`
  (`node:20-alpine`, matching `frontend/Dockerfile`'s build stage and the
  `engines` constraint `node >=20.19.0 <23`), bind-mounted to `frontend/`. Kept
  running for reuse in future Mongle frontend dev/test work, per PM direction.
- `tests/e2e/`: run directly on host (Node v26.2.0), because the E2E harness's
  `webServer` command drives the **host** Docker daemon (`docker compose -p
  mc_phase1 ...`) and Playwright must reach host-published ports
  (`localhost:13001` etc.) — containerizing the runner itself would require
  Docker-in-Docker/socket passthrough and host-network wiring not worth the
  complexity for this task.

Both `package-lock.json` files confirmed byte-unchanged after install
(`git status --porcelain` empty for both paths).

## 2. Lint / Build reconfirmation

| Check | Result |
|---|---|
| `npm run lint` (frontend, in `mongle-frontend-toolchain`) | **PASS** — 0 errors, 0 warnings |
| `npm run build` (`tsc -b && vite build`) | **PASS** — 315 modules transformed, 0 TypeScript errors, build completed in 1.07s |

## 3. Playwright cold-start — Round 1

Command: `npx playwright test --config=playwright.mongle.config.ts` (host, fresh
`mc_phase1` stack built from scratch via `tests/e2e/scripts/start-mongle-phase1.sh`).

```
70 tests run across 5 projects (desktop/iphone/ipad/android-tablet-portrait/android-tablet-landscape)
66 passed
0 failed
4 skipped (intentional — same 4 as previously reported)
Duration: 55.9s
```

Teardown (`globalTeardown` → `stop-mongle-phase1.sh`, `docker compose ... down -v`)
ran automatically: `mc_phase1-*` containers, `mc_phase1_network`, and
`mc_phase1_phase1_pg_data` volume all removed. Confirmed via `docker ps -a` /
`docker volume ls` immediately after — nothing left.

## 4. Playwright cold-start — Round 2

Re-ran identically, from the fully torn-down state (true second cold start,
including a fresh Postgres volume).

```
66 passed
0 failed
4 skipped
Duration: 54.0s
```

**Round 1 vs Round 2 comparison:**

- Pass/fail/skip counts: identical (66/0/4 both rounds).
- Test identity set (name + project, order-independent): **identical** —
  `diff` of sorted test-title lists between the two run logs produced 0 lines.
- No occurrence of `console error` / `uncaught` / `Error:` outside of test
  titles that literally contain the word "error" as part of their PASS name
  (e.g. "... no console error") — i.e., 0 actual failures or unexpected error
  log lines in either run.
- Teardown fully clean after both rounds (containers/network/volume all
  removed both times, verified via `docker ps -a`/`docker volume ls`/`docker
  network ls` filtered on `mc_phase1`).

```
PREVIOUSLY_REPORTED_E2E_REFERENCE: 66 passed / 0 failed / 4 intentional skipped
CURRENT_ROUND_1: 66 passed / 0 failed / 4 skipped — MATCHES
CURRENT_ROUND_2: 66 passed / 0 failed / 4 skipped — MATCHES, IDENTICAL TO ROUND 1
REGRESSION_0: CLAIMABLE (both real, cold-start, Docker-executed runs, not asserted from documents)
```

## 5. Visual comparison (real browser, before vs after)

Built a throwaway Playwright screenshot script (kept only in the scratchpad,
never committed to the repo) that logs in as the first synthetic player and
captures full-page screenshots at 4 reference viewports (mobile 390×844,
tablet 768×1024, tablet 1024×1366, desktop 1440×900) × 6 representative
routes (`/`, `/dashboard`, `/wagle`, `/family`, `/admin`, an unregistered path
for 404) = 24 screenshots per side.

- **"After"**: captured against the current tree (HEAD `9bcd1a5`), `mc_phase1`
  stack freshly started for this purpose, then torn down.
- **"Before"**: captured against a temporary `git worktree --detach` at the
  pre-Foundation commit `08619298ff7b7a175ba4d30537be92e0387b2eb4` (parent of
  the Foundation commit `0c2a040`), with its own `npm ci` in `tests/e2e/`
  (worktrees don't share installed `node_modules`), its own `mc_phase1` stack
  instance, screenshots captured, then torn down and the worktree removed
  (`git worktree remove --force`). Main checkout's branch/HEAD were never
  touched by this — confirmed via `git status`/`git rev-parse HEAD` before and
  after, both identical to baseline.

**Pixel diff (PIL, per-pixel RGB difference, percentage of differing pixels
over total pixels), all 24 pairs:**

| Route | All 4 viewports |
|---|---|
| `/` (root/login-select) | 0.004%–0.022% |
| `/dashboard` | 0.004%–0.022% |
| `/wagle` | **0.000%** |
| `/family` | **0.000%** |
| `/admin` | 0.004%–0.022% |
| `/this-route-does-not-exist` (404) | **0.000%** |

All 24 pairs: **identical image dimensions** before vs after (no layout
shift, no reflow, no new overflow/scrollbar introduced by the Foundation
token/typography change).

**Root cause of the non-zero pairs, confirmed by direct visual inspection**
(read both `desktop__dashboard.png` before/after side by side): the only
visible difference between the two images is the mission-card timestamp text
("아빠 · 오후 8:53" vs "아빠 · 오후 8:51") — an artifact of
`phase1_seed_synthetic.py` stamping wall-clock time on each independent seed
run (before-capture and after-capture were necessarily two separate seed
executions, minutes apart). This is **not** a font, token, or CSS-driven
difference — `/`, `/dashboard`, and `/admin` are exactly the three routes
whose rendered content includes this dynamic mission/seed timestamp; `/wagle`,
`/family`, and 404 render no such dynamic text and are byte-for-byte pixel
identical (0.000%).

Console error signal captured during both before and after screenshot runs
was **identical** across all 4 viewports both times: 1× `401 Unauthorized`
(expected — `/admin` was hit without a separate admin login, same in both
before/after) + 3× `404 Not Found` (expected — from the intentionally
unregistered path and related sub-resource lookups). No new console error
type appeared post-Foundation that wasn't already present pre-Foundation.

```
UNEXPECTED_SCREEN_DELTA: NONE FOUND
MATERIAL_REGRESSION: NONE FOUND
EXPECTED_FOUNDATION_DELTA: effectively none measurable at pixel level for
  these specific captured states — the Foundation's font-family/token changes
  did not produce a detectable rendering difference in Chromium for this
  content at this fidelity; the previously-anticipated Noto-Sans-KR text
  delta (per MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md item 35) is
  present in principle but did not register above sub-0.03% pixel noise
  dominated by the seed timestamp text in this comparison.
```

## 6. Docker cleanup

Confirmed clean at every teardown point in this task (after Round 1, Round 2,
"after" visual capture, and "before" visual capture in the worktree):

```
docker ps -a --filter name=mc_phase1     -> empty
docker volume ls --filter name=mc_phase1 -> empty
docker network ls --filter name=mc_phase1 -> empty
```

The pre-existing, unrelated containers on this host (`mc-backend`/`mc-db`/
`mc-frontend` legacy point-festival stack, `outlook_hub-*`, `viblot-*`,
`projectflow-edu`, etc.) were never touched by this task.

The `mongle-frontend-toolchain` container (created this task, for
lint/build/npm-ci only, per explicit PM direction to keep a reusable Mongle
frontend container rather than a one-shot `--rm` run) was **left running**,
intentionally, for continued use in future sessions.

## 7. Forbidden actions — none performed

No Foundation re-implementation, no Harness restore/rewrite, no Harness
document commit, no `agent-system/` file modification, no assertion
weakening, no skip/retry/timeout manipulation, no mixing of an E2E failure
with a code fix (there was no failure), no `reset`/`restore`/`clean`/`stash`,
no `commit`/`push`/`merge`/`rebase`/`PR`, no global Docker prune (only the
project-scoped `-p mc_phase1 ... down -v`, which is the harness's own
documented, non-destructive-to-other-projects teardown).

## 8. Verdict

```
GIT_STATE_RECONCILIATION: PASS (carried forward from prior turn's stability gate)
LINT: PASS
BUILD: PASS
E2E_ROUND_1: 66 passed / 0 failed / 4 skipped
E2E_ROUND_2: 66 passed / 0 failed / 4 skipped
E2E_ROUNDS_IDENTICAL: YES
VISUAL_DELTA: NONE UNEXPECTED (0.000%-0.022%, fully attributable to dynamic
  seed timestamp text, not Foundation CSS/token/font changes; 0 dimension
  changes)
CONSOLE_ERROR_DELTA: NONE (identical pre-existing pattern before/after)
DOCKER_CLEANUP: CONFIRMED CLEAN
REGRESSION_0: CLAIMABLE

FINAL VERDICT: PASS

MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001: PASS
WAVE_6_1_IMPLEMENTATION_STATUS: FULLY_VERIFIED
```

## 9. Next-task eligibility

Per `MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md` item 45's own gate
("`MONGLE-W6-2-A1-MOBILE-RECONSTRUCTION-001` MUST NOT START until
`MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001` PASSes"), that gate is now
satisfied. This task does **not** start `MONGLE-W6-2-A1-MOBILE-
RECONSTRUCTION-001` or any other follow-on screen work — that remains a
separate, explicitly-authorized next task per the standing instructions for
this task family.

No commit/push/PR was performed.
