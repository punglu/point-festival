# MONGLE_FE_ROUTE_ALIGNMENT_REPORT

TASK ID: MONGLE-FE-ROUTE-ALIGNMENT-001

## Final Verdict

**PASS — 승격됨 (MONGLE-FE-E2E-HARNESS-RESTORE-001 + MONGLE-E2E-DORAN-SUBSCRIPTION-SEED-ALIGNMENT-001 완료 후)**

> **갱신 이력**: 최초 작성 시 `CONDITIONAL`이었음 — E2E 인프라가 폐기되어 전체 스위트를 실행할 수 없었고(§11의 옛 항목 2), 1건의 열린 명명 질문이 있었음(§7). 후속 작업 `MONGLE-FE-E2E-HARNESS-RESTORE-001`이 인프라를 복구했고, 그 과정에서 드러난 `doran` 서비스 구독 시드 누락 회귀는 `MONGLE-E2E-DORAN-SUBSCRIPTION-SEED-ALIGNMENT-001`에서 해결됨. 콜드 스타트 2회 연속 **30/30 PASS** 확보로 이 작업의 CONDITIONAL 사유(E2E 미실행)가 완전히 해소되어 PASS로 승격. 명명 질문(§7 와글와글/몽글)은 이후 `MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001`에서 RESOLVED 처리됨(몽글=플랫폼, 와글와글=메시징 기능 표시명, doran=내부 기술 도메인 — `MONGLE_NAMING_INVENTORY.md` §3.1 참고) — 자세한 내용은 `MONGLE_FE_E2E_HARNESS_RESTORE_REPORT.md`와 `MONGLE_E2E_DORAN_SUBSCRIPTION_SEED_ALIGNMENT_REPORT.md` 참고.

> **Namespace rename note (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, added after this document was written):** `NaranAppShell` → `MongleAppShell`, `specs-naran` → `specs-mongle`, `playwright.naran.config.ts` → `playwright.mongle.config.ts`. File:line citations in this document reflect the state at write time and are not retroactively updated. Route strings (`/naran/doran`, `/naran/family`) are unaffected and remain accurate.

## Start Gate

| Item | Value |
|---|---|
| Worktree | `/Users/mac/mac_Project/minecraft_points_festivals_doran_ui` (confirmed, matches candidate) |
| Branch | `dev-newmarkp` (confirmed, matches candidate) |
| HEAD (start) | `b0aea1d208f94ba928342d423c0f15048ca8b34d` |
| `git status --short` (start) | only `tests/e2e/test-results/**` noise (pre-existing, unrelated) |
| Dirty diff | limited to test-results artifacts; 0 source files dirty at start |
| Untracked files | 5 `tests/e2e/test-results/**` directories (Playwright run artifacts, pre-existing) |
| Other session activity | none detected |
| Package manager | npm (`frontend/package-lock.json`) |
| Frontend framework/router | React 18.3 + Vite 6 + `react-router-dom` 6.28 |
| Frontend entry point | `frontend/src/main.tsx` → `App.tsx` |
| Test command | `npx playwright test` (in `tests/e2e/`), config-specific: `--config playwright.naran.config.ts` for the Naran shell suite |
| Build command | `npm run build` (= `tsc -b && vite build`) |
| Reference package path | `/Users/mac/mac_Project/minecraft_points_festivals/temp/design_handoff_family_platform/` |
| Reference: tokenized HTML present | Yes |
| Reference: `TOKENIZATION_REPAIR_REPORT.md` present | Yes |
| Reference: approved-original SHA-256 | `d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9` (unchanged throughout this task) |
| Reference: tokenized wrapper count | 72 (first `1a`, last `3l`) |
| Reference modification this task | **0** |

**Start Gate verdict: PASS** — no FAIL condition triggered; dirty state was pre-existing noise, not a conflict.

## Wave 1 — Screen Reference Baseline

