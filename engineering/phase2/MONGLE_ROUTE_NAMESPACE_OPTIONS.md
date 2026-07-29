# MONGLE_ROUTE_NAMESPACE_OPTIONS

TASK ID: MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-DESIGN-001
Grounded in `MONGLE_CURRENT_ROUTE_AND_PERSISTENCE_INVENTORY.md`'s measured route table — no candidate below invents a route that isn't traceable to either the current IA or the previously-approved mockup screen inventory (`MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`).

## Scope reminder

Only `/naran/doran` and `/naran/family` literally contain the retired platform name. `/`, `/dashboard`, `/admin/*` do **not** contain `naran` and are not required to change for this migration's stated purpose — but Option D below considers changing them anyway, for a different reason (approved-mockup IA alignment), and is scored on that basis.

## Option A — Keep `/naran/...` (status quo, no route change)

```
/naran/doran
/naran/family
```

- **Product clarity**: Low — URL literally shows a retired internal codename to users (visible in address bar, bookmarks, shared links).
- **Brand alignment**: Fails — contradicts the entire purpose of `MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001`'s rebrand if the most user-visible surface (the URL bar) still says "naran".
- **Route stability**: Perfect (unchanged).
- **PWA compatibility**: N/A (no scope/start_url dependency on these two paths today).
- **Deep-link safety**: Perfect (nothing changes).
- **Back behavior**: N/A.
- **Existing migration**: Trivial — none needed.
- **Service expansion**: Poor — a future 3rd platform service would need to either join the `naran` prefix (compounding the problem) or break the existing pattern.
- **Internal separation**: Fails — `doran` is directly visible in `/naran/doran`.
- **Testability**: Perfect (unchanged).
- **Rollback**: N/A.
- **Complexity**: None.

**Verdict**: valid only as a "do nothing" baseline for comparison; not recommended given the task's own premise that `naran` should not remain in user-visible surfaces indefinitely.

## Option B — `/mongle/...` prefix

```
/mongle/doran
/mongle/family
```

- **Product clarity**: Medium — clearer than `naran`, but still exposes the internal `doran` messaging-domain name to users who have no reason to know it.
- **Brand alignment**: Good — explicit `mongle` namespace matches the platform's own internal identifier.
- **Route stability**: Good — a namespace prefix is a stable long-term pattern if more platform-level (non-service-specific) routes are added later.
- **PWA compatibility**: Compatible — a `scope: "/mongle/"` or `scope: "/"` both work; no conflict.
- **Deep-link safety**: Good, same mechanics as today.
- **Back behavior**: No new risk (same SPA navigation model).
- **Existing migration**: Same two files/consumers as Option C (see §Impacted files below) — equal migration cost.
- **Service expansion**: Good — new platform services can join under `/mongle/<service>` uniformly.
- **Internal separation**: **Fails the "doran이 노출되지 않아야 한다" goal implied by the task's own framing** — `doran` stays literally in the path.
- **Testability**: Good — same test-update shape as Option C.
- **Rollback**: Good — a single-segment prefix is easy to alias back if needed.
- **Complexity**: Low-Medium.

**Verdict**: better than A, but doesn't achieve full internal-name separation because it still spells out `doran`.

## Option C — Flat semantic routes, Doran name hidden (RECOMMENDED)

```
/wagle           (와글와글 — replaces /naran/doran; the room-list/conversation feature)
/family          (가족 — replaces /naran/family)
```

`/`, `/dashboard`, `/admin/*` are **left exactly as they are** — they don't contain `naran` and changing them isn't this migration's stated purpose.

