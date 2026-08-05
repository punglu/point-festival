# QA Evidence — MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Role: Developer self-check (implementer). **Not** Independent QA — per
  `agent-system/rules.md` Invariant 6, this session cannot award its own
  final QA PASS. A separate focused Independent QA pass is the correct
  next step.
- Full narrative context, per-row disposition, and design-decision
  reasoning: see this task's own handoff,
  `agent-system/handoffs/active/MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md`.
  This file records the concrete evidence only.

## Baseline

- Branch: `dev-newmarkp`
- HEAD at start: `97bc09ddf1bd3c3002b969f89c089bd3d423e04a`
- `git status --short` at start: clean
- `git stash list` at start: empty

## Static checks

| Check | Command | Result |
|---|---|---|
| Lint | `pnpm run lint` (frontend/) | PASS — 0 errors/warnings (besides pre-existing Node-engine-version notice) |
| Typecheck + build | `pnpm run build` (`tsc -b && vite build`) | PASS — clean compile, production bundle built |
| Diff whitespace | `git diff --check` | PASS — clean |
| Diff scope | `git status --short` | Matches declared file list exactly, no unrelated drift |

## Runtime checks (executed against the project's own native dev stack)

Environment: `./dev.sh start` — native `uvicorn` (backend `.venv`,
`app.main:app`, port 8000) + `pnpm run dev` (Vite, port 5174) + native
local PostgreSQL 16, DB `mc_festival` (existing persistent dev DB,
`alembic upgrade head` run by `dev.sh` itself). No Docker used or
required.

### Backend API shape confirmation

```
$ curl -s http://localhost:8000/api/players
[{"id":1,"name":"유빈",...,"is_locked":false,"total_points":0,...},
 {"id":2,"name":"유현",...}, {"id":3,"name":"아빠",...}, {"id":4,"name":"엄마",...}]

$ curl -s http://localhost:8000/api/configs/level.thresholds
{"detail":"인증이 필요합니다"}   # 401, pre-existing/unauthenticated — same as legacy code's own identical fetch
```

Confirms `ProfileSelectorContainer`'s data-shape assumptions (`id`,
`name`, `is_locked`, `total_points`) against the real running backend, and
confirms the level-thresholds 401 is a pre-existing condition inherited
unchanged from the legacy component (both old and new code make the exact
same unauthenticated call and both fall back to `thresholds = null`).

### Browser check (Playwright, ad hoc script — not committed, deleted after use)

Runtime: `tests/e2e`'s pinned `@playwright/test@1.58.2`; matching
Chromium installed via `PLAYWRIGHT_BROWSERS_PATH=0
./node_modules/.bin/playwright install chromium` (the exact command
documented in `tests/README.md`), not an unpinned/latest install.

| Check | Result |
|---|---|
| `/` renders canonical `1a` (`[data-canonical-screen-id="1a"]` count) | `1` |
| Profile buttons show real backend names/points | `["유유빈★0P›","유유현★0P›","아아빠★0P›","엄엄마★0P›","관리자 로그인 ›"]` (no fixture data) |
| Click real profile "유빈" → navigates to real PIN screen | PASS — header shows "유빈", "PIN 번호를 입력하세요", real keypad rendered |
| "← 다른 플레이어 선택" → returns to `1a` | PASS — `[data-canonical-screen-id="1a"]` count `1` again |
| Console/page errors beyond the pre-existing 401s | None |
| Mutation to DB during the check | None — GET-only + client-side navigation; no PIN submitted, no login completed |
| `git status --short` after the check | Clean (no runner-induced drift) |

### Responsive check

| Viewport | Horizontal overflow | Profile buttons rendered |
|---|---|---|
| 390×844 | `false` | 5 |
| 820×1180 | `false` | 5 |
| 1180×820 | `false` | 5 |

## Deferred rows — evidence that the blocker is real, not asserted

- `1j`/`1j-1`: `pages/PinEntryPreview/index.tsx` and
  `pages/AccountLockPreview/index.tsx` read directly — both are static
  `data-implementation-mode="ui-only"` components with no props/model
  contract and no live route (`grep` for both component names in
  `App.tsx` shows only their own `/__wave6/*` preview route, never
  imported into `pages/Auth/**`). `GET /api/players` (above) confirmed
  the backend exposes only `is_locked: boolean`, no attempt count or
  retry timestamp — the frozen `1j-1` visual's specific "5회 실패"/"5분
  후" copy has no real data to source from.
- `2s`: not re-investigated this task; re-cites
  `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001`'s own Phase B finding
  (`agent-system/active.md` lines ~696-698 at time of this task) verbatim
  rather than re-deriving it, since no code in the relevant path changed
  since that finding.

## Known gaps (disclosed)

- No currently-locked seed player existed in this session's DB, so the
  container-level locked-profile guard (`ProfileSelectorContainer`'s
  `handleSelect` not forwarding `onPlayerSelect` for `is_locked`) was
  verified by code inspection (byte-identical condition to the legacy
  `PlayerCard`'s `disabled` check) but not exercised live in the browser.
- The committed Playwright spec suite (`tests/e2e/specs-mongle/**`) was
  not run/extended — no existing spec references `1a` or
  `ProfileSelectorContainer`; adding one was judged out of scope for this
  single-slice task given a real, passing manual runtime check was
  already produced covering the same behavior.
- `1a-1` was regression-reviewed by diff only (confirmed 0 change), not
  re-executed end-to-end this session.

## Final Declaration

- Verification: `DEVELOPER_SELF_CHECK_COMPLETE` / `INDEPENDENT_QA_PENDING`.
- This is explicitly **not** a self-declared Independent QA PASS.
- No product/backend/migration/seed/auth-policy/session-storage/RBAC/
  PIN-policy change of any kind. No commit/push/merge/rebase performed.
