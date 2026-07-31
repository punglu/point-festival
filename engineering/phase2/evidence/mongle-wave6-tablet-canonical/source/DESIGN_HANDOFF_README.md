# Handoff: 가족 플랫폼 (Family Platform) — Full Screen Set

## Overview
Complete mobile + admin UI for a family-management platform: missions/points ("포인트 잔치" gamification), family chat, calendar, album, to-dos, community board, and a parent/admin console (mission management, approvals, point policy, user management). 71 screens covering onboarding, core flows, settings, admin, and edge/empty states.

## About the Design Files
The files in `screens/` are **design references built in HTML** — static, high-fidelity prototypes showing the intended look and layout, not production code to copy directly. The task is to **recreate these designs in the target codebase's existing environment** (React Native / SwiftUI / Flutter / web React — whichever this project already uses, or the best-fit choice if none exists yet), using that environment's own component and state patterns. Do not embed or `<iframe>` these HTML files into the product.

Two HTML files are included and are equivalent in every way except styling:
- `가족 플랫폼 화면 재현.dc.html` — literal hex/px values inline (the original approved mockup).
- `가족 플랫폼 화면 재현-tokenized.html` — identical DOM/text/layout, but color and radius values are written as `var(--token-name)` referencing `design-system/canonical-tokens.css`. **Use the tokenized file + `canonical-tokens.css`/`canonical-tokens.json` as your source of truth for design values** — it's the same UI with the values already named for you.

## Fidelity
**High-fidelity (hifi)**. Colors, typography, spacing, radius, and shadows are final and documented in `design-system/canonical-tokens.css` / `.json`. Recreate pixel-perfectly using your codebase's own component library, substituting the documented token values.

## Design Tokens — Quick Reference
Full detail in `design-system/canonical-tokens.css`, `.json`, and `TOKEN_CLASSIFICATION.md`. Summary:

**Color**
- Brand: `#5A35DF` (primary/600), `#6B46F2` (secondary/500)
- Canvas: `#F7F6FC` — Surface: `#FFFFFF` — Sunken surface: `#FBFAFE`
- Text: primary `#17103A`, secondary `#4A3F72`, tertiary `#8A83A8`, disabled `#A8A5B6`, faint `#C7C3D6`
- Border: subtle `#F0EEF7`, default `#EAE7F5`, input `#E6E2F4`
- Status: success `#1F9D62`/`#DCF4E8`, warning `#B4791A`/`#FDEFCF`, danger `#EF4665`/`#FBE0E6`, reward `#F1983A`/`#FFC93C`
- Tinted purple surfaces: `#F1EDFC`, `#F4F2FD`, `#EEE8FF`, `#E7DFFB`, `#DCD0F8`

**Radius**: pill `999px`, phone-frame `44px`, hero card `24px`, list-group card `18px`, summary/stat card `20px`, input `14px`

**Spacing scale (px)**: 4, 6, 8, 10, 12, 14, 16, 18, 22, 24 (organic, not a strict 8pt grid)

**Typography**: Noto Sans KR, weights 400/500/700/900. Roles: caption 11 · small 12 · body-sm 13 · body 14 · body-lg 15 · title-sm 17 · title 19 · title-lg 21 · display-sm 28 · display 36.

