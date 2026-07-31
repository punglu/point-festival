# ONE_OFF_LITERAL_REGISTER

Values used exactly once, with no reuse rationale. Not tokenized.

| Location | Value | Reason to keep as literal |
|---|---|---|
| 1a status bar battery/signal glyphs | `#17103A` fills, hand-built with `radial-gradient`/`border` shapes | Fake device chrome, explicitly excluded from token evidence per task rules. |
| 1y error state icon | bg `#F1EDFC`, icon color `#8A73D6` | Single-use empty/error illustration tint; `#8A73D6` appears nowhere else in the file. |
| 2i dashboard stat "가족 전체 포인트" number | `--color-brand-600` on a stat that otherwise would be neutral | Cosmetic emphasis choice for one KPI tile, not a rule ("all stat numbers are brand-colored" is false — most stat numbers are `--color-text-primary`). |
| 1t chat-settings channel icon composite (logo + small pencil badge) | `#5A35DF` badge on top of the brand pin logo image | One-off composition specific to the "change room photo" affordance. |
| 2j "영화관 나들이" locked reward tile | `opacity:.55` | Single disabled-preview treatment; not reused as a formal "locked" component state elsewhere. |
| 1x weekday bar chart bar heights (40/70/55/100/30/65/15%) | literal per-bar percentages | Sample/mock data, explicitly excluded from token extraction per task rules (fake data). |
| Emoji glyphs (🎉 🔒 🍭 🎮 etc.) throughout | literal characters | Task rules exclude temporary emoji from design-token evidence; treat as placeholder content, not iconography contract. |
| 1r onboarding step-dot fill `#5A35DF` vs unfilled `#EDE8FA` | literal pair | Only one stepper exists in approved screens; insufficient evidence for a "stepper" component token. |
| 2j reward-shop per-card icon tile colors | `#FBE0E6`/`#EEE8FF`/`#FDEFCF`/`#DCF4E8` | Cosmetic per-item variety, not a semantic mapping (confirmed against SCREEN_LOCAL register — kept there as a set, but each individual hex-to-icon pairing itself is a one-off, not a rule to encode). |
