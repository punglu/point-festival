# MONGLE_W6_2_A1_TOKEN_PRIMITIVE_GAPS

Task: MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001

## Token gaps

NONE. All colors, spacing, radii, and shadows used in the new/changed A1 code
(`Auth.module.css`'s new `.brandHeader`/`.brandMascot`/`.brandTitle`/
`.brandSubtitle`/`.profilePanel*`/`.playerCard` (new rules)/`.profile*`/
`.lockNotice`/`.footer*` rules) reference existing `--color-*`, `--space-*`,
`--radius-*`, `--shadow-*`, `--border-width-hairline` custom properties from
`frontend/src/styles/global.css`. No new custom property was declared and no
raw hex/px value was introduced for a design-decision color, spacing, radius,
or shadow.

## Primitive gaps

1. **BLOCKER (Foundation-owned, `CROSS_SESSION_SHARED_FILE_CHANGE_REQUIRED`).**
   `frontend/src/shared/components/Avatar/Avatar.module.css`'s `.avatar` rule
   sets `overflow: hidden` (needed to clip the image/fallback to a circle),
   but `.statusDot` is positioned at `right: 0; bottom: 0` on the same
   element — the overflow clip cuts the status dot into a quarter-circle
   "leaf" shape instead of a full circle with its intended white ring
   (confirmed visually at 3x device-scale crop). Grepped every existing
   consumer of `Avatar` (`ChatHeader`, `MessageBubble`, `RoomItem`,
   `DoranLanding`, and others) for a `status=` prop: **zero existing
   consumers pass it.** A1's `PlayerCard` is the first real caller to use
   `status`, which is why this defect has not been visible until now. This
   is a Foundation primitive bug, not an A1 page-level defect — per this
   task's file-ownership rules, `Avatar.module.css` was not edited directly.
   Left as-is; A1 uses the real primitive with the real bug present. Needs a
   Foundation-owner fix (likely: apply the circular clip via a nested
   wrapper or `clip-path` on the image only, not the whole `.avatar` box, so
   `.statusDot` can render unclipped).

2. **Non-blocking, informational.** No existing shared primitive provides a
   "job-title + numeric level" combined badge (`Lv.3 모험가`-style). The
   existing `Avatar`, `Button`, `AppIcon`, and outline icon set covered
   every other visual need for A1 without modification. Not a gap requiring
   action now — recorded only because the Visual Delta doc's Delta 3
   references it; no primitive change is being requested for this, since
   the underlying blocker is the missing API data field (see Visual Delta
   doc), not a missing component.

## Asset gaps

NONE remaining. One was found and resolved during this task, not left open:
the mascot illustration was initially implemented with the wrong existing
asset (`brand-icon.png`, does not match the approved screenshot) and was
corrected mid-task to the actual canonical master
(`family_platform_pin_logo_transparent_1024.png`, per
`MONGLE_W6_ASSET_POLICY_FREEZE.md`), copied byte-for-byte into
`frontend/src/assets/logos/family-platform-mascot.png` (SHA-256
`dd5c48b3e670636b7822a5893e213ce8e99fd667b82b4cb53026e344bea4f0b8`, identical
to the source evidence file). See Visual Delta doc, Delta 1.

One pre-existing observation, not a gap introduced or left by this task: the
copied master PNG is 1024×1024 and 484KB, uncompressed for web delivery. No
image-optimization tooling exists in this repo's frontend build today (plain
Vite asset import, no imagemin-equivalent step) — introducing one is outside
A1's scope. Flagged for a future, separately-scoped asset-pipeline task if
payload size becomes a concern.
