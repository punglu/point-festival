# Wave 6 1e 관리자 포인트 관리 — Canonical Measurement

## Canonical metadata

| Field | Value | Status |
|---|---|---|
| Screen | A5 / `1e` / 관리자 포인트 관리 | MEASURED |
| Role / form factor | Admin / Desktop | MEASURED |
| Approved PNG | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/screen_admin_point_approved.png` | APPROVED_PNG |
| PNG SHA-256 | `c7172ed789ecdbcba04049dcc70faab8e2c90138959ab09de691318c5065a099` | MEASURED |
| PNG full/content bounds | `0,0,1448,1086` | MEASURED |
| Comparison size | `1448×1086`; crop 0, resize 0 | FIXED |
| HTML structure reference | `.../source/가족 플랫폼 화면 재현.dc.html`, anchor `1e` | MEASURED |
| HTML SHA-256 | `d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9` | MEASURED |
| Standalone pair | not found | NOT_APPLICABLE_MISSING_SOURCE |
| HTML canvas | `1440×1030` | STRUCTURE_REFERENCE_ONLY |
| Style guide | `assets/uploads/family_platform_style_guide_v1.png` | MEASURED |
| Style guide SHA-256 | `c52196127ff3050b1e3dbe90241d13d7dfa0dc93c7442bf25fbda4cd4aaa9e42` | MEASURED |

The approved PNG owns visual authority. Pixel scans on all four centre edges
show its rounded frame/shadow anti-aliasing reaches the PNG boundary; no
separable gallery margin exists. The HTML's smaller canvas is never a resize
target.

## Zone geometry and typography

Measurements below are from HTML 1e and must be compared against the approved
PNG during implementation; `PNG` remains the override for any difference.

| Zone | Geometry / layout | Typography / state |
|---|---|---|
| Frame | HTML `1440×1030`, radius 20, `#F7F6FC`, shadow `0 30px 70px rgba(40,20,90,.20)` | PNG comparison includes its full `1448×1086` frame/shadow |
| Sidebar | width 300; padding `26px 20px`; `#FBFAFE`; column gap 26 | family 26/900, admin mode 14 |
| Brand | top padding 6; logo `130×130`; centred; gap 6 | `우리 가족`, `관리자 모드` |
| Navigation | six rows; gap 4; padding `15px 16px`; radius 14; icon `21×21`, stroke 1.8 | inactive 16/500 `#4A3F72`; active `#EFEAFC/#DFD5F8`, 16/700 `#5A35DF` |
| Account footer | auto bottom; padding 14; radius 16; avatar 40; gap 12 | `관리자`, `admin@ourfamily.com` |
| Main | flex; padding `34px 40px`; gap 24; white; left edge shadow | title 36/900; description 15 |
| Header controls | date `14px 20px`, radius 14; CTA `15px 24px`, radius 14 | date 15; CTA 16/700 |
| Filter row | border `#F0EEF7`; radius18; padding `16px 18px` | tabs 15; active purple border; filter 15 |
| Stat cards | 3 equal grid columns; gap16; border/radius18; padding20; avatar 64 | labels15; values30/900; unit20 |
| Table | columns `1.1fr 2fr 1fr 1fr 1fr .9fr`; header `18px 24px`; five rows `16px 24px` | header14/700; cells15; negative points red/700 |
| Table actions | `36×36`, radius10, edit purple / delete red | HTML inline symbols only |
| Info banner | `#F4F1FD`; radius18; padding `20px 24px`; gap16; info circle42 | title16/700; body14 |

## Text inventory

`포인트 관리`; `포인트 차감 내역을 조회하고 관리할 수 있습니다.`;
`2026. 07. 22 (수)`; `차감 추가`; `전체`; `서연`; `민준`; `전체 필터`;
`서연 오늘 보유`; `민준 오늘 보유`; `오늘 총 차감`; table headings
`사용자/사유/금액/일시/등록자/관리`; five deduction reasons shown in HTML;
`모든 포인트 차감 내역은 기록으로 남습니다.` and its body copy.

No responsive contract exists in authority sources:
`RESPONSIVE_AUTHORITY_NOT_PROVIDED`.

## Asset authority

| Asset | Authority / implementation rule | State |
|---|---|---|
| Logo | `assets/uploads/family_platform_pin_logo_transparent_1024.png`; SHA `dd5c48b3e670636b7822a5893e213ce8e99fd667b82b4cb53026e344bea4f0b8` | EXACT_REUSE |
| Six sidebar icons | exact HTML 1e inline SVG paths, 21px/stroke 1.8 | HTML_FALLBACK |
| Avatar representations | no standalone asset found; reproduce HTML's initial/circle treatment only in preview | HTML_FALLBACK / AVATAR_ASSET_AUTHORITY_UNRESOLVED |

## 1E_SOURCE_TO_IMPLEMENTATION_MATRIX

| Canonical component | PNG/HTML basis | Current code candidate | Target preview location | State |
|---|---|---|---|---|
| Desktop frame/sidebar/main | PNG first, HTML geometry | none | page root/CSS module | REBUILD_REQUIRED |
| Logo | exact asset | none | sidebar brand | EXACT_REUSE |
| Sidebar icon paths | HTML inline SVG | none | preview-local icon functions | HTML_FALLBACK |
| Sidebar avatar/footer | HTML initial circle | current admin is protected | preview-local footer | HTML_FALLBACK |
| Header/filter/stat cards/table/banner | PNG first, HTML text/structure | `PointView` read-only | preview-local sections | APPROVED_PNG_OVERRIDE |
| `/admin/points` / PointView | current route/source | protected existing source | none | CURRENT_CODE_REFERENCE_ONLY / PROTECTED_EXISTING_SOURCE |

