# AMBIGUITY_AND_PM_REVIEW

All 8 items below were flagged `PM_REVIEW_REQUIRED` and have since been **RESOLVED** by explicit PM decision. Each entry records the decision and which files were updated.

## 1. Canvas color duplication — RESOLVED
**Decision**: `#F7F6FC` and `#F8F7FD` (1d/2g) represent the same semantic canvas meaning and are folded into one `--color-canvas` token — no alias created. `--color-surface` remains a separate semantic token (different role: card/modal surface vs. app background) despite both being light neutrals; not merged just because names differ.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `TOKEN_CLASSIFICATION.md`.

## 2. Card radius 18px / 20px — RESOLVED
**Decision**: not normalized to one value. Two distinct card families are kept as separate component tokens: `card-list` (18px — list-group wrappers: 1f, 1g, 1i, 1t, 2a) and `card-stat` (20px — single summary/stat cards: 1c, 1h, 2j).
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `TOKEN_CLASSIFICATION.md`, `COMPONENT_STYLE_CONTRACT.md`.

## 3. Avatar size ramp — RESOLVED
**Decision**: defined as an `xs/sm/md/lg` scale using only actually-observed repeat sizes: `xs` 34px, `sm` 44px, `md` 60px, `lg` 78px. No intermediate sizes (38/40/52/56/66/70/72/80) were invented as named steps — they remain per-composition variants of the nearest scale step.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `COMPONENT_STYLE_CONTRACT.md`.

## 4. Points progress-fill gradient — RESOLVED
**Decision**: stays a Point Festival (1c) screen-local token. Not promoted to global/shared component scope until a second independent consumer outside gamification surfaces is confirmed.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `SCREEN_LOCAL_TOKEN_REGISTER.md`, `TOKEN_CLASSIFICATION.md`.

## 5. Chat bubble color — RESOLVED
**Decision**: defined as a `ChatBubble` component token with three explicit states — `own` (#6944EF, kept distinct from brand-600 per approved source), `other` (#F3F0FF), `system` (pill, #EFECF8). No approved image conflicted with the HTML for this component, so the HTML value stands as authority.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `COMPONENT_STYLE_CONTRACT.md`, `TOKEN_CLASSIFICATION.md`.

## 6. Input error state — RESOLVED
**Decision**: recorded as `NOT_DEFINED_IN_APPROVED_SOURCE`. Approved screens only signal input errors via helper-text color; no new border/error visual state is invented. This absence is explicitly not a completion blocker.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `COMPONENT_STYLE_CONTRACT.md`, `TOKEN_CLASSIFICATION.md`.

## 7. Motion tokens — RESOLVED
**Decision**: excluded entirely from the canonical Visual Token set — no evidence exists in the approved static source. Motion will be defined separately as a UX Engineering baseline, not as a design token. Previously-proposed placeholder durations (120/200/320ms) were removed rather than kept as approved values.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `TOKEN_CLASSIFICATION.md`, `FINAL_REPORT.md`.

## 8. Hidden screens (1z0–1z5) — RESOLVED
**Decision**: screens reachable via screen-selection/route/JS state are included in source inventory and token extraction regardless of a current `display:none`. Only screens with no reachable path at all would be marked `NON_CANONICAL_CANDIDATE` — none were found in this set, so all six (1z0–1z5) remain fully canonical evidence.
**Files updated**: `canonical-tokens.json` (hiddenScreens policy), `TOKEN_CLASSIFICATION.md`, `SOURCE_SCREEN_INVENTORY.md` (already listed these as valid evidence — confirmed unchanged).

---

## Asset resolution (companion decision, not a numbered ambiguity)
Real photo/avatar asset replacement is separated into its own follow-up task. The style guide instead fixes the **slot contract**: size, aspect ratio, object-fit, crop alignment, radius, fallback, and loading/error behavior for avatar photos and album photos. Placeholder colors are excluded from the UI token palette.
**Files updated**: `canonical-tokens.css`, `canonical-tokens.json`, `COMPONENT_STYLE_CONTRACT.md`.

---

No open ambiguities remain. See `FINAL_REPORT.md` for the updated final verdict.
