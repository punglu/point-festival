# COMPONENT_STYLE_CONTRACT

Structural + token contract for components that repeat across ≥4 approved screens. States not observed in the static mockups are marked accordingly — these are proposed conventions, not extracted facts (PM_REVIEW_REQUIRED).

## Button — Primary Pill
- **Structure**: full-width or auto-width block, centered label, rounded rect.
- **Default**: bg `--color-brand-600`, text `--color-text-on-brand`, radius 14–16px, padding `16px` (or `13–15px` compact variant), shadow `--shadow-cta`.
- **Hover**: not present in source (static). Proposed: bg darken ~8%. PM_REVIEW_REQUIRED.
- **Pressed**: not observed. Proposed: remove shadow, translateY(1px). PM_REVIEW_REQUIRED.
- **Focus**: not observed. Proposed: `0 0 0 4px rgba(90,53,223,.10)` ring (reuse input focus ring). PM_REVIEW_REQUIRED.
- **Disabled**: observed once as "300P 필요" locked reward tile — bg `#fff`/border `#E3DEF5`, text `--color-text-disabled`, no shadow.
- **Error**: not applicable to this component in source.

## Button — Secondary / Outline
- **Default**: bg `#fff`, border `1px solid --color-border-default`, text `--color-text-secondary`.
- **Danger variant**: border `#F8DDE3`, text `--color-danger` (used for 반려/삭제/계정 정지 actions).

## Card
- **Structure**: rounded container, optional icon/avatar leading element, text stack, optional trailing action/badge.
- **Two RESOLVED card families** (not normalized to one radius):
  - `card-list` (radius 18px): multi-row list-group wrapper — 1f 내 활동, 1g 오늘 일정, 1i 할 일, 1t 참여 멤버, 2a 최근 활동.
  - `card-stat` (radius 20px): single summary/stat card — 1c 오늘 통계, 1h 앨범 카드, 2j 리워드 타일.
- **Default**: bg `--color-surface`, shadow `--shadow-card-sm`, no border (shadow-only elevation) OR `1px solid --color-border-subtle` (admin/table cards use border, not shadow).
- **Hover/Pressed**: not observed (static mockups). Not defined — not a blocker.

## Input Field
- **Structure**: label above, single-line value row, optional leading icon.
- **Default**: bg `#fff`, border `1px solid --color-border-input`, radius 14–16px, padding `14px 16px`.
- **Focus**: border `1.5px solid --color-brand-600` + ring `0 0 0 4px rgba(90,53,223,.10)` — this IS observed directly (1a-1 PIN field, PIN change field).
- **Error**: helper text below field turns `--color-danger`. Input border itself stays neutral in the approved source — **RESOLVED: `NOT_DEFINED_IN_APPROVED_SOURCE`**. No new red-border state is invented; absence is not a completion blocker.
- **Disabled**: not observed.

## Bottom Dock (tab bar)
- **Structure**: 4 equal-width columns, icon above label, thin top border separating from content, home-indicator bar below.
- **Default (inactive item)**: icon+label `--color-text-disabled`, no weight.
- **Active item**: icon+label `--color-brand-600`, label `font-weight:700`.
- **Icon size**: 23×23, stroke-width 1.8, 1.8px round linecap/join (single-stroke style, no filled icons in dock).

## Avatar
- **Structure**: circular container, either initials-on-gradient (unphotographed member) or image (brand logo/photo).
- **RESOLVED size scale** (only actually-observed repeat sizes named — no invented intermediate steps):
  - `xs` 34px — 1t 참여 멤버 리스트, 2g 채팅 답장
  - `sm` 44px — 1b 홈 헤더, 1d 대화 리스트 아바타
  - `md` 60px — 2i 부모 대시보드 통계, 2c 레벨업 아이콘
  - `lg` 78px — 1a 프로필 선택 카드
  - Other observed sizes (38/40/52/56/66/70/72/80) are per-composition variants of the nearest scale step, not separate named tokens.
- **Presence dot**: 13–16px circle, `--color-success-dot` fill, 2–3px white border, bottom-right offset.
- **Locked state**: gray gradient fill + lock badge overlay (1a 지호 프로필).
- **Photo asset slot contract** (RESOLVED — real assets are a separate follow-up task):
  - shape: circle · object-fit: cover · crop-align: center · fallback: initials-on-gradient · loading/error behavior: not defined in approved source.

## Badge / Status Pill
- **Structure**: inline pill, no icon by default (emoji used only in a few legacy instances — flagged as one-off, not canonical).
- **Tone map**: success → `--color-success` / `--color-success-surface`; warning → `--color-warning` / `--color-warning-surface`; danger → `--color-danger` / `--color-danger-surface`; neutral/info → `--color-brand-600` / `--color-tint-purple-200`.

## Modal / Bottom Sheet
- **Modal**: centered, radius 24–28px, backdrop `rgba(23,16,58,.42–.55)`, shadow `--shadow-modal`.
- **Sheet**: anchored bottom, radius `28px 28px 0 0`, drag handle `40×5px` `#E3E1EA` pill centered at top, shadow `--shadow-sheet`.
- **Close affordance**: `✕` top-right, color `--color-text-faint`/`--color-text-disabled` — not a real icon-button in source, plain text glyph. PM_REVIEW_REQUIRED to formalize as icon-button component.

## List Row
- **Structure**: leading icon/avatar (34–44px), 1–2 line text stack (flex:1), optional trailing meta text and/or chevron/toggle.
- **Divider**: `1px solid --color-border-subtle-alt` between rows, no divider after the last row in a group.
- **Chevron**: SVG `M5 9l7 7 7-7`-style single-stroke arrow (post-cleanup) — NOT the literal "›" or "⌄" glyphs; those were a known alignment defect in earlier iterations and have been corrected in the approved file.

## Chat Bubble
- **RESOLVED 3-state contract**: `own` / `other` / `system`.
  - **own**: bg `#6944EF` (kept distinct from `--color-brand-600` per approved source — not normalized), text white, radius `18px 6px 18px 18px` (tail top-right), align right. Metadata: "읽음 N" receipt above timestamp.
  - **other**: bg `#F3F0FF`, text `--color-text-primary`, radius `6px 18px 18px 18px` (tail top-left), align left.
  - **system**: pill shape (radius 999px), bg `#EFECF8`, text `--color-text-muted`, centered (date dividers, "사진 추가됨" notices).
- **Metadata**: timestamp 11px `--color-text-disabled` beside bubble.

## Album / Photo Slot Contract (RESOLVED — asset swap is a separate follow-up task)
- grid tile: aspect 1:1, radius 12px, object-fit cover, center crop.
- album card thumb: aspect 4:3, radius 12px, object-fit cover, center crop.
- hero highlight: aspect 16:9, radius 24px, object-fit cover, center crop.
- fallback: diagonal placeholder pattern (not a UI color token — excluded from palette).
- loading/error behavior: not defined in approved source.

## Toggle Switch
- **Structure**: pill track + circular knob, knob positioned via flex `justify-content: flex-start|flex-end`.
- **Contract fix applied in approved file**: track MUST declare `align-items:center` alongside `justify-content` — its absence was a real defect (knob sat top-aligned, not vertically centered) found and corrected during PM review. This is now part of the canonical contract, not optional.
- **On**: bg `--color-brand-600`, knob right.
- **Off**: bg `#E3E1EA`, knob left.
