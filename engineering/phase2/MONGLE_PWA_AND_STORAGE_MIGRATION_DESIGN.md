# MONGLE_PWA_AND_STORAGE_MIGRATION_DESIGN

TASK ID: MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-DESIGN-001
**READ-ONLY design document.** No manifest/SW/storage code touched. All "current state" claims trace to `MONGLE_CURRENT_ROUTE_AND_PERSISTENCE_INVENTORY.md` §5–6.

## Part 1 — PWA

### 1.1 Current state recap (measured, §6 of the inventory doc)

Manifest-only. No Service Worker, no offline capability, no `id`/`scope`, `start_url: "/"`, root-path hosting, no `vite-plugin-pwa`/workbox dependency, no `mongle.life`/`PUBLIC_APP_URL` wiring anywhere in code. Cannot verify an existing real-user install base from this session (no analytics access) — treated as **NOT VERIFIED**, not assumed zero and not assumed nonzero.

### 1.2 Scope separation (per task §12)

| Bucket | Items | Rationale |
|---|---|---|
| **Route Migration required scope** | `manifest.json`'s `start_url` (only if it needs to change to reflect a new default landing route — see 1.3), any `<Link>`/`navigate()` targets that currently hardcode `/naran/*` | These are the only PWA-adjacent items that would actually break if `/naran/*` routes changed and nothing else were touched |
| **PWA Foundation (separate future task)** | Adding `id`, `scope`, a real Service Worker, precache, offline fallback, `shortcuts`, install-prompt UX, update-flow UI | None of this exists today; building it is net-new feature work, not a migration of something that already exists. Should not be smuggled into a route-rename task. |
| **Post-Wave** | Push notifications, background sync, share target, protocol handlers | Explicitly named as out-of-scope by the task's own §12 instruction ("Push, WebSocket, background sync를 Route Migration 구현에 끼워 넣지 않는다") |
| **Decision-only in this design (no implementation)** | Whether `start_url` should point at `/` (current) vs a post-login route, whether `scope` should be added at all before a Service Worker exists | Recorded as PM Gate items (§ this doc's Part 3 and the main design report) |

### 1.3 `manifest.json` fields — current vs. recommended

| Field | Current | If Option C route rename lands | Recommendation |
|---|---|---|---|
| `start_url` | `/` | No forced change — `/` still resolves to `AuthPage`, which itself redirects to `/dashboard`/`/admin` when already logged in. Renaming `/naran/doran`→`/wagle` does not require touching `start_url`. | **Keep `/`.** Changing it is a PWA-Foundation-scope decision (e.g. "should an installed app skip the login screen"), not a route-migration necessity. |
| `id` | Absent | Unaffected by the route rename | Adding an explicit `id` (typically `/` or a stable opaque string) is recommended **before** any future Origin change (e.g. adopting `www.mongle.life`), because `id` is what lets a browser recognize "this is the same installed app" across a URL/Origin change. Since no Service Worker or real install flow exists yet, this is a **PWA Foundation** item, not blocking this migration. |
| `scope` | Absent (defaults to `/`) | Unaffected — both `/naran/*` and `/wagle`+`/family` fall under the default `/` scope either way | No change needed for the route rename itself. If a Service Worker is added later, an explicit `scope: "/"` should be set at that time for clarity, not as part of this migration. |

**Conclusion**: **the route rename (Option C) requires zero PWA manifest changes.** The manifest fields most people would assume need touching (`start_url`, `scope`) do not, because neither depends on the specific `/naran/*` path strings — they're already scoped to the whole origin.

### 1.4 Origin change consideration (`www.mongle.life`)

Not implemented anywhere in code today (confirmed absent from `CORS_ORIGINS`, no config references it). If/when a real Origin change happens:
- Any existing installed PWA (if one exists — NOT VERIFIED) tied to the *current* origin will not automatically follow to a new origin; this is a browser-level limitation, not something this app's code can paper over without a genuine `id`-based migration strategy or a user-facing "reinstall" prompt.
- This is **entirely independent** of the `/naran/*` → `/wagle`+`/family` path rename — changing path segments within the same origin does not, by itself, invalidate an install.
- Recommendation: treat "final domain adoption" as its own future PWA Foundation task, explicitly decoupled from this route migration (per the task's own §16 item #15).

## Part 2 — Persisted storage migration (`naran.activeFamily.${accountId}`)

### 2.1 Option comparison

| Option | Description | Data loss risk | Complexity | Rollback | Multi-tab | Multi-account | Testability | Removable later | Permanent tech debt |
|---|---|---|---|---|---|---|---|---|---|
| **A — Keep the key forever** | Do not rename `naran.activeFamily.*` at all; only the two routes change (Option C), storage is untouched. | **None.** | **None.** | Trivial (nothing to roll back). | No change from today. | No change from today. | No new tests needed. | No — it's permanent by definition. | The word "naran" survives indefinitely in a code identifier, contradicting the rename's own goal, but with zero user-facing risk. |
| **B — New key preferred, legacy read as fallback (no write-back)** | `load()` tries the new key name first; if absent, reads the legacy key (read-only, never deletes it) and uses that value for the current session only. | **None** — old data is read, never destroyed. | Low — one extra conditional read. | Trivial — removing the fallback branch reverts to new-key-only behavior. | Same characteristics as today (last-write-wins on whichever key is actually written). | Both keys are `accountId`-namespaced already; no new collision risk. | Easy — deterministic given key presence/absence. | New key can eventually become the only one read; legacy key is **never actively removed** under this option, so disk clutter (a handful of bytes per account) persists forever unless a separate cleanup step is added. | Moderate — the fallback-read branch itself becomes permanent unless explicitly retired later. |
| **C — Copy-forward on first access, legacy retained for a window (RECOMMENDED)** | On `load()`, if the new key is absent and the legacy key has a valid value, write that value to the new key (one-time copy), then proceed exactly like today. Legacy key is left in place (not deleted yet) for a PM-defined window, then a later cleanup task removes it. | **None** — copy-forward preserves the value; nothing is deleted until the separate later cleanup step, which only fires after the window. | Low-Medium — one extra read + conditional write, all inside the already-existing `load()` function. | Straightforward — reverting means removing the copy-forward branch; no user data is destroyed by rollback since the legacy key was never deleted. | No new risk — the copy-forward write happens inside the same `load()` call that already writes `localStorage` today. | Same per-account namespacing carries over unchanged to the new key name. | Testable deterministically: "legacy only" → expect copy-forward + correct behavior; "new only" → expect normal behavior; "both, differing values" → new key wins (already the more recent one). | **Yes** — cleanly removable after the PM-defined window, as its own small follow-up task. | Lowest of the realistic options — the migration logic has a defined expiry. |
| **D — Dual-write, remove old key after a window** | Write both old and new keys simultaneously for a transition period; read only the new key. After the window, stop writing the old key and optionally delete it. | **None**, but slightly more invasive than C (touches the write path on every `selectFamily()`/`load()` call, not just a one-time copy). | Medium — two write sites need updating instead of one copy-forward branch. | Same as C, but reverting must also stop the dual-write, not just a read fallback. | No new risk beyond C. | Same as C. | Slightly more test surface than C (must verify both keys stay in sync). | Yes, same as C. | Similar to C, marginally higher due to the extra write site. |
| **E — Rename the key immediately, no compatibility** | Just change the key name; old data is orphaned. | **Real, user-visible** — every multi-Family account loses their remembered selection on their next `load()` (see inventory doc §5 item 11). Single-Family accounts are unaffected (auto-select still works). | Lowest code complexity, but **not recommended per the task's own explicit instruction** ("Option E는 사용자 상태 손실 가능성이 있으므로 특별한 근거 없이 권장하지 않는다"). | N/A — there's nothing to roll back to once data is orphaned; the only "rollback" is asking affected users to re-select their Family once. | No new risk. | No new risk. | Simple to test, but tests would have to accept the regression as "expected," which is itself a signal this option is wrong. | N/A (nothing left to remove). | None technically, but a real (if minor and one-time) user-facing regression. |

### 2.2 Recommendation

**Option C.** It achieves the eventual goal (retire the `naran`-named key) with **zero data-loss risk**, the smallest code footprint of the zero-risk options (B/C/D), and — unlike B — has a defined end state (the legacy key actually gets removed eventually, rather than the fallback-read branch living forever). D is a reasonable second choice if the team specifically wants both keys to always be in sync during the transition window (e.g. to support rolling back the *route* migration independently of the *storage* migration), but for a single-key, single-purpose value like a Family-ID selection, that extra synchronization complexity isn't justified.

### 2.3 What "new key name" should be — explicitly a PM Decision Gate item

This design does **not** pick a literal replacement string (e.g. `mongle.activeFamily.${accountId}`) — that decision belongs to the PM Decision Gate (see main design report §16 item 5), consistent with this task's instruction not to confirm implementation details prematurely. The migration mechanism (Option C above) works identically regardless of what the new key's literal name ends up being.

## Part 3 — Old install compatibility

Since no Service Worker or real install-tracking exists today (Part 1), "old install compatibility" for *this* migration reduces to: **does an already-bookmarked or already-installed instance still work after the route rename?**

- A same-origin path rename (Option C: `/naran/doran`→`/wagle`) does **not** invalidate an existing "Add to Home Screen" shortcut, because such shortcuts on most platforms simply reopen the browser at the `start_url` (`/`), not at whatever path the user happened to be on when they installed it. The Family/Doran routes are not the PWA entry point.
- A bookmarked deep-link to the *old* path (`/naran/doran`) is the actual compatibility concern — addressed by the redirect/alias design in the Migration Plan document (`MONGLE_ROUTE_NAMESPACE_MIGRATION_PLAN.md`), not by anything PWA-specific.
- If a real Service Worker is added later (PWA Foundation, out of this scope) with precached navigation routes, *that* future task would need its own cache-invalidation plan for any route it had precached — not relevant today since no such cache exists.

## Part 4 — Rollback (PWA/storage-specific slice; full rollback scenario list lives in the Migration Plan doc)

What must be preserved to roll back cleanly:
- The legacy `naran.activeFamily.*` key itself — Option C never deletes it during the transition window, so reverting the route/storage code changes leaves user data fully intact.
- `manifest.json`'s current fields — since Part 1 concludes **no manifest change is required** for the route rename, there is nothing PWA-side to roll back in the first place.
- No Service Worker exists to go "stale" — this specific rollback failure mode (Service Worker serving a cached old route) is **not applicable** today; it becomes relevant only once a PWA Foundation task adds one, and that task would own its own rollback design at that time.
