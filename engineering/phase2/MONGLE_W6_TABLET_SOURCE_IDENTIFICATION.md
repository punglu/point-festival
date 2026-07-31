# MONGLE_W6_TABLET_SOURCE_IDENTIFICATION

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 8 (태블릿 정본 HTML 발견 Gate).

## Search scope actually used

The prompt's search roots (`/Users/mac/mac_Project/minecraft_points_festivals/temp/screen_renew`,
`.../temp`) do not exist in this environment (Linux/WSL, `/appl/point-festival`). Per PM direction given
this session, the search was redirected to the actual repository:

```
find /appl/point-festival -iname "*tablet*" -o -iname "*태블릿*" -o -iname "*.dc.html" -o -iname "*responsive*"
```

Single hit region: **`docs/temp/design_tablet/`** (gitignored via root `/docs/` rule — untracked,
scratch/reference-drop location, same role as a `temp/` folder would play on the Mac side; no other
candidate directory anywhere in the repo matched).

## Candidate inventory (40 files, `.thumbnail`/`Zone.Identifier` excluded from content-count, full manifest at `/tmp/mongle-wave6-0c-gate/tablet_source_manifest.sha256`)

| Path | Role |
|---|---|
| `가족 플랫폼 화면 재현-tablet.dc.html` | **Tablet candidate (root copy)** |
| `design_handoff_family_platform/screens/가족 플랫폼 화면 재현-tablet.dc.html` | Tablet candidate (packaged copy) |
| `가족 플랫폼 화면 재현.dc.html` | Mobile 71-screen HTML (root copy) |
| `design_handoff_family_platform/screens/가족 플랫폼 화면 재현.dc.html` | Mobile 71-screen HTML (packaged copy) |
| `가족 플랫폼 화면 재현-tokenized.html` (+ packaged copy) | Same 71 screens, `var(--token)` values |
| `design-system/*` (+ packaged copy) | Style guide HTML, `canonical-tokens.css`/`.json`, 8 classification MD docs |
| `uploads/*.png` (10 files) | Raster assets — **verified SHA-identical to `screen_renew/uploads/`**, see below |
| `HANDOFF_PROMPT.md`, `support.js`, `.thumbnail` | Delivery metadata / preview runtime — not design content |

## Duplicate resolution (exactly 2 raw candidates → 1 master, per Section 8 rule)

Both the tablet HTML and the mobile HTML exist twice (root vs. `design_handoff_family_platform/screens/`
packaged copy). SHA-256 confirms **byte-identical duplicates**, not competing versions:

| File | Root SHA-256 | Packaged-copy SHA-256 | Verdict |
|---|---|---|---|
| `...-tablet.dc.html` | `24a02ab6...571d6` | `24a02ab6...571d6` | **IDENTICAL** — `EXPECTED_DUPLICATE` |
| `...화면 재현.dc.html` (mobile) | `d0c42227...2d30fb9` | `d0c42227...2d30fb9` | **IDENTICAL** — `EXPECTED_DUPLICATE` |
| `...tokenized.html` | `1d11874d...25da5327` | `1d11874d...25da5327` | **IDENTICAL** — `EXPECTED_DUPLICATE` |
| `design-system/` (8 MD + CSS + JSON + HTML) | — | — | `diff -rq` → **zero differences**, full-tree `EXPECTED_DUPLICATE` |

Root copy (`docs/temp/design_tablet/가족 플랫폼 화면 재현-tablet.dc.html`) is designated **master**; the
`design_handoff_family_platform/` tree is the packaged duplicate (matches the delivery's own
`HANDOFF_PROMPT.md`, which describes it as "위 파일들의 사본"/"a copy of the above files").

**Result: exactly one content-distinct tablet candidate → `TABLET_CANONICAL_SOURCE_IDENTIFIED`.**
No `TABLET_SOURCE_AMBIGUOUS` condition applies; Hard Stop #11 does not trigger.

## Tablet HTML characterization (Section 8 checklist)