- **Product clarity**: High — `/wagle` directly matches the user-visible feature name "와글와글" (romanized), `/family` is self-explanatory; neither requires the user to know any internal codename.
- **Brand alignment**: Good — consistent with the confirmed naming hierarchy (몽글=platform, 와글와글=messaging feature, doran=internal only) established in `MONGLE_NAMING_INVENTORY.md` §3.1.
- **Route stability**: Good — flat top-level routes are exactly the shape the approved mockup's screen inventory uses (`1b 홈`, `1c 포인트 잔치`, `1d 대화`, etc. are all flat, not prefixed) — this candidate doesn't invent a structure that a later mockup-driven IA change would have to unwind.
- **PWA compatibility**: Fully compatible — flat root-level paths work cleanly with any `scope` choice (`/` or narrower).
- **Deep-link safety**: Good, provided the compatibility-redirect design (see the Migration Plan doc) preserves query/hash.
- **Back behavior**: No new risk if implemented as `replace` navigation for the old→new alias (see Plan doc §11 there).
- **Existing migration**: **Smallest actual blast radius of any renaming option** — only 2 routes change; `/`, `/dashboard`, `/admin/*` and all their navigate()/Link call sites are untouched.
- **Service expansion**: Good — new top-level features (calendar `/calendar`, album `/album`, todo `/todo` — all currently `FUTURE_IMPLEMENTATION` per the screen/route/dock matrix) can join the same flat pattern without needing a namespace decision first.
- **Internal separation**: **Achieves the goal** — `doran` does not appear anywhere in the URL.
- **Testability**: Good — `specs-mongle/01-shell.spec.ts`'s `page.goto('/naran/doran')` calls become `page.goto('/wagle')`, mechanically equivalent effort to Option B.
- **Rollback**: Good — same single-path-segment simplicity as Option B, plus it doesn't entangle with a wider IA change (Option D) that would be much costlier to unwind.
- **Complexity**: Low — exactly 2 route-string changes plus the redirect/compat layer (§ Migration Plan doc).

**Verdict**: **Recommended.** Solves the actual, narrowly-scoped problem (retired platform name visible in URLs) with the least code churn, without pre-committing to a full mockup-driven IA redesign this task was never asked to do.

## Option D — Full IA rebuild aligned to the approved mockup (NOT recommended for this migration)

```
/            (1a 로그인)
/home        (1b 홈 — currently doesn't exist as a route at all, see MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md's SCREEN_EXISTS_ROUTE_MISSING finding for 1b)
/markpoint   (1c 포인트 잔치 — replaces /dashboard)
/wagle       (1d 대화 — replaces /naran/doran)
/me          (1f 나 — currently only an embedded widget, not a route)
/family      (replaces /naran/family)
/admin/*     (unchanged)
```

