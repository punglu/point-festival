# MONGLE_W6_ASSET_POLICY_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 17. Merges `6.0A/ASSET_MANIFEST.md` (mobile approved
source) with this session's direct read of the tablet HTML (4 zone-mapped screens) and
`docs/temp/design_tablet/design-system/*` asset-slot contracts.

| Asset | Role | Classification | Basis |
|---|---|---|---|
| `family_platform_pin_logo_transparent_1024.png` | Brand mascot, in-use master | `CANONICAL_MASTER` | SHA-confirmed identical across `screen_renew` and `docs/temp/design_tablet/uploads/`; also directly `src=`-referenced in A2 hero, A4 room-list header in the tablet source this session (6+ mobile placements per 6.0A, now confirmed reused at tablet scale too) |
| `brand_pin_logo_transparent.png` (2048²) | Higher-res sibling | `DELIVERY_ASSET`, not referenced by `src=` in either mobile or tablet HTML | Unchanged from 6.0A; grep for the filename in the tablet HTML also returns 0 hits (checked this session) |
| `family_platform_style_guide_v1.png` / `_preview.png` | Style-language reference | `PRESENTATION_ARTIFACT` (context only, not a UI asset) | Unchanged from 6.0A classification |
| `screen_login_approved.png`, `..._family_home_approved.png`, `..._point_festival_approved.png`, `..._family_chat_approved.png`, `..._admin_point_approved.png` | Tier 1M primary visual truth for A1/A2/A3/A4/A5 | `CANONICAL_MASTER` (visual reference, not exportable UI asset) | SHA-confirmed identical to `screen_renew`; directly viewable in this environment now (upgrade from 6.0A's Mac-only access) |
| `19de6297-c168-45f4-be59-878a01bc0641.png` | Unknown, 1536×1024 | `SOURCE_MISSING` classification held over as `UNKNOWN` — **not resolved this session**, not opened/viewed as part of this read-only Gate | Unchanged from 6.0A; flagged for a human visual check, still outstanding |
| Home-hero "blob mascot family" illustration (D5, approved PNG only) | A2 hero illustration | `SOURCE_MISSING` | 6.0A finding, **re-confirmed not present** in `docs/temp/design_tablet/uploads/` either (10/10 files accounted for, none match this description) — the tablet HTML's own A2 hero (this session's read) uses the **same pin-logo asset**, not this illustration, and a plain purple gradient card, not real icon art. **The tablet delivery does not solve D5** — it independently confirms the illustration asset still doesn't exist anywhere in this environment. |
| Real flat icons (service tiles, mission rows) — approved PNG only (D5) | A2 service tiles, A3 mission icons | `SOURCE_MISSING`, re-confirmed | The tablet HTML's own A2 service-tile grid and A3 mission list (both read in full this session) use **emoji** (📖🗓️🖼️📋🏠🍽️🏥🚗📚, 🧹📖👥💳 etc.), not real icon files — **the tablet delivery uses the same emoji-placeholder pattern 6.0A already flagged for the mobile source**, it does not introduce or resolve the missing real-icon-asset problem. This directly updates `D5`: sourcing real assets remains necessary regardless of which HTML (mobile or tablet) is built from. |
| Tablet-specific new SVG icon set (nav-rail icons: 홈/잔치/대화/나/설정, admin-rail icons) | Nav iconography, both landscape rails | `APPROVED_INLINE_SVG` | New this session's read — these are genuine, real (non-emoji) 24×24 outline SVG icons, inline in the tablet HTML, single-stroke style (`stroke-width:1.8`), consistent across A2/A3/A4/A5 nav rails and BottomDock. **This is new, usable icon evidence the mobile source's own `6.0A/ASSET_MANIFEST.md` already partially covered** ("~9+ distinct 24×24 viewBox outline icons... several byte-identical `path` data reused across A2/A3/A4's BottomDock") — the tablet source reuses the **same path data**, confirmed by visual/structural match (Home icon path `M4 10.6 12 4.2l8...` appears identical across every screen read this session) |
| Fake status-bar-look row (A2 landscape, time/battery/signal glyphs) | Chrome-adjacent decoration | `PRESENTATION_ARTIFACT` candidate — **not fully resolved this session** | Flagged in `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` item 15; needs the same scrutiny 6.0A gave the mobile mockup's fake status bar before Wave 6.1 |
| Phone-mockup frame / home-indicator bar | Mobile-only chrome | `FORBIDDEN_FINAL_ASSET`, unchanged | 6.0A's `PRESENTATION_ARTIFACT` finding stands; **the tablet screens read this session (A2-A5) do not reproduce a phone-frame chrome** — each tablet canvas is presented as a plain rounded-rect device mock (`border-radius:28px`, drop shadow), not a phone-shaped frame, so this specific artifact is mobile-only and does not need to be separately forbidden for tablet |
| Photo-attachment placeholder texture (A4) | Chat photo placeholder | `LOW_RESOLUTION_PLACEHOLDER`, unchanged | Not re-checked against tablet A4 this session (tablet A4's read did not include a photo-attachment zone) — `NOT_VERIFIED` for tablet specifically |

## Policy re-confirmed (Section 17 required list, all checked this session)

- Fake status bar: **not fully clear** — flagged above, not blanket-forbidden without resolving the A2
  landscape ambiguity first.
- Fake home indicator / phone frame: confirmed absent from the tablet source's own presentation, no
  action needed for tablet; remains forbidden for any mobile-frame chrome carried into product UI.
- Mock outer shadow: the tablet source's own `0 30px 70px rgba(40,20,90,.20)` drop shadow around each
  device mock is the **presentation-artifact shadow**, distinct from the `--shadow-card`/`--shadow-modal`
  UI-token shadows already frozen in `MONGLE_W6_DESIGN_TOKEN_FREEZE.md` — do not conflate the two when
  implementing; the device-mock shadow is not a product token.
- Functional emoji: **actively still in use** in both mobile and tablet sources for service tiles/mission
  icons (D5) — the prohibition on shipping emoji as final icons stands; this freeze does not relax it.
- Missing icons/illustrations: not fabricated by this task, per instruction — `ASSET_BLOCKED` stands for
  A2's hero illustration and A2/A3's flat icon set until sourced.
- 1024/2048 logo relationship: confirmed unchanged (1024px = in-use master, 2048px = unreferenced
  sibling, both SHA-identical to the 6.0A baseline).
- New tablet assets: only the inline SVG nav-icon set is new *and* real (not emoji, not a missing
  reference) — classified `APPROVED_INLINE_SVG`, safe to extract into a real icon set/sprite for Wave 6.1
  nav-rail and BottomDock work.

## D5 status update

**Not resolved.** The tablet delivery, despite being a much larger and more complete design document than
the original 10-screen mobile source, uses the **identical workaround** (emoji placeholders, no real
icon/illustration files) for exactly the same two screens (A2 hero + service tiles, A3 mission icons) that
6.0A already flagged. This is meaningful new evidence that the missing-asset problem is a genuine sourcing
gap in the underlying design process, not an artifact of one particular HTML export being incomplete.

## Verdict for this Gate

**ASSET_POLICY_CLASSIFIED**, D5 remains `ASSET_BLOCKED` for A2/A3 icon-level visual work (re-confirmed,
not newly resolved), 1 new usable asset category found (inline nav-icon SVG set), 2 items left
`NOT_VERIFIED` (fake-status-bar-row ambiguity, A4 photo-placeholder-in-tablet).
