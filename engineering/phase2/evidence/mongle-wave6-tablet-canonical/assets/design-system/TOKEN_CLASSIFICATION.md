# TOKEN_CLASSIFICATION

Source of authority: PM-approved screens in `가족 플랫폼 화면 재현.dc.html` (1a–1y, 1z, 2a–2k), including hidden/duplicate-removed screens 1z0–1z5 which still count as approved visual evidence even though hidden from the live canvas.

## A. Global Semantic Tokens

| Token | Value | Meaning | Evidence (screens/selectors) |
|---|---|---|---|
| color-brand-600 | #5A35DF | primary action, active nav/tab, links | 1a PIN dots, 1b CTA, all "완료/제출/저장" buttons |
| color-brand-500 | #6B46F2 | link default, progress-fill start | helmet `a{}`, 1c progress bar |
| color-canvas | #F7F6FC | app background (RESOLVED: single token; 1d/2g's #F8F7FD folded in, no alias) | all frames incl. 1d, 2g |
| color-surface | #FFFFFF | card/modal surface — semantic alias distinct from canvas by role, not merged despite similarity | all cards |
| color-text-primary | #17103A | headings/primary text | all screens |
| color-text-secondary | #4A3F72 | supporting text | all screens |
| color-text-tertiary | #8A83A8 | captions/meta | all screens |
| color-text-disabled | #A8A5B6 | timestamps, inactive nav | all screens |
| color-border-subtle | #F0EEF7 | hairline divider | all card/list containers |
| color-success / -surface | #1F9D62 / #DCF4E8 | positive status | 1c 완료 배지, 1i, 1m 승인 카운트 |
| color-warning / -surface | #B4791A / #FDEFCF | pending/attention status | 1c 진행중, 1m 대기, 1v |
| color-danger / -surface | #EF4665 / #FBE0E6 | destructive/error/negative | 1a 잠김, 1l −P, 1s 반려 |
| color-reward | #F1983A (+ #FFC93C gradient) | point/star reward accent | 1a 포인트 배지, 1c, 1l, 1x |
| radius-pill | 999px | chip/badge/pill button | all badges & filter chips |
| radius-xl (frame) | 44px | phone device frame | every mobile frame |
| radius-card-list | 18px | list-group container card (RESOLVED, kept distinct) | 1f, 1g, 1i, 1t, 2a |
| radius-card-stat | 20px | single summary/stat card (RESOLVED, kept distinct) | 1c, 1h, 2j |
| avatar-scale | 34/44/60/78px | xs/sm/md/lg (RESOLVED: only observed sizes named) | 1t/2g, 1b/1d, 2i/2c, 1a |
| spacing scale | 4/6/8/10/12/14/16/18/22/24 | gap & padding rhythm | pervasive |
| typography roles | 11–36px, weights 400/500/700/900 | text hierarchy | pervasive |

## B. Shared Component Tokens

| Component | Token basis | Reused in (≥4 screens) |
|---|---|---|
| Button (primary pill) | radius 14–16px, shadow `0 10px 22px rgba(70,35,180,.28)` | 1a-1, 1k, 1l, 1o, 1r, 1s, 1u, 1z |
| Card | radius 18px, shadow `0 5px 16px rgba(60,30,120,.05)` | 1b, 1c, 1f, 1g, 1h, 1i, 1x, 2a |
| Input field | border `#E6E2F4`, focus `1.5px #5A35DF` + ring | 1a-1, 1o, 1u, 1z |
| Bottom dock | icon 23px, active `#5A35DF`, inactive `#A8A5B6` | 1b, 1c, 1d, 1f, 1g, 1h, 1i, 2j |
| Avatar (circle) | sizes 34/38/44 (row) vs 60–80 (hero) | pervasive |
| Badge/status pill | radius 999px, 12px/700 | 1c, 1e, 1g, 1m, 1q |
| Modal/Sheet | modal radius 24px, sheet `28px 28px 0 0` | 1z, 2c, 2h, 2j |
| List row | 13px/14px padding, divider `#F4F2FA` | 1f, 1g, 1i, 1t, 2a, 2k |
| Chat bubble | own `#6944EF` / other `#F3F0FF` / system pill `#EFECF8` (RESOLVED 3-state) | 1d, 2g |

## C. Screen-Local Tokens

See `SCREEN_LOCAL_TOKEN_REGISTER.md` for full list. `points-progress-fill` is RESOLVED as screen-local (Point Festival) pending a 2nd independent consumer.

## D. One-Off Literals

See `ONE_OFF_LITERAL_REGISTER.md`. Examples: 2j reward-shop icon tile colors (#FBE0E6/#EEE8FF/#FDEFCF/#DCF4E8 per single card), 1y error-state icon circle `#F1EDFC`/`#8A73D6` (only error/empty-state screens), 2i dashboard-only stat number colors.

## Not Defined In Approved Source

- **Input error border**: helper-text color signals error; border stays neutral. RESOLVED as `NOT_DEFINED_IN_APPROVED_SOURCE` — not a blocker, no new state invented.

## Hidden Screens Policy (RESOLVED)

Screens 1z0–1z5 are reachable via screen-selection/JS state (not orphaned) and are therefore included in source inventory and token evidence, despite currently being `display:none` in the approved file.

## Motion (RESOLVED)

Excluded from canonical visual tokens — no evidence in approved static source. To be defined separately as a UX Engineering baseline.

## Resolved Items
All 8 items formerly flagged PM_REVIEW_REQUIRED are now RESOLVED — see `AMBIGUITY_AND_PM_REVIEW.md`.