- Parsed all 72 screen wrappers (66 visible + 6 hidden), confirmed order matches the approved source exactly.
- Classified by type using only direct structural/textual evidence (hidden-attribute check, backdrop-overlay signal, source comments) — left genuinely uncertain modal-vs-full-screen calls explicitly unconfirmed rather than guessed.
- Established the 7-tier authority order per PM directive.
- **Verdict: PASS.** Deliverable: `engineering/phase2/MONGLE_SCREEN_REFERENCE_BASELINE.md`.

## Wave 2 — Route Audit

- Enumerated the full route tree (5 top-level + 7 nested admin routes) and every `navigate`/`Link`/`NavLink`/`window.location`/redirect call site (≈25 call sites across 12 files).
- Found **0 broken/orphan link targets** among everything currently wired up — a positive, verified finding, not assumed.
- Found **1 systemic gap**: no top-level catch-all/404 route (blank page on any unmatched path).
- Found and precisely documented **two parallel, non-unified chat systems** (legacy `ChatModal`, real API vs. new `DoranLanding` Room List, fixture-only) — reported as a fact, not resolved or unified (out of this task's scope).
- Confirmed nginx SPA fallback and Vite config are unaffected by any FE-only route change.
- **Verdict: PASS** (non-blocking gap carried to Wave 4). Deliverable: `engineering/phase2/MONGLE_ROUTE_AUDIT.md`.

## Wave 3 — Naming ('몽글') Cleanup

- Found **zero** literal user-visible `도란`/`Doran` text anywhere in the frontend — the app-level rename to `몽글` had already been completed in the pre-existing `b0aea1d` checkpoint, before this task began. This is reported honestly as a finding, not fabricated as "work done this wave."
- Found and precisely documented **one genuine open question**: `와글와글` is used consistently (9 occurrences, 4 files) as the specific display name for the chat/Doran feature, distinct from the app-level `몽글` brand. The PM's task text names only `도란→몽글` as in scope; `와글와글` was never mentioned. **This was deliberately left unchanged** rather than guessed in either direction — see §7 below.
- Recorded the PM's mid-task naming/URL decision (`Mongle Home` / `Mongle` / `www.mongle.life` / `PUBLIC_APP_URL` env-var pattern / no internal `doran→mongle` rename) as a documentation-only addendum — confirmed no domain string is hardcoded anywhere in the repo (0 hits before and after).
- **Verdict: PASS** (0 code changes required or made; one item explicitly flagged, not silently resolved). Deliverable: `engineering/phase2/MONGLE_NAMING_INVENTORY.md`.

## Wave 4 — Screen/Route/Dock Matrix + Minimum Repair

- Built the full 72-row matrix (`engineering/phase2/MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`), cross-referencing Waves 1-2's evidence plus direct component reads. 15 `IMPLEMENTED_MATCH`, 33 `FUTURE_IMPLEMENTATION`, 9 `NOT_PRODUCT_SCREEN`, remainder split across mismatch/modal/state categories.
- Confirmed the Dock's current 3-slot/3-label scheme (마크포인트/와글와글/가족) does not match the approved 4-slot mockup (홈/포인트잔치/대화/나) — this is the **same, already-PM-flagged, backend-blocked gap** found in the prior `DOCK_EXISTING_CONTRACT_AUDIT.md` session. **Not hardcoded around**, per explicit prohibition.
- Identified screen `3l` (바로가기 편집) as the almost-certain intended home for a future Dock-configuration UI — documented, not built.
- **The only evidence-backed minimal route repair found**: no top-level 404/fallback route existed. Implemented one (`App.tsx`), reusing the existing `PlatformPages.module.css` pattern (no new stylesheet, no refactor of unrelated code).
- Added one new E2E test case asserting the fallback renders instead of a blank page.
- **No canonical route was renamed.** `/naran/doran` remains as-is; `/mongle` was not adopted, per explicit instruction not to decide this without stronger evidence than currently exists.
- **No API/DB/backend file was touched.**
- **Verdict: CONDITIONAL** — the code fix itself is complete and verified; the full existing E2E suite could not be executed (see §11).

## Files modified

| File | Change |
|---|---|
| `frontend/src/App.tsx` | Added a `NotFoundPage` component and a top-level `path="*"` catch-all route. No existing route's path, guard, or element changed. |
| `tests/e2e/specs-naran/01-shell.spec.ts` | Added one new test case for the 404 fallback. No existing test modified, skipped, or weakened. |
| `frontend/package.json` / `frontend/package-lock.json` | Added `@types/node` as a devDependency — fixes a pre-existing `tsc -b` build failure in `vite.config.ts` (unrelated file, introduced in the pre-existing `b0aea1d` commit, not by this task) that blocked the "build 통과" gate this same task requires. Type-only addition; no runtime behavior change. |

## Files intentionally NOT modified

- `frontend/src/platform/pages/DoranLanding.tsx`, `NaranAppShell.tsx`, and all `platform/doran/**` files — no `도란`/`Doran` user-visible text existed to fix; the `와글와글` question was left open (§7), not silently resolved.
- Any backend file, any `doran` internal identifier, any route path string (`/naran/doran`, `/admin/*`, etc.), any Dock hardcoded array beyond adding nothing — Dock's 3-item array is unchanged.
- `nginx.conf`, `vite.config.ts`'s proxy logic — confirmed unaffected by the new FE-only route.
- Reference package (`temp/design_handoff_family_platform/`) — 0 files touched, 0 Drive operations.

## Route tree — before and after

Before (Wave 2 finding) = **identical to after**, except one addition:

```
/                    → AuthPage
/dashboard            → NaranAppShell → UserDashboard
/admin/*               → NaranAppShell → AdminDashboard (7 nested routes, unchanged)
/naran/doran           → NaranAppShell → DoranLanding
/naran/family          → NaranAppShell → AccessBoundary → FamilyLanding
/*  (NEW)              → NotFoundPage                                    ← Wave 4 addition, the only tree change
```

## User-visible '도란' removal result

**Already 0 before this task started.** No removal work was necessary or performed. See `MONGLE_NAMING_INVENTORY.md` §1.

## Remaining internal `doran` identifiers and why they stay

Confirmed internal-only (component names, file paths, TS types, one CSS/backend comment, one nginx location-block comment, the `service_code` string, the `platform/doran/` directory) — all protected under the PM's explicit instruction #8/#10 not to bulk-rename internal identifiers in this task. Full occurrence-by-occurrence list in `MONGLE_NAMING_INVENTORY.md` §2.

## Screen ↔ Route ↔ Dock mapping summary

Full 72-row detail in `MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`. Headline: roughly 20% of approved screens (15/72) map cleanly to an implemented route/component; ~46% (33/72) are genuinely unimplemented features (calendar, album, board, search, widget gallery, onboarding, invites — none hallucinated as "in progress," all confirmed absent by direct grep); the remainder are modal/state variants that correctly have no route, or design-only hidden drafts.

## Route error fixes made

1. Added a top-level `path="*"` fallback route + `NotFoundPage` component in `App.tsx` (the one systemic gap found in Wave 2).

## Redirect/alias list

None added. No canonical route renamed, so no legacy-alias/redirect was needed. (`AdminDashboard`'s existing nested `path="*"` → `Navigate to /admin` was already present and correct — not a new addition.)

## Direct access / refresh results

Manually verified live against a fresh `npm run dev` instance of this exact worktree (port 5175, proxied to a running `mc-backend` container):
- `/`, `/dashboard`, `/naran/doran`, `/naran/family`, `/admin` — all render non-blank content (consistent with unauthenticated redirect-to-`/` behavior; no regression).
- `/this-path-does-not-exist` — now renders the new "페이지를 찾을 수 없어요" heading + "몽글로 돌아가기" link (previously would have rendered blank).
- 0 browser console/page errors observed across all six checks.

## Lint / typecheck / build / test results

| Check | Result |
|---|---|
| `npm run lint` | **PASS**, exit 0, 0 errors/warnings |
| `npm run build` (`tsc -b && vite build`) | **PASS**, exit 0 — after fixing the pre-existing `@types/node` gap (see Files Modified); build output confirmed (315 modules, `dist/` produced) |
| E2E (`tests/e2e/specs-naran/01-shell.spec.ts` via `playwright.naran.config.ts`) | **NOT EXECUTABLE this session** — its documented isolated test stack (`mc_phase1` Docker compose, ports 15434/18001/13001) has been retired from this repository (confirmed absent via `find`; matches the repo's own `chore(infra): retire phase0/phase1 isolated dev runtime` history). This predates this task. In its place, the new route/test was verified manually via a live `npm run dev` instance (see §"Direct access / refresh results" above) — real evidence, but not equivalent to running the full existing spec file end-to-end. |
| Root `tests/e2e/specs/*.spec.ts` suite | Also not executed — same reason, plus its `docker-compose.phase0.yml` dependency is likewise absent; unrelated to this task's file changes. |

## API/DB change evidence

**Zero.** No file under `backend/`, `database/`, or any `*.py` was opened for writing this task. `git diff --stat` (final) touches only `frontend/src/App.tsx`, `frontend/package.json`, `frontend/package-lock.json`, and `tests/e2e/specs-naran/01-shell.spec.ts`.

## Remaining non-blocking items

1. **`와글와글` vs `몽글` naming** (Wave 3 §3) — genuine open PM question, deliberately not resolved by this task. If the PM confirms unification, the specific 9 occurrences + 1 E2E assertion are already enumerated in `MONGLE_NAMING_INVENTORY.md` for a fast follow-up.
2. **E2E suite execution** — blocked by retired `mc_phase1` infra, not by anything this task changed. Rebuilding that isolated test stack is infrastructure work, out of this task's scope.
3. **Dock 4-slot / user-configurable Dock / `3l` shortcut editor** — confirmed still blocked on the same backend gap recorded in the prior `DOCK_EXISTING_CONTRACT_AUDIT.md` session. Not re-litigated or worked around here.
4. **33 `FUTURE_IMPLEMENTATION` screens** — real, unimplemented features (calendar, album, board, search, invites, onboarding, widget gallery, redemption/reward-shop flow). None built in this task, per explicit scope limits.
5. Several matrix rows (1k, 1s, 1v, 2m, 2o, 2s, 2t, 2x, 2z) are marked "not deeply re-verified this pass" — reasonable-confidence inferences from adjacent evidence, not fabricated certainty. A deeper per-feature audit would firm these up if needed later.

## Risk

- **Low**: the only functional code change (404 route) is additive, isolated, and directly verified live; it cannot regress any existing route since React Router matches more specific paths first.
- **Low-medium**: the unresolved `와글와글`/`몽글` question means the app currently ships with two different-sounding names for "the chat feature" vs. "the app" — a real but pre-existing (not newly introduced) user-facing inconsistency.
- **Medium**: E2E regression coverage for this exact worktree cannot currently be run at all (infra retired) — this is a pre-existing testing gap this task surfaced but did not create or fix.

## Generated documents

- `engineering/phase2/MONGLE_SCREEN_REFERENCE_BASELINE.md`
- `engineering/phase2/MONGLE_ROUTE_AUDIT.md`
- `engineering/phase2/MONGLE_NAMING_INVENTORY.md`
- `engineering/phase2/MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`
- `engineering/phase2/MONGLE_FE_ROUTE_ALIGNMENT_REPORT.md` (this file)

## Git status

- No commit, push, merge, reset, clean, or stash performed at any point in this task.
- Final `git status --short` (this worktree): `App.tsx`, `package.json`, `package-lock.json`, `tests/e2e/specs-naran/01-shell.spec.ts` modified (all reviewed above); 4 new files under `engineering/phase2/`; pre-existing `tests/e2e/test-results/**` noise unchanged in nature (new run artifacts from this session's manual test executions).
- Branch remains `dev-newmarkp`, still 1 commit ahead of `origin/dev-newmarkp` (from the pre-existing `b0aea1d`, unrelated to this task) — not pushed.