| Check | Finding |
|---|---|
| SHA-256 (master) | `24a02ab63b7e4aafccbbc064ba7f99d1ffe429ef4f43f8427f6699defcf571d6` |
| Size | (see manifest) |
| Title / doc marker | No `<title>`; header comment: "TABLET RESPONSIVE COMPANION — 15 priority screens, landscape (1024x700) + portrait (768x1024) tablet breakpoints. Denser multi-column layouts, not scaled-up phone frames. Approved phone-frame source (가족 플랫폼 화면 재현.dc.html) untouched." — **the file's own header explicitly names the mobile 71-screen `.dc.html` (not `standalone-src.html`) as its paired approved source.** |
| Canvas/viewport sizes | Landscape `1024×700`, portrait `768×1024` — hardcoded per-screen `<div style="width:...px; height:...px">`, not CSS media queries |
| Screen section headers | 15 numbered `<!-- ==== N. 화면명 ==== -->` comments (lines 32–2003), covering 1b/1c/1d/1g/1h/1i/1k/1n/1q/2j/1e/2i/2x/3c/2q |
| **Actual `data-screen-label` coverage (re-measured this session, not copied from the delivery's own README)** | **132 labels = 66 distinct screens** (33 pairs of 가로/세로), continuing **past** the last section-header comment (line 2003) through line ~4136 with unlabeled sections for 51 additional screens. The delivery's own `README.md`/`HANDOFF_PROMPT.md` both undercount this as "15 screens" / "71개 화면" (two different, both-wrong claims — see Delta Register). |
| A1–A5 mapping | See table below |
| Breakpoint/layout rule | No `@media` queries found (grep confirmed 0 hits); each screen/viewport pair is a separately hand-authored fixed-size block, matching the mobile source's own "no responsive CSS, only discrete artifacts" pattern already documented in `6.0A/HTML_STRUCTURE_EXTRACTION.md` |
| Tablet-specific DOM | Left icon rail (92px width, replaces BottomDock) on landscape; BottomDock retained on portrait; multi-column CSS Grid layouts (`grid-template-columns:1.45fr 1fr`, `repeat(5,1fr)`, etc.) |
| Asset references | `uploads/family_platform_pin_logo_transparent_1024.png` (same file, SHA-verified below) |
| External dependency | Google Fonts `Noto Sans KR` CDN link (same as mobile source) |
| Inline style ratio | ~100% (same authoring convention as the mobile HTML family) |
| Distinguishable from a desktop source | Yes — explicit `1024×700`/`768×1024` labeling, phone-frame chrome fully absent (no fake status bar/home-indicator observed in the 6 screens read in depth so far), fixed-size boxed presentation (not a fluid desktop layout) |

## A1–A5 to tablet-screen-ID mapping

| Mongle screen ID (6.0AB) | Tablet delivery screen ID | Tablet coverage |
|---|---|---|
| A1 (로그인/프로필/PIN) | `1a`(로그인/프로필 선택), `1a-1`(ID/PW 로그인), `1j`(PIN입력), `1j-1`(계정잠금), `1u`(PIN변경), `2s`(PIN최초설정), `1r`(온보딩), `2d`(비밀번호찾기/이메일인증) | **`1a`/`1a-1` = NO TABLET VARIANT** (confirmed below); `1j`/`1j-1`/`1u`/`2s`/`1r`/`2d` = covered |
| A2 (Family Home) | `1b`(홈) | Covered — section header #1 |
| A3 (Markpoint / 포인트 잔치) | `1c`(포인트 잔치) | Covered — section header #2 |
| A4 (Wagle GROUP / 가족 대화) | `1d`(대화) | Covered — section header #3 |
| A5 (Admin Point / 관리자 포인트 관리) | `1e`(포인트관리) | Covered — section header #11 |
| — (no A-series equivalent) | `1f`(나의 프로필) | **NO TABLET VARIANT** |

**All 3 screens with zero tablet coverage (`1a`, `1a-1`, `1f`) were independently re-verified this
session** by grepping the full `data-screen-label` list — none of the 66 covered screens map to "로그인",
"프로필 선택", or "나의 프로필".

## Approved-asset overlap with 6.0A's `screen_renew` (independently re-verified this session)

10/10 raster files in `docs/temp/design_tablet/uploads/` are **SHA-256-identical** to the corresponding
rows of `6.0A/approved_source_file_inventory.csv` (which recorded them under `screen_renew/uploads/`):

| Asset | SHA-256 match |
|---|---|
| `screen_login_approved.png` | ✅ `fb3c9b6b...a73765` |
| `screen_family_home_approved.png` | ✅ `d486d0eb...4070e9f2` |
| `screen_point_festival_approved.png` | ✅ `35bdeff6...41f75eb93` |
| `screen_family_chat_approved.png` | ✅ `b3dbc554...21f0ff9300` |
| `screen_admin_point_approved.png` | ✅ `c7172ed7...5065a099` |
| `family_platform_pin_logo_transparent_1024.png` | ✅ `dd5c48b3...5674c5c4070e9f2`(logo) |
| `brand_pin_logo_transparent.png` (2048²) | ✅ |
| `family_platform_style_guide_v1.png` / `_preview.png` | ✅ both |
| `19de6297-c168-45f4-be59-878a01bc0641.png` (UNKNOWN, 1536×1024) | ✅ |

This is strong, direct evidence that `docs/temp/design_tablet/` traces to the same design source as
`screen_renew` (shared brand asset folder). **This is not evidence that the two HTML structural sources
are the same** — see next section.

## Mobile HTML source conflict (new finding, not anticipated by the task's own gate checklist)

`6.0A/APPROVED_SOURCE_FILE_INVENTORY.md` recorded `standalone-src.html` (and its byte-identical
Korean-named twin, same filename as used here: `가족 플랫폼 화면 재현.dc.html`) as **153,869 bytes**,
SHA-256 `5f823d4cc98755785ff308bf9e3d756d3a40fb5f93a2194c756886ccef3a82a7`, containing exactly **10
screens** (A1, A1-S1, A2, A3, A4, A5, EXTRA-01..04).

The file with the **same display name** in `docs/temp/design_tablet/` is **636,567 bytes**, SHA-256
`d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9` — **not the same file** — and
contains **71 screens** under a completely different ID scheme (`1a`–`3l`, per its own
`design-system/SOURCE_SCREEN_INVENTORY.md`).

Classification: **SOURCE_CONFLICT**, not `MODIFIED_EXISTING_MOBILE_SOURCE` (no shared identity/history
to call it a "modification" of) and not silently treated as a superset/replacement, per the task's own
rule against confirming source relationships by filename alone. Two explanations are equally consistent
with the evidence gathered this session and **neither is confirmed**:

1. The 71-screen file is a **later, more complete design pass** from the same design session/brand
   asset set, and `standalone-src.html` (10-screen) is an earlier snapshot that 6.0A happened to analyze.
2. The two are **independent deliverables** (different scope/purpose) that happen to reuse the same
   brand uploads folder because they come from the same overall product design initiative.

This conflict is carried forward as **PM Decision D13** in `MONGLE_W6_PM_DECISION_REGISTER.md`. Per
Section 5 Hard Stop discipline, this task does **not** guess which mobile HTML is authoritative for
A1–A5 pixel-level values; the existing 6.0A/6.0B measurements against `standalone-src.html` remain the
only pixel-level mobile evidence this document set relies on (tagged `COMMITTED_DERIVED_EVIDENCE`, not
`RE-VERIFIED_THIS_SESSION`), and the 71-screen file is used **only** for its role as the tablet
companion's stated mobile counterpart (structure/content reference for the 15 tablet-covered screens),
never for pixel-level A1–A5 measurement.

## Required output classification

**`TABLET_CANONICAL_SOURCE_IDENTIFIED`**
- Master: `docs/temp/design_tablet/가족 플랫폼 화면 재현-tablet.dc.html` (SHA-256 `24a02ab6...571d6`)
- Duplicate (packaged copy, byte-identical): `docs/temp/design_tablet/design_handoff_family_platform/screens/가족 플랫폼 화면 재현-tablet.dc.html`
- Coverage: 66/71 catalog screens have a tablet variant; all 5 A1–A5 anchor screens except A1's
  `로그인/프로필 선택` sub-screen are covered (A1's PIN/lock/onboarding sub-screens are covered; the
  top-level profile-picker screen is not).
- Companion mobile source it declares itself paired to (`가족 플랫폼 화면 재현.dc.html`, 71-screen) is
  **not** the same file 6.0A measured (`standalone-src.html`, 10-screen) — flagged as `D13`, not resolved.
