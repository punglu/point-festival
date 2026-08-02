# Mongle Screen Porting Practical Guide

Status: evidence-backed working guide from A2 family home (`1b`) and 1e admin
point management (`1e`). It is not a shared-component design, automation plan,
or a final visual-gate verdict.

## Scope and authority

For a screen with a tokenized canonical HTML source, port its **app-content**
directly into a page-local React preview first. Preserve DOM order, visible
copy, layout values, inline SVG paths, and assets. The approved PNG is used to
resolve a major conflict only: missing or wrong asset, clipping, overflow,
whole-section displacement, or a materially different icon/background.

Exclude gallery labels, device chrome, and board decoration; do not remove app
content to make a viewport fit. Do not resize a canonical PNG for comparison.

## Porting sequence

1. Extract the app-content element from tokenized HTML and list its visible
   text/assets.
2. Convert the DOM mechanically to JSX in `pages/<Screen>/index.tsx`.
3. Move screen CSS into `<Screen>.module.css`; retain canonical literals when
   an equal semantic token does not already exist.
4. Keep exact repository assets and canonical inline SVGs page-local.
5. Add only a detached `/__wave6/<screen>` preview route; do not replace a
   product route, add navigation, API calls, storage writes, or sessions.
6. Run lint/build, then rebuild the official `mongle` frontend once per batch.
7. Correct only a measured BLOCK_NOW mismatch using a shared layout contract.

## Layout contracts observed

| Contract | Evidence | Correct repair |
| --- | --- | --- |
| Table header/body | 1e | One `grid-template-columns` contract for header and every body row. |
| Pagination | 1e | Reserve non-shrinking table/footer height; do not rely on flex shrink. |
| Sidebar rhythm | 1e | One nav row height and one nav gap; keep footer `margin-top:auto`. |
| Mobile dock | A2 | Use page flex sizing and dock height/padding, not positional offsets. |
| Section rhythm | A2, 1e | Adjust wrapper padding, section gaps, and flex sizing before child margins. |
| Responsive fit | A2 | Test all approved viewports; horizontal overflow and scrollbar are failures. |

Do not use `transform`, per-row margins, per-column absolute positioning, or
viewport-only patches to hide a structural mismatch.

## Asset authority

Use this order:

1. Exact repository asset.
2. Exact canonical HTML inline SVG.
3. Clean, preview-local crop from the approved PNG, with source/crop/result
   hashes recorded.
4. Page-local temporary fallback with an explicit authority gap.

Do not keep canonical placeholder emoji, install a similar icon library, create
an AI asset, or promote a first-screen asset to `shared`.

## UI-only separation

Preview pages allow static fixture arrays, local presentation state, no-op
buttons, CSS Modules, page-local assets, and inline SVG. They forbid API/service
calls, WebSocket/SSE, store/context login actions, storage or cookie writes,
product navigation, timers/polling, and dependencies on legacy product views.

The route imports only the page entry. Existing product routes remain untouched.

## Practical disposition table

| Classification | Examples | Action |
| --- | --- | --- |
| BLOCK_NOW | required element/copy/asset missing; clipping; overflow; wrong route; table/sidebar/dock contract failure; preview network or storage activity | Correct before evidence refresh. |
| TEST_LATER | 1–2px position difference; font antialiasing; space advance; thin-border or same-SVG raster difference | Record; do not redesign for it. |
| WIRE_LATER | real data lengths; loading/empty/error states; confirmed focus/hover/disabled behavior | Decide during API wiring/interaction work. |
| NON_BLOCKING_RASTER | residual pixel-diff value, shadow diffusion, tiny stroke variation | Do not require diff = 0. |

## Commonization rule

Start page-local. Record a shared candidate only after a second real consumer
uses the same visual **and** behavioral contract. Promote only after both
consumers are confirmed; superficial resemblance is insufficient.

## Batch handoff — Wave 6 mobile HTML direct ports

Recommended single-session batch: 10 screens, all with tokenized HTML anchors
and no current desktop-only administration surface:

| Canonical ID | Label | Form factor | HTML-direct status |
| --- | --- | --- | --- |
| `1d` | 대화 | Mobile | ready |
| `1f` | 나 프로필 | Mobile | ready |
| `1g` | 가족 일정 | Mobile | ready |
| `1h` | 앨범 | Mobile | ready |
| `1i` | 할 일 | Mobile | ready |
| `1k` | 미션 상세 | Mobile | ready |
| `1l` | 보상 교환 | Mobile | ready |
| `1n` | 알림 목록 | Mobile | ready |
| `1o` | 일정 추가 | Mobile | ready |
| `1p` | 사진 상세 | Mobile | ready |

All ten have a visible tokenized-HTML anchor. None has been independently
checked here against an approved PNG for a new visual gate; that remains a
screen-level review obligation. Desktop admin anchors (`1m`, `1z1`, `1z2`,
`2e`, `2i`) and modal/error flows are excluded from this first batch because
they introduce distinct desktop or interaction-state contracts.

### Single-session follow-up prompt

```text
Task: MONGLE-W6-NEXT-BATCH-HTML-DIRECT-PORT-001

Work sequentially in this worktree. For the ten listed canonical IDs, port
tokenized HTML app-content directly to page-local React/CSS Modules and add
detached preview routes. Preserve DOM order, exact copy, assets and inline SVG.
Do not replace product routes, add API/storage/navigation behavior, create
shared components, or introduce a generic generator.

Per screen: render success; wrong text 0; required app-content omission 0;
asset 404 0; horizontal overflow 0; preview API/WebSocket/storage/navigation 0.
Per batch: ESLint once; TypeScript/Vite build once; official `mongle` frontend
rebuild once; route smoke test once; representative screenshot evidence only
for screens with a measured blocking mismatch.
```
