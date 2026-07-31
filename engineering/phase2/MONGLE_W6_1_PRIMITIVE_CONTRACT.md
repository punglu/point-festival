# MONGLE_W6_1_PRIMITIVE_CONTRACT

Task: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001, §24. Final API/behavior contract for the 3 primitives
in this task's scope (§3 items 12-14), post-reconciliation.

## Avatar (`frontend/src/shared/components/Avatar`)

- **API**: `size?: 28 | 36 | 44 | 56 | 72 | 'xs' | 'sm' | 'md' | 'lg'` (widened union — every pre-existing
  numeric literal preserved verbatim; named sizes are new, additive, map to `34/44/60/78px` respectively).
- **Consumers preserved**: `DoranLanding.tsx`, `RoomItem.tsx`, `ChatHeader.tsx`, `MessageBubble.tsx` — all
  4 pass numeric literals today; **zero behavior change** for any of them (confirmed by the widened-union
  static test).
- **Accessibility**: `alt` remains a required prop; the no-image fallback renders `role="img" aria-label={alt}`
  unchanged; the online/offline/locked status dot keeps its screen-reader-only text span unchanged.
- **Not changed**: image-load-failure handling (the component has no `onError` re-fallback logic either
  before or after this task — that gap, if real, is pre-existing and out of this task's scope to fix,
  since it is not part of the token/primitive-wiring reconciliation this task performs), fallback-color
  logic (still `--color-brand-100`/`--color-brand-700`, unchanged), data model, per-screen usage pattern.

## IconButton (`frontend/src/shared/components/IconButton`)

- **Finding**: already fully compliant with §17(B)'s contract before this task touched anything — 44px
  min touch target via `var(--size-touch-min)`, mandatory `label` prop rendered as `aria-label`,
  `:focus-visible` outline, `:disabled` state, `type` defaults to `'button'`, icon alignment via a
  dedicated `.iconSlot` wrapper, pressed/active state (`:active { transform: scale(0.94) }`) preserved.
- **Change made**: **none functional.** Only benefits from the global `--color-brand-500`/`--radius-control`
  token value continuity (no value change to those specific tokens this task).
- **Consumers preserved**: `ChatHeader.tsx`, `ChatComposer.tsx` — 0 lines of either file touched.

## Button (`frontend/src/shared/components/Button`)

- **Starting state**: 0 real consumers anywhere in `frontend/src` (confirmed by fresh grep both before and
  after implementation — no new consumer was added by this task, matching §17(C)'s explicit instruction
  not to force a first consumer onto a screen).
- **API preserved**: `variant?: 'primary' | 'ghost' | 'dangerSm'` — same 3 keys, no new variant added, no
  variant renamed.
- **API addition**: `type` now defaults to `'button'` (previously unset, i.e. native default `'submit'`).
  Zero-risk since there are 0 consumers to break; documented as a safety-oriented default consistent with
  `IconButton`'s existing convention.
- **Explicitly not added**: a `loading` state/prop — §17(C) only allows this "if existing API supports
  it," and it did not.
- **Styling reconciled to canonical tokens**: `background`/`color` now reference `--color-brand-600`
  (primary), `--color-ink-700`/`--color-surface-soft`/`--color-brand-50` (ghost), `--color-danger` (dangerSm)
  instead of the legacy `--accent`/`--input-bg`/`--muted`/`--text` set and hardcoded hex literals. Added
  `:focus-visible` ring (`--color-brand-500`), `:disabled` state, `min-height: var(--size-touch-min)` on
  the base `.btn` (touch-target compliance for the `primary` variant; `ghost`/`dangerSm` explicitly opt out
  via `min-height: auto` since they are historically small/dense controls, not primary touch targets —
  this mirrors the existing size differentiation already present in the original CSS, not a new decision).
  `dangerSm`'s light-red background literal (`#fee2e2`) was intentionally **not** tokenized — no canonical
  danger-tint token exists yet, and inventing one was judged out of scope (avoiding Hard Stop #22's
  "arbitrary token policy decision").
- **Not done**: consumer migration onto any A3/A5 screen (explicitly forbidden by §17(C); remains a future
  task's first-real-consumer event).

## Cross-cutting accessibility/touch-target confirmation

| Primitive | Touch target | Accessible name | Focus-visible | Disabled state |
|---|---|---|---|---|
| Avatar | n/a (not interactive) | `alt` required | n/a | n/a |
| IconButton | 44px (pre-existing) | `label` → `aria-label` required | Yes (pre-existing) | Yes (pre-existing) |
| Button | 44px (`primary`, new this task) | inherits native `<button>` semantics + `children` text | Yes (new this task) | Yes (new this task) |

## Verdict

**PRIMITIVE_CONTRACT_PRESERVED.** Avatar's and IconButton's existing consumer APIs are unbroken (Hard
Stop #14 does not fire). Button's 0-consumer status means its reconciliation carries zero regression risk
by construction, and no new variant, no consumer migration, and no `loading` state were force-added.
