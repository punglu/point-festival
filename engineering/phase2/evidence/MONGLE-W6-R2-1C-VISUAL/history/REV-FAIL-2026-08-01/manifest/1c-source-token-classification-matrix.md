# 1c source-to-implementation matrix

Structural source: `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html`, `#1c` / `data-screen-label="포인트 잔치"`.

| Source order | Zone | Element / text | Asset or visual value | Classification | React / CSS destination | Interaction | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | device | status bar and device chrome | time, radios, home indicator | layout-literal | none | none | EXCLUDED_MOCK_CHROME |
| 2 | header | pin logo, `포인트 잔치`, helper, logout | approved pin PNG, 96px image | asset-reference | `PointFestivalPreview.header` | logout no-op | IMPLEMENTED |
| 3 | profile | 서연, Lv.3, 320P/500P, 64% level bar | gradient profile card | screen-local-token | `profileCard` | none | IMPLEMENTED |
| 4 | metrics | 오늘 획득 / 남은 미션 / 현재 보유 | 3-column stat panel | layout-literal | `metrics` | none | IMPLEMENTED |
| 5 | week | `7월 3주차`, 월–일 20–26 | selected 22 circle | existing-component-token | `weekCard` | local selected-day state | IMPLEMENTED |
| 6 | cheer | 가족 응원 메시지, 엄마/아빠 cards | initial-color avatars | approved-one-off-literal | `cheerSection` | none | IMPLEMENTED |
| 7 | missions | 방 청소하기 / 숙제 다 하기 / 동생과 사이좋게 | emoji, progress, reward, status | screen-local-token | `missionSection` | presentation-only row no-op | IMPLEMENTED |
| 8 | history | 포인트 사용 내역 / 문구점에서 노트 구입 / −30P | signed amount, no progress bar | screen-local-token | `historyRow` | no-op | IMPLEMENTED |
| 9 | dock | 홈 / 포인트 잔치 / 대화 / 나 | outline SVG, point active | existing-component-token | `bottomDock` | no-op | IMPLEMENTED |
| 10 | gallery | `1c` badge and board label | gallery-only metadata | layout-literal | none | none | EXCLUDED_GALLERY_ONLY |

## Required indicators

- APP_CONTENT_SOURCE_ELEMENT_COUNT: 8
- APP_CONTENT_IMPLEMENTATION_ELEMENT_COUNT: 8
- UNMAPPED_APP_CONTENT_ELEMENT_COUNT: 0
- MISSING_CANONICAL_TEXT_COUNT: 0
- UNCLASSIFIED_VISUAL_VALUE_COUNT: 0
- UNDEFINED_TOKEN_COUNT: 0
- SEMANTIC_TOKEN_MISMATCH_COUNT: 0
- UNJUSTIFIED_GLOBAL_TOKEN_ADDITION_COUNT: 0