## Read-only current implementation inventory

`/admin/points` is declared as the `points` nested route in
`frontend/src/pages/AdminDashboard/index.tsx`. `frontend/src/pages/AdminDashboard/views/PointView/PointView.tsx`, its CSS and hook are reference-only; this task must not change them.

## Grounding decision

`CANONICAL_CONTENT_BOUNDS_MEASURED`; `PNG_FIRST_COMPARISON_CONTRACT_FIXED`;
`STYLE_GUIDE_GROUNDED`; `ASSET_AUTHORITY_RECORDED`; `READY_FOR_1E_IMPLEMENTATION`.

## Correction-002 canonical/target coordinate matrix

Coordinates use the fixed `1448×1086` approved-PNG canvas. CSS box is the
layout box; visible bounds exclude transparent logo/crop padding and include
SVG stroke coverage. Target deltas are resolved by shared CSS owners only.

| Element | Canonical box / visible x,y,w,h | Target box / visible x,y,w,h | Delta | Authority / CSS owner | Method / verification |
|---|---|---|---|---|---|
| Sidebar logo | 88,64,112,104 / 94,72,100,91 | 100,58,112,104 / asset visible bounds | target flow | PNG / `.logo` | intrinsic ratio; runtime check |
| Family name / admin label | 88,186,112,31; 95,232,98,18 | brand flow / glyph visible | target baseline | PNG / `.brand` | typography flow |
| Nav container / rows 1–6 | 21,315,272,421; each 272×51 | sidebar flow / same box | 0 target | PNG + HTML SVG / `.navItem` | 21px, 1.8 stroke |
| Active row | 21,463,272,51 | same box | 0 target | PNG / `.navItemActive` | shared border box |
| Footer / icon / text | 21,973,272,79; 40×40 / stroke visible | auto-bottom 272×79 / SVG 21px | 0 target | PNG + HTML SVG / `.accountFooter` | no emoji, overflow hidden |
| Title / subtitle | 359,61,184,48; 360,114,342,21 | 358,52,shared flow | recorded pre-runtime | PNG / `.main,.heading` | padding/line-height only |
| Date / CTA | 1014,75,205,53; 1242,70,155,59 | header shared baseline | recorded pre-runtime | PNG / `.headerActions` | common padding |
| Filter | 357,167,1038,88 | content-width box | 0 target | PNG / `.filters` | shared gap |
| Summary cards 1–3 | 357,286,328,132; gap 26 | equal grid columns | 0 target | PNG / `.stats` | grid only |
| Table / header / rows / pagination | 357,449,1038,476; 58; 5×72; 66 | one shared table grid | 0 target | PNG / `.tableCard,.tableRow` | no per-row margin |
| Info banner | 357,956,1038,92 | content-width box | 0 target | PNG / `.infoBanner` | shared section gap |

Table columns use one exact source and target grid: `1.1fr 2fr 1fr 1fr 1fr .9fr`; user, reason, amount, time, author, and actions share identical header/row column starts. No absolute patches, transforms, viewport branches, or per-element margins exist.

Static conclusion: all required elements mapped; CSS box and visible bounds are
separated; authority and owner recorded; unresolved blocking coordinate
conflicts 0; sidebar and table static contracts PASS.

## Correction-003 invalidation

`PREVIOUS_CANONICAL_COORDINATE_MATRIX_PASS` and
`PREVIOUS_RUNTIME_COORDINATE_VERIFICATION_PASS` are **INVALIDATED_BY_GPT_RENDERED_EVIDENCE**.
They compared design targets and layout contracts, not measured visible pixel
bounds from the two 1448×1086 raster images. Any subsequent matrix must record
canonical visible x/y/w/h, implementation visible x/y/w/h, and their delta from
the rendered image pair; CSS declarations and DOM bounds are supporting data
only.

## Correction-002 coordinate matrix

All coordinates are against the fixed approved-PNG canvas (`1448×1086`).
Implementation uses the same page-root coordinate system; no viewport-specific
offset is permitted.

| Element | Canonical x/y/w/h | Implementation geometry contract |
|---|---:|---|
| title | 359/61/184/48 | main padding-left 45, top 52; 40px/900 |
| subtitle | 360/114/342/21 | title stack gap 8; 16px |
| date / add | 1014/75/205/53; 1242/70/155/59 | common header baseline and padding |
| filter container | 357/167/1038/88 | full main content width |
| summary cards | 357/286/328/132; gap 26 | three equal grid columns |
| table / banner | 357/449/1038/476; 357/956/1038/92 | header 58, five 72px rows, footer 66 |
| sidebar logo | 88/64/112/104 | aspect-preserved centred logo asset |
| family identity | family baseline y=211 | centred brand flow only |
| six nav rows | x=21/w=272; 74px vertical rhythm | inline SVG 21px / stroke 1.8 |
| account footer | 21/973/272/79 | sidebar auto-bottom, 34px bottom padding |

### Table column contract

Header and every row use one shared grid: `1.1fr 2fr 1fr 1fr 1fr .9fr`.
User and reason text are left aligned; amount begins at its canonical column;
time, author and controls retain their common grid starts. Per-row margins,
absolute offsets, and text-specific adjustments are prohibited.
