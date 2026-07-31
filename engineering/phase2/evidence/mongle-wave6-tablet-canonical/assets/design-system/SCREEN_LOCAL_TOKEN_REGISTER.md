# SCREEN_LOCAL_TOKEN_REGISTER

Tokens meaningful only within one screen or one hero moment. Not promoted to global/component scope.

| Screen(s) | Local token | Value | Why not promoted |
|---|---|---|---|
| 1a, 1a-1, 1j, 1j-1, 1r | login-hero-gradient | `linear-gradient(180deg,#C6A9F5 0%,#B58EF0 30%,#A579EC 52%,#F7F6FC 78%,#F7F6FC 100%)` | Purple-to-canvas mood wash specific to auth/onboarding moments; no non-auth screen reuses it. |
| 1b | home-hero-card-gradient | `linear-gradient(135deg,#D9CBF8 0%,#C3AAF3 55%,#B79AF0 100%)` | Appears once (홈 "가족 대화" hero card); no second instance to justify a shared token. |
| 1c, 1f, 1x | points-progress-fill | `linear-gradient(90deg,#6B46F2,#5A35DF)` | **RESOLVED**: PM confirmed Point Festival (1c) screen-local; not promoted until a 2nd independent consumer outside gamification is confirmed. |
| 1e, 1m, 1v, 2a, 2e, 2i | admin-sidebar-width | `300px` | Fixed layout constant for the admin desktop shell only; not meaningful on mobile screens. |
| all admin desktop screens | admin-canvas-size | `1440×1030` | Presentation/frame size for this review artifact, not a responsive breakpoint. |
| 1d, 2g | chat-composer-shadow | `0 6px 16px rgba(60,30,120,.07)` | Pill-shaped composer bar shadow, distinct enough from generic card shadow to track separately; only 2 screens use it. |
| 1g | calendar-legend-dots | `#C4B4F2` / `#7ED9AE` / `#F7CD5C` | Category color-coding specific to the family-calendar feature; not a status-token (do not confuse with success/warning). |
| 2c | levelup-modal-gradient | `linear-gradient(160deg,#7B4BEE,#5A35DF)` | Celebration-moment background, one screen only. |
| 1p | photo-viewer-dark-surface | `#17103A` (as full-screen bg, not text color) | Only the immersive photo viewer inverts to a dark surface; not a dark-mode system (dark mode itself is an unimplemented settings toggle, see 2k). |
| 2j | reward-tile icon backgrounds | `#FBE0E6` / `#EEE8FF` / `#FDEFCF` / `#DCF4E8` | Per-reward-category tinting, cosmetic variety rather than a semantic status color — do not confuse with success/warning/danger surfaces despite overlapping hex values. |

## Explicit non-promotion note (RESOLVED)
`points-progress-fill` stays screen-local per PM decision (see `AMBIGUITY_AND_PM_REVIEW.md`, item 4). `#F8F7FD` chat-canvas variant was resolved by folding into the single `--color-canvas` token (item 1) \u2014 no alias created.