- **Product clarity**: Highest, if fully realized — matches the approved mockup's actual information architecture 1:1.
- **Brand alignment**: Best, in the long run.
- **Route stability**: **Poor for this migration specifically** — depends on screens (`/home`, `/me`) that don't exist as routes yet (per the prior task's matrix: 1b/1f are `SCREEN_EXISTS_ROUTE_MISSING`/embedded-widget-only), so "migrating" `/dashboard` → `/markpoint` today would just rename a route that still points at the same legacy `UserDashboard` component, while `/home` would need a *new* screen built first — conflating a route-rename with net-new screen development.
- **PWA compatibility**: Same as C once realized.
- **Deep-link safety**: Higher risk short-term — `/dashboard` is the single most Link/navigate-referenced route in the entire codebase (used as the post-login landing target, the brand-logo link target, and the `isLegacyDashboard` layout-branching condition) — renaming it multiplies this migration's blast radius severalfold for no benefit tied to the `naran` problem.
- **Back behavior**: Same mechanics, but more surface area to verify.
- **Existing migration**: **High** — touches `/dashboard` (heaviest-referenced route) in addition to the two `naran` routes.
- **Service expansion**: Best, long-term.
- **Internal separation**: Same as C for the Doran piece.
- **Testability**: Larger regression surface — every existing `/dashboard` E2E assertion (`toHaveURL(/dashboard/)`) would need updating too.
- **Rollback**: Harder — a `/dashboard`→`/markpoint` rename that gets rolled back mid-flight risks stranding users who bookmarked the interim URL.
- **Complexity**: High, and — critically — **entangles a route-namespace migration with unstarted screen development** (per the user's own most recent question in this conversation: mockup-driven screen rebuild "hasn't started yet"). Doing the IA rebuild as part of *this* migration would violate this task's own §4 scope boundary ("디자인 재구축이나 기능 구현으로 확장하지 않았는가").

**Verdict**: the right eventual direction, but **not this task's job**. Recommend treating Option D as the target of a later, separate Task once A1–A5 screen rebuild work (already gated behind its own PM decisions per `NEXT_A1_IMPLEMENTATION_PROMPT.md`) actually produces the `/home` and `/me` screens Option D depends on. Migrating `/naran/*` now (Option C) does not block or conflict with adopting D later — C's `/wagle` and `/family` paths are exactly what D would keep anyway.

## Comparison table

| Criterion | A (status quo) | B (`/mongle/*`) | C (flat semantic) | D (full IA rebuild) |
|---|---|---|---|---|
| Product clarity | Low | Medium | **High** | Highest (not achievable yet) |
| Brand alignment | Fails | Good | **Good** | Best (long-term) |
| Route stability | Perfect | Good | **Good** | Poor (depends on unbuilt screens) |
| PWA compatibility | N/A | Compatible | **Compatible** | Compatible (once realized) |
| Deep-link safety | Perfect | Good | **Good** | Higher risk (touches `/dashboard`) |
| Back behavior | N/A | No new risk | **No new risk** | More surface area |
| Existing migration cost | None | Low-Medium | **Lowest (2 routes only)** | High |
| Service expansion | Poor | Good | **Good** | Best |
| Internal separation (`doran` hidden) | Fails | **Fails** | **Achieves** | Achieves |
| Testability | Perfect | Good | **Good** | Larger regression surface |
| Rollback | N/A | Good | **Good** | Harder |
| Complexity | None | Low-Medium | **Low** | High, out of scope |

## Final recommendation

**Option C** (`/wagle`, `/family`, everything else unchanged). Rationale, in order of weight:

1. It is the only candidate that fully separates the internal `doran` name from anything user-visible, matching the confirmed naming hierarchy.
2. It has the smallest actual migration footprint — exactly the two routes that contain the problem this task exists to solve, nothing more.
3. It does not entangle this migration with the separate, not-yet-started, PM-gated mockup screen rebuild (Option D's real appeal) — keeping this task's scope honest to what was asked (§4 of this design task's own instructions).
4. It is forward-compatible with Option D — if/when `/home` and `/me` get built, they can simply join the same flat pattern C already establishes; nothing about C needs to be undone.

## Impacted files if Option C is adopted (measured, not estimated — for the Migration Plan doc to consume)

Route-string occurrences of `/naran/doran` and `/naran/family` requiring a corresponding `/wagle`/`/family` addition (not a destructive replace — see redirect design in the Storage/PWA doc and the Migration Plan):

- `frontend/src/App.tsx` — 2 `<Route path=...>` definitions
- `frontend/src/platform/shell/MongleAppShell.tsx` — 6 occurrences (desktop nav `to=`, mobile Dock `to=` ×2, `isDoranConversationMobile` check, `doranState` unavailable-banner check)
- `tests/e2e/specs-mongle/01-shell.spec.ts` — 3 `page.goto()` calls
- `backend/scripts/phase1_seed_synthetic.py` — 1 code comment (informational only, not a functional dependency)
- `tests/e2e/artifacts/mongle-route-alignment/{mobile,tablet,desktop}/03-naran-doran.png`, `04-naran-family.png` — screenshot filenames (cosmetic, not a functional dependency; can be renamed opportunistically during the implementation task, not migration-blocking)

No backend file, no DB row, no migration, no `doran` internal API path requires any change under Option C — the `/api/families/{family_id}/doran/...` backend contract is untouched by a frontend-route rename.
