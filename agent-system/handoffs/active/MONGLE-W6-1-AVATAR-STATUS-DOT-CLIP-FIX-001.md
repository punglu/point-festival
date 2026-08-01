# MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001

- Task ID: `MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001`
- author/agent: Claude Code
- created_at: 2026-07-31
- git_ref: worktree `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`, HEAD `9bcd1a5855732537203e6b1ff71841adf184796f` (unchanged; nothing committed)
- environment: macOS, Docker 29.4.0, isolated `mc_phase1` stack
- evidence: this handoff + `agent-system/qa/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `9bcd1a5855732537203e6b1ff71841adf184796f`
- End HEAD: unchanged (no commit made)
- Final Commit: none yet — PM directed this land in a governance/Foundation-only
  commit separate from A1 code, after independent QA

## Goal

Fix the shared `Avatar` primitive's status-dot clipping defect (PM-directed,
split out of the isolated A1 visual publishing task rather than worked around
in A1's own files): `.avatar`'s `overflow: hidden` (needed to clip the
image/fallback into a circle) also clipped the corner-positioned
`.statusDot`, cutting it into a quarter-circle. Zero existing consumers pass
`status` today; A1's `PlayerCard` was the first real caller to expose it.

## Worktree and changed files

- Changed Files:
  - `frontend/src/shared/components/Avatar/Avatar.tsx` — wrapped the
    image/fallback branch in a new inner `<span className={styles.avatarInner}>`;
    `statusDot`/`srOnly` spans remain direct children of the outer `.avatar`,
    now siblings of `.avatarInner` rather than of the image/fallback directly.
  - `frontend/src/shared/components/Avatar/Avatar.module.css` — moved
    `overflow: hidden` off `.avatar` onto the new `.avatarInner` rule
    (`display:flex; align-items:center; justify-content:center; width:100%;
    height:100%; border-radius: var(--radius-pill); overflow:hidden`).
    `.avatar` keeps `position:relative`, its border-radius, background, and
    color — everything except the clip.
  - `frontend/src/shared/tokens/tokenContract.test.mjs` — added 3 static
    source-contract tests under the existing "(B) Avatar primitive tests"
    section (same `node:test`/`node:assert`, zero-new-dependency pattern
    already established in this file): `.avatar` no longer declares
    `overflow:hidden`, `.avatarInner` does; `Avatar.tsx` renders the inner
    wrapper; `statusDot` is rendered after `avatarInner`'s closing tag
    (i.e., a sibling, not nested inside it).
- Existing Dirty State: none new introduced by this task; the pre-existing
  Wave 6.1 governance dirty files (three `MONGLE_W6_1_*` reports, three
  `agent-system/handoffs/active/MONGLE-W6-1-*` files, three
  `agent-system/qa/MONGLE-W6-1-*` files) were already present at task start
  and are untouched by this specific fix (they belong to the separate
  Foundation E2E Closeout / governance-addendum work done earlier this
  session).

## Commands and outcomes

- Confirmed zero existing consumers pass `status`:
  `grep -rn "status=" frontend/src --include="*.tsx"` → no hits outside
  the isolated A1 worktree's `PlayerCard.tsx` (not part of this worktree).
- Confirmed no external CSS reaches into Avatar's internal DOM structure
  (`grep` for `Avatar.module`/`:global(...avatar`/`avatar >` across
  `frontend/src/**/*.css` outside `Avatar.module.css` itself) → no hits, so
  restructuring the internal wrapper is safe.
- `node --test frontend/src/shared/tokens/tokenContract.test.mjs`: **29
  passed, 0 failed** (26 pre-existing + 3 new Avatar-fix assertions).
- `npm run lint` (frontend, after a clean `rm -rf node_modules && npm ci` to
  clear a pre-existing, unrelated missing-native-binary issue —
  `@rollup/rollup-darwin-arm64` — confirmed via `git stash`/rebuild to
  reproduce identically without this task's changes, i.e. not caused by this
  fix): **PASS**, 0 errors/warnings.
- `npm run build` (`tsc -b && vite build`): **PASS**, 315 modules
  transformed, 0 TypeScript errors.
- Rebuilt the isolated `mc_phase1` frontend Docker image explicitly (the
  harness script `start-mongle-phase1.sh` only auto-builds db/backend, not
  frontend) and ran `tests/e2e/specs-mongle/01-shell.spec.ts` (iphone +
  desktop projects): **27 passed, 1 correctly-scoped desktop-only skip, 0
  failed** — this suite exercises `RoomItem`/`ChatHeader`/`DoranLanding`,
  the real existing Avatar consumers.
- Manual screenshot verification (4x device-scale) of `/wagle` after login:
  every existing Avatar instance (room-list initials, chat-header stacked
  avatar) renders as a fully circular avatar, visually unchanged from before
  the fix (none of them use `status`, so the only behavioral difference this
  fix could introduce — status-dot clipping — does not apply to them; their
  image/fallback circular clip is pixel-equivalent since `.avatarInner` is
  sized to exactly fill the old `.avatar` clipping box).
- Docker cleanup: `docker compose -p mc_phase1 ... down -v` confirmed clean
  after the E2E run and after the manual screenshot check.

## Completed / remaining

- Known Gaps: none for the fix itself. The *validation* of the fix's visual
  effect on a `status`-bearing Avatar was performed in the separate isolated
  A1 worktree (not this one), since that is currently the only real
  `status`-passing consumer in the codebase; this worktree's own consumers
  (`RoomItem`/`ChatHeader`/`DoranLanding`) don't exercise the status-dot path
  at all, only the "did we break the existing circular clip" path, which is
  confirmed clean.
- Not Measured / Estimated: none — every claim above is either a directly
  captured command result or a directly viewed screenshot.
- QA Status: self-check only (static tests + lint + build + target E2E +
  manual visual spot-check). Per PM direction this is a shared Foundation
  primitive change and requires independent QA before being folded into any
  governance/Foundation commit or before A1 integration proceeds.
- Drive Evidence: none.
- Coverage Map Review: see `agent-system/qa/COVERAGE_MAP.md` — this task adds
  3 static contract tests to an already-listed test file; no new test tier,
  journey, or environment status introduced.

## Risks and Human Gate

This touches a shared Foundation primitive (`Avatar`), which is normally
single-writer/high-risk per `agent-system/rules.md`. No other active task
currently claims `frontend/src/shared/components/Avatar/**` (grepped
`agent-system/active.md` and `agent-system/relay/current.md` before
starting; only this session's own relay entry claims it, declared before any
edit). PM explicitly directed this be split into its own task rather than
worked around in A1's isolated worktree.

## Next agent first action

Independent QA (a session other than this one) should verify: every
Avatar `size`/`status` combination renders as claimed, re-run the static
tests/lint/build/target E2E independently, and re-verify no existing
consumer regressed. Only after that PASS should this be folded into the
Wave-6.1-scoped governance commit (docs + Agent System records + this
Foundation fix — still not combined with A1 page code, per PM's explicit
separation of A1 code into its own commit later).

## Forbidden Scope

Backend/DB/migration files (none touched), A1 page-level files (none
touched — those live only in the separate isolated A1 worktree), any other
shared Foundation primitive beyond `Avatar` (none touched).

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md` entry for this Task ID
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: 3 new static assertions were added to an
  already-tracked test file (`tokenContract.test.mjs`); no new tier, journey,
  execution environment, or known-gap status changed.
- CLOSEOUT GATE: `PASS`

Closeout Gate PASS means only that the four documentation obligations above
are synchronized — it is not independent QA PASS, and does not authorize
folding this into a commit or into A1 integration on its own.
