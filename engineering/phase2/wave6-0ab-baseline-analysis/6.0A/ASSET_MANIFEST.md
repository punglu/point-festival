# Asset Manifest

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 13). Full data: `asset_manifest.csv` (15 rows: 10 raster files under `uploads/` + 5 inline/non-file asset categories found by reading the HTML directly).

## Raster assets (`uploads/`)

| Asset | Role | Master candidate? | Key finding |
|---|---|---|---|
| `family_platform_pin_logo_transparent_1024.png` | Brand mascot (purple smiling pin/droplet + confetti) | Yes — the only pin-logo file actually referenced by `src=` in the HTML (6+ places) | Used at 6 different display sizes (96-210px) via `object-fit:contain`; no separate size variants exist |
| `brand_pin_logo_transparent.png` (2048²) | Higher-res sibling of the above | Candidate, but **not referenced anywhere in the HTML** | Confirmed via `grep -oE 'src="[^"]*"'` on the full document — zero hits for this filename |
| `family_platform_style_guide_v1.png` / `_preview.png` | Shared style-language reference (long-form raster, 1600×6773 / 1600×4400) | No | Not tied to any single screen; not referenced by the HTML; used only as corroborating context |
| `screen_login_approved.png`, `screen_family_home_approved.png`, `screen_point_festival_approved.png`, `screen_family_chat_approved.png`, `screen_admin_point_approved.png` | Primary visual truth for A1/A2/A3/A4/A5 respectively | No (final renders, not source masters) | See `TIER1_HTML_VISUAL_DELTA.md` for per-screen comparison |
| `19de6297-c168-45f4-be59-878a01bc0641.png` (1536×1024) | **Unknown** | No | UUID filename, not referenced anywhere in the HTML, no other file names or metadata identify it — classified `UNKNOWN`, flagged for a human visual check rather than guessed at |

## Non-file / inline assets (found by direct source inspection, no separate files)

- **Inline SVG icon set** (~9+ distinct 24×24 viewBox outline icons: Home, Point-festival/location-pin,
  Chat/message, Person, plus 6 AdminSidebar icons and several settings-row icons in EXTRA-01). These are
  literal `<svg>` markup embedded in the HTML, not separate asset files — several are byte-identical
  `path` data reused across A2/A3/A4's BottomDock. **Not exported as a standalone icon set/sprite/font
  anywhere in the approved source** — a future implementation would need to extract them from the HTML
  directly.
- **Emoji glyphs** (🔔💜🎉🧹📖👥💳📎📷🖼✨👍😊🍚🗓️🖼️📋 etc.) used throughout as informal
  icons/decoration. Flagged `implementation_suitability = 주의 필요 (EMOJI_PLACEHOLDER)` — cross-referenced
  with the independently re-verified finding in `TIER1_HTML_VISUAL_DELTA.md` that the **approved PNGs
  replace nearly all of these emoji with real flat icon illustrations that do not exist as standalone
  files anywhere in this folder** (`SOURCE_MISSING` for those specific icons — calendar+heart, photo-frame,
  clipboard-check, broom, open-book, two-people, credit-card, and the "blob mascot family" Home-hero
  illustration). This is the single most consequential asset finding of Phase A.
- **Fake iOS status bar** and **phone-mockup frame + home-indicator bar**: pure CSS/div constructions,
  present on every mobile screen, explicitly flagged `PRESENTATION_ARTIFACT` — these must **not** be
  carried into any real implementation (a real browser/PWA renders its own status bar / home indicator).
- **Photo-attachment placeholder texture** (A4, 3× 74×74px `repeating-linear-gradient` swatches labeled
  "사진 1/2/3"): an intentional low-fidelity placeholder, not a real photo asset — `LOW_RESOLUTION_PLACEHOLDER`,
  real attachment rendering is `PM_DECISION_REQUIRED`/deferred.

## Licensing

No licensing or attribution metadata was found for any raster asset (`NOT_VERIFIED` throughout the
`licensing` column of the CSV) — assets appear to be AI-generated or custom-made for this design pass,
but this is an inference, not a confirmed fact, and is reported as such.

Assets were only read, never copied, moved, re-encoded, or renamed. The only new files produced from
them are the Playwright render's own screenshots/crops under `/tmp/mongle-wave6-0ab/evidence/`, which
are fresh renders of the *HTML*, not copies of the approved raster assets themselves.