**Avatar scale**: xs 34px, sm 44px, md 60px, lg 78px (only these four sizes are canonical — don't invent intermediate sizes).

**Motion**: **not defined** in the source (static mockups). Do not invent transition timing from this handoff — get real interaction specs from product/design before implementing animation.

**Known non-uniformities (intentional, not bugs)**: card radius has two families (18px list-group vs 20px stat/summary cards) — pick per component type, see `COMPONENT_STYLE_CONTRACT.md`. Chat bubble "own" color (`#6944EF`) is deliberately distinct from brand-600.

## Responsive — Tablet
`screens/가족 플랫폼 화면 재현-tablet.dc.html` covers the **15 priority screens** at two tablet breakpoints. These are **layout redesigns, not scaled-up phone screens** — density is the point: the extra space carries more real content per screen, not bigger type.

**Breakpoints**
- Landscape **1024×700** — master–detail. A persistent left rail replaces the bottom dock (84px icon rail for member screens, 80px for admin), and content splits into 2–3 columns: list + detail, or content + context sidebar.
- Portrait **768×1024** — single column with expanded grids. The bottom dock stays; cards go 2-up or 3-up, calendar day cells grow to 36px, photo grids go 6-across.

**Density rules applied (carry these into implementation)**
- Every screen keeps the full chrome the phone version has: status bar, back arrow + title + subtitle count line, filter chip row, and a footer info card. Don't drop these when adapting other screens.
- Subtitle lines carry real counts (“구성원 4명 · 초대 대기 1명 · 관리자 2명”) rather than generic descriptions.
- Landscape gains a **context sidebar** carrying secondary data that the phone screen hides behind navigation (권한 관리, 교환 내역, 인사이트, 아이별 현황).
- Admin screens become **real data tables** at tablet width (5-column grid rows, sticky header row, status pills, pagination footer) instead of the phone's stacked list rows.
- Type scale is *unchanged* from phone — 11–14px body, 20–24px titles. Tablet gets more content, not larger text.

**Screens covered**: 1b 홈, 1c 포인트 잔치, 1d 대화, 1g 가족 일정, 1h 앨범, 1i 할 일, 1k 미션 상세, 1n 알림, 1q 구성원 관리, 2j 리워드샵, 1e 포인트 관리, 2i 부모 대시보드, 2x 미션 통계, 3c 가족 게시판, 2q 가족 규칙.

The remaining 56 screens have no tablet variant yet — apply the rules above when you reach them, using the closest covered screen as the pattern (list screen → 1h/1n, form → 1k, admin table → 1e, dashboard → 2i).

## Screens (71 total)
Full descriptions of layout/components/copy are in the HTML itself — every screen is inline-styled and self-contained, so **read the HTML for a screen directly** rather than requesting a re-description; the markup is the spec. Screen IDs below match `id="..."` attributes in the HTML for quick lookup.

**Onboarding / Auth**: 1a login+profile picker, 1a-1 plain ID/password login, 1j PIN entry, 1j-1 PIN lockout, 1r create-family onboarding, 1u change PIN, 2s first-time PIN setup, 2d forgot password (2-step), 2w accept family invite, 3i cancel invite

**Core app**: 1b home, 1c points/missions ("포인트 잔치"), 1d family chat, 1f my profile, 1g family calendar, 1h album, 1i to-dos, 1k mission detail + proof submission, 1l redeem points, 1n notifications list, 1o add calendar event, 1p photo viewer, 1q family members management, 1s mission rejected, 1t chat room settings, 1w album search results, 2j reward shop, 2u event detail, 2v album upload progress, 2y album sharing settings, 2z edit profile, 3a calendar sync/share

**Community board**: 3c board list, 3d comments, 3e trending posts

**Search / Widgets**: 3j global search, 3k widget gallery, 3l shortcut editor

**Settings**: 2k settings index, 2n notification preferences, 3f language, 3g theme (light/dark/font-size — UI only, not wired), 3h delete account

**Admin console**: 1e point ledger, 1m approval queue, 1v family rules/point policy, 1x child weekly report, 1z create-mission modal, 2a user detail, 2e mission list management, 2f invite approval, 2i parent dashboard, 2l create-mission full page, 2m edit-mission form, 2o point policy editor, 2p invite list, 2q family rules info, 2r activity log, 2t send announcement, 2x mission stats dashboard, 3b stats filter modal

**Utility / states**: 1y error & empty states (network error, no notifications, no search results), 2b chat media gallery, 2c level-up celebration modal, 2g chat reply/long-press menu, 2h redeem confirmation dialog

Six additional screens (`1z0`–`1z5`) exist in the HTML but are hidden (`display:none`) — they were superseded drafts (early versions of 2a/2c/2d/2e). Safe to ignore; not canonical.

## Interactions & Behavior
All screens are **static mockups** — no live interaction, animation, or state transition is implemented. Buttons/toggles/tabs show only their visual states (active/inactive), not wired behavior. Treat every clickable element's *label and position* as the interaction spec; the actual behavior (navigation target, API call, validation) must be inferred from context and confirmed with product before building, since it isn't encoded in the HTML.

Known interactive-state conventions used consistently across screens (recreate these):
- **Toggle switch**: track `justify-content: flex-end` (on, bg brand-600) / `flex-start` (off, bg `#E3E1EA`) + `align-items:center` on the track (required for the knob to sit vertically centered).
- **Input focus**: border `1.5px solid #5A35DF` + ring `0 0 0 4px rgba(90,53,223,.10)`.
- **Input error**: NOT_DEFINED_IN_APPROVED_SOURCE — only helper-text color changes to danger; the border itself was never shown changing color. Don't invent a red-border state without checking with design first.
- **Status badges**: pill shape, tone-mapped per `TOKEN_CLASSIFICATION.md` (success/warning/danger/neutral).

## Assets
- `uploads/family_platform_pin_logo_transparent_1024.png` — brand mascot/pin logo, used as the app icon and empty-state imagery throughout. Bring your own copy of this asset into the target codebase (do not hot-link the design tool's uploads path).
- All avatar photos, album photos, and chat-attached photos are **placeholders** (diagonal gradient pattern blocks or initials-on-gradient), not real assets — swap for a real image-loading component with the slot contract below.

### Photo slot contract (from `COMPONENT_STYLE_CONTRACT.md`)
- Avatar: circle, `object-fit: cover`, center-crop, fallback = initials on brand gradient.
- Album grid tile: 1:1, radius 12px, `object-fit: cover`.
- Album card thumbnail: 4:3, radius 12px, `object-fit: cover`.
- Album hero highlight: 16:9, radius 24px, `object-fit: cover`.
- Loading/error states for image fetch: **not defined in source** — design your own per your app's existing patterns.

## State Management
Not applicable to this handoff — screens are static; there is no state to port. Infer required state (form fields, toggle values, list data, pagination) from each screen's rendered content when implementing.

## Design Tokens — Files
- `design-system/canonical-tokens.css` — `:root` custom properties + example component classes (buttons, cards, toggle, badge, chat bubble, avatar scale, asset slots).
- `design-system/canonical-tokens.json` — same values, structured with meaning/source-screens/confidence per token — useful for generating a typed tokens file (TS/Swift/Kotlin) programmatically.
- `design-system/APPROVED_VISUAL_STYLE_GUIDE.html` — open directly in a browser for a visual swatch/type/component reference.
- `design-system/TOKEN_CLASSIFICATION.md` — which values are global vs. component-scoped vs. screen-local vs. one-off (don't tokenize everything — this file tells you what's intentionally NOT a shared token).
- `design-system/COMPONENT_STYLE_CONTRACT.md` — structural + state contract per repeating component (button, card, input, dock, avatar, badge, modal/sheet, list row, chat bubble, toggle).
- `design-system/SCREEN_LOCAL_TOKEN_REGISTER.md` — values that are intentionally scoped to one screen/feature (e.g. the points-progress gradient is Point-Festival-only, not global).
- `design-system/ONE_OFF_LITERAL_REGISTER.md` — values used exactly once; leave these as literals, don't invent tokens for them.
- `design-system/SOURCE_SCREEN_INVENTORY.md` — the full 43-entry screen list from the original extraction pass (this handoff's 71-screen set is a superset — see Screens section above for the complete current list).
- `design-system/AMBIGUITY_AND_PM_REVIEW.md` / `FINAL_REPORT.md` — record of design decisions already resolved by PM; final status **APPROVED_VISUAL_DESIGN_SYSTEM_READY**.

## Files
```
design_handoff_family_platform/
├── README.md                                          (this file)
├── screens/
│   ├── 가족 플랫폼 화면 재현.dc.html                    (all 71 screens, literal values)
│   ├── 가족 플랫폼 화면 재현-tokenized.html              (same screens, var(--token) values — prefer this one)
│   └── 가족 플랫폼 화면 재현-tablet.dc.html              (15 priority screens × landscape + portrait tablet)
└── design-system/
    ├── APPROVED_VISUAL_STYLE_GUIDE.html
    ├── canonical-tokens.css
    ├── canonical-tokens.json
    ├── TOKEN_CLASSIFICATION.md
    ├── COMPONENT_STYLE_CONTRACT.md
    ├── SCREEN_LOCAL_TOKEN_REGISTER.md
    ├── ONE_OFF_LITERAL_REGISTER.md
    ├── SOURCE_SCREEN_INVENTORY.md
    ├── AMBIGUITY_AND_PM_REVIEW.md
    └── FINAL_REPORT.md
```

## For Claude Code — quick start
1. Open `screens/가족 플랫폼 화면 재현-tokenized.html` in a browser and `design-system/canonical-tokens.css` side by side — every color/radius in the screens maps to a named variable there.
2. Read `TOKEN_CLASSIFICATION.md` first — it tells you what to actually turn into shared design-system primitives in your codebase vs. what to leave as one-off literals per screen.
3. Read `COMPONENT_STYLE_CONTRACT.md` for the 8 repeating components (button, card [two radius families], input, bottom dock, avatar [xs/sm/md/lg only], badge, modal/sheet, list row, chat bubble [own/other/system], toggle) — build these once as shared components, then compose all 71 screens from them plus screen-specific layout.
4. For each screen, open its `<div id="...">` block directly in the HTML — it's the full spec (exact copy, layout, states shown). No separate per-screen written spec exists beyond this README's summary; the HTML *is* the detailed spec.
5. Do not implement motion/transitions from guesswork — flagged as not defined in source; get real specs before animating.
