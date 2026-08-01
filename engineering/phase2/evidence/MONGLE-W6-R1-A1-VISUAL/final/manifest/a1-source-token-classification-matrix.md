# A1 source-to-implementation matrix

Source: `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html`, screen `1a-1` / `로그인 폼`.

| Source order | Source element | Source text/value | Classification | React / CSS destination | Interaction | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | mock status bar | time, signal, Wi-Fi, battery | layout-literal | none | none | EXCLUDED_MOCK_CHROME |
| 2 | brand image | `family_platform_pin_logo_transparent_1024.png`, 150×150 | asset-reference | `AccountLoginView.logo` | none | IMPLEMENTED |
| 3 | brand halo | 120×7 radial gradient | screen-local-token | `logoHalo` | none | IMPLEMENTED |
| 4 | service heading | 가족 플랫폼 | typography-literal | `hero h1` | none | IMPLEMENTED |
| 5 | service description | 아이디로 로그인하고 우리 가족과 연결돼요 | typography-literal | `hero p` | none | IMPLEMENTED |
| 6 | sheet heading | 로그인 / family account helper | layout-literal | `heading` | none | IMPLEMENTED |
| 7 | account ID label and field | 아이디 / `seoyeon@ourfamily.com` / user icon | existing-component-token | `fieldGroup`, `field`, `PersonIcon` | local input | IMPLEMENTED |
| 8 | password label and field | 비밀번호 / lock / bullets / eye | existing-component-token | `passwordField`, `LockIcon`, `EyeIcon` | local password visibility | IMPLEMENTED |
| 9 | focused error state | purple focus border/ring and 2/5 error text | screen-local-token | `passwordField`, `error` | presentation-only | IMPLEMENTED |
| 10 | login persistence | 로그인 상태 유지 / selected rounded checkbox | existing-component-token | `rememberButton`, `checkbox` | local toggle | IMPLEMENTED |
| 11 | recovery action | 비밀번호 찾기 | existing-component-token | `textAction` | no-op | IMPLEMENTED |
| 12 | primary CTA | 로그인 | existing-component-token | `submit` | no-op submit | IMPLEMENTED |
| 13 | divider | 또는 | approved-one-off-literal | `divider` | none | IMPLEMENTED |
| 14 | profile action | 프로필 선택으로 돌아가기 / add-user icon | existing-component-token | `secondary`, `AddProfileIcon` | no-op | IMPLEMENTED |
| 15 | family notice | shield, approval title, administrator help | existing-component-token | `notice`, `ShieldIcon` | none | IMPLEMENTED |
| 16 | footer | v1.0.0 · 가족 플랫폼 / 관리자 로그인 › | typography-literal | `footer` | no-op admin action | IMPLEMENTED |
| 17 | mock home indicator | 132×5 black bar | layout-literal | none | none | EXCLUDED_MOCK_CHROME |

## Measured mapping indicators

- APP_CONTENT_SOURCE_ELEMENT_COUNT: 15
- APP_CONTENT_IMPLEMENTATION_ELEMENT_COUNT: 15
- UNMAPPED_APP_CONTENT_ELEMENT_COUNT: 0
- MISSING_CANONICAL_TEXT_COUNT: 0
- UNCLASSIFIED_VISUAL_VALUE_COUNT: 0
- UNDEFINED_TOKEN_COUNT: 0
- SEMANTIC_TOKEN_MISMATCH_COUNT: 0
- UNJUSTIFIED_GLOBAL_TOKEN_ADDITION_COUNT: 0

The imported frontend mascot is byte-identical to the approved archive asset: SHA-256 `dd5c48b3e670636b7822a5893e213ce8e99fd667b82b4cb53026e344bea4f0b8`; both files are 1024×1024 RGBA PNGs.
