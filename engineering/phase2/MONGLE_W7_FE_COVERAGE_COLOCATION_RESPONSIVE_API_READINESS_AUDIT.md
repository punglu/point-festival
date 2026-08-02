# MONGLE-W7-FE-COVERAGE-COLOCATION-RESPONSIVE-API-READINESS-AUDIT-001

## Verdict

`MONGLE_W7_FE_COVERAGE_COLOCATION_RESPONSIVE_API_AUDIT_CONDITIONAL`

Read-only audit observed on 2026-08-02 (Asia/Seoul). Coverage, code structure,
runtime routes, responsive risk, and API availability are measured sufficiently
for planning. The verdict is conditional because the tablet result is a
code/runtime structural finding, not a visual acceptance of every screen.

## Baseline and authority

| Item | Measured value |
| --- | --- |
| Worktree / branch / HEAD | `/Users/mac/mac_Project/mongle_ui` / `dev-newmarkp` / `3294c902a88a846d75e0896741784f75aa827fbe` |
| Dirty before audit | 223 paths: 2 modified, 221 untracked, 0 deleted |
| Product changes by audit | 0; this report is the only audit output |
| Tokenized source | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현-tokenized.html` SHA-256 `1d11874d0bceb227b5cecd81bdb8954fd3d620818292f9b608300aa925da5327` |
| Structural reference | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html` SHA-256 `d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9` |
| Style guide | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/family_platform_style_guide_v1.png`, preview PNG, and `assets/design-system/APPROVED_VISUAL_STYLE_GUIDE.html` |
| Code authority | `frontend/src/App.tsx`; current preview route registry |

The source has 49 labelled screens under 45 wrapper IDs. Seven labels belong
to six deliberately removed wrappers. `1y` contains three screens under one
ID; `2d` contains two. Those are authority conflicts, not inferred routes.

`MONGLE_W6_TOKENIZED_SCREEN_INVENTORY.md` is **STALE_DOCUMENT** for several
preview-route entries: current code now has routes it lists as `—`. It also
maps both `1a` and `1a-1` to `/login`, while code marks only `1a-1`.

## A. Coverage matrix

| Measure | Count |
| --- | ---: |
| Source screen labels including removed variants | 49 |
| Eligible non-removed source labels | 42 |
| Unique eligible canonical IDs | 39 |
| Code-confirmed canonical pages (`data-canonical-screen-id`) | 36 |
| Detached preview routes | 35 |
| `/login` canonical route | 1 (`1a-1`) |
| Candidate active product mapping without canonical marker | 1 (`1a` → `/`) |
| Tokenized but not code-confirmed | 1 (`1a`) |
| PNG-only | 0 found |
| Authority-conflict source screens | 5 (`1y` three, `2d` two) |
| Duplicate canonical IDs | 2 (`1y`, `2d`) |
| Missing source | 0 |
| Approved PNG files found by naming pattern | 5 |

### Per-status coverage

| Status | IDs / source screens | Evidence |
| --- | --- | --- |
| IMPLEMENTED_ROUTE | `1a-1`, `1b`, `1c`, `1d`, `1e`, `1f`, `1g`, `1h`, `1i`, `1j`, `1j-1`, `1k`, `1l`, `1m`, `1n`, `1o`, `1p`, `1q`, `1r`, `1s`, `1t`, `1u`, `1v`, `1w`, `1x`, `1z`, `2a`, `2b`, `2c`, `2e`, `2f`, `2g`, `2h`, `2i`, `2j`, `2k` | 35 `/__wave6/*` routes plus `/login`; current preview smoke: 35/35 HTTP 200. |
| UNKNOWN | `1a` 로그인 | `/` renders `AuthPage`, but it has no canonical marker and no explicit source mapping. |
| AUTHORITY_CONFLICT | `1y`: 네트워크 오류/알림 없음/검색 결과 없음; `2d`: 비밀번호 찾기/이메일 인증 | One ID represents multiple distinct screens. |
| NOT_IN_SCOPE_REMOVED | `1z0`…`1z5` removed variants | Source explicitly hides/removes them; no implementation inferred. |

All current `*Preview/index.tsx` files and `A1AccountLogin/index.tsx` were
statically checked for `fetch`, axios, API client, storage, WebSocket/SSE,
product-navigation, and service imports: 0 matches.

## B. Simple colocation matrix

| Classification | Count | Evidence |
| --- | ---: | --- |
| COLOCATION_COMPLIANT | 35 | Every canonical page directory has `index.tsx` and one local CSS module; no page-to-page imports were found. |
| MINOR_REORGANIZATION | 0 | — |
| STRUCTURAL_REORGANIZATION | 1 | `FamilyHomePreview` has routed `index.tsx` plus a second `standalone.tsx` source entry. |
| UNKNOWN | 0 | — |

Legacy `UserDashboard` and wildcard `AdminDashboard` are product aggregates,
not canonical preview ports. They need a separate route-to-screen mapping
before applying the one-route/one-page-directory test.

## C. Mobile/tablet responsive matrix

### Measured facts

- 35/35 preview URLs returned HTTP 200. Representative current browser samples
  loaded Noto Sans KR (`document.fonts.status = loaded`), with 0 blocking
  console errors and 0 preview API requests.
- At 390×844, sampled mobile routes had no horizontal document overflow.
  `1c` (979px), `1d` (940px), `1f` (922px), `1h` (1124px), and `1i` (966px)
  are vertically scrollable. This audit records them as screen-specific
  dock/scroll review candidates, not automatic clipping failures.
- At 768×1024, sampled mobile roots expanded to 768px. Only
  `FamilyHomePreview.module.css` has an `@media` rule; 34 of 35 preview CSS
  modules have none. The source canonical mobile canvas is 480px.
- Desktop-primary source screens are `1e`, `1m`, `1v`, `1z`, `2a`, `2e`, and
  `2i` (1440×1030 source canvas). At 1448×1086 all seven rendered as
  1448×1086 roots, HTTP 200, loaded font, 0 console errors, 0 preview API.

| Classification | Count | Screen set |
| --- | ---: | --- |
| MOBILE_PASS (structural smoke only) | 28 | Mobile detached previews; this is not visual acceptance. |
| TABLET_PASS | 1 | `1b`, the only preview with an explicit responsive rule. |
| TABLET_MINOR_FIX | 0 | No evidence supports calling any missing tablet contract minor. |
| TABLET_LAYOUT_REQUIRED | 27 | Remaining mobile previews: no explicit tablet rule; mobile one-column layout expands to tablet width. |
| RESPONSIVE_NOT_APPLICABLE | 7 | Desktop-primary `1e`, `1m`, `1v`, `1z`, `2a`, `2e`, `2i`. |

## D. Font/global-layout findings

| Finding | Classification | Evidence |
| --- | --- | --- |
| Noto Sans KR runtime loading | GLOBAL_FONT: no failure observed | Browser samples reported `loaded`; global fallback begins with Noto Sans KR. |
| 400/500/600/700/800/900 exact usage | NOT_VERIFIED per-screen | Existing evidence explicitly checks 400/500/700/900; unused weights are not called missing. |
| Reset baseline | correct | `border-box` universal reset; images use `max-width:100%`. |
| Root horizontal masking | GLOBAL_ROOT_LAYOUT finding | `html, body, #root` apply `max-width:100vw; overflow-x:hidden`; fixed-width desktop children can be concealed instead of responsive. |
| Vertical/dock behavior | PAGE_LAYOUT | Preview pages own their `min-height:100dvh`, flex, overflow, and dock rules. |

Counts: global font failures observed **0**; root/global layout findings **1**;
page-local layout findings **28** (27 tablet contracts plus duplicate 1b source).

## E. Shared-component candidate matrix

| Candidate | Consumers | Disposition | Reason |
| --- | ---: | --- | --- |
| Bottom dock | 9 previews + legacy dashboard | SHARE_AFTER_RESPONSIVE | Appearance repeats; active/navigation contract differs. |
| Admin sidebar | 1e preview + legacy AdminDashboard | SHARE_AFTER_RESPONSIVE | Visual authority and route behavior differ. |
| Avatar | 10+ | SHARE_AFTER_WIRING | Asset/presence semantics differ. |
| Status chip | 10+ | SHARE_AFTER_WIRING | Status taxonomy differs. |
| Form field | A1/PIN/password/schedule flows | SHARE_AFTER_WIRING | Interaction and validation are not wired. |
| Table shell/pagination | 1e, 1m, 2a, 2e, 2i + legacy admin | KEEP_PAGE_LOCAL | Columns/actions/data contracts differ. |
| Empty/error state | list previews / unresolved 1y | KEEP_PAGE_LOCAL | `1y` has an authority conflict. |
| Back/page header | 15+ | FALSE_SIMILARITY | Copy, controls, and dock relation differ. |
| Section card | 20+ | FALSE_SIMILARITY | Only surface appearance repeats. |

Counts: READY_TO_SHARE **0**; SHARE_AFTER_RESPONSIVE **2**;
SHARE_AFTER_WIRING **3**; KEEP_PAGE_LOCAL **2**; FALSE_SIMILARITY **2**.

## F. Screen-to-API readiness matrix

Live OpenAPI (`http://localhost:18001/openapi.json`) returned 200. No mutating
probe was performed. Preview pages intentionally consume none of these APIs.

| Domain / related screens | Existing code/OpenAPI evidence | Status | Gap |
| --- | --- | --- | --- |
| Account/Auth (`1a`, `1a-1`, `1j`, `1j-1`, `1u`, `2d`) | `/api/auth/*`, account login/refresh/logout, `/api/me`, sessions/devices; active Auth client exists | API_READY | `1a` mapping and `2d` collision remain. |
| Family/Membership (`1q`, `1v`, onboarding) | family, member, role, service, account-context paths | API_READY | Role/view-model mapping required. |
| Profile (`1f`) | `/api/me`, players, level tiers | API_PARTIAL | Preference/avatar update contract unverified. |
| Home (`1b`, `2i`) | daily point, cheer, weekly mission, Markpoint summaries | ADAPTER_REQUIRED | No aggregate frontend view-model adapter. |
| Mission (`1k`, `1m`, `1s`, `2e`, `2f`) | mission/template/admin/Markpoint lifecycle paths | API_READY | DTO/role mapping remains. |
| Todo (`1i`) | no dedicated todo router/path | API_MISSING | Product contract required. |
| Point (`1c`, `1e`, `1l`, `2h`) | Markpoint balance, ledger, missions, deductions, config/templates | API_READY | Adapter/ownership mapping required. |
| Reward (`1l`, `2j`) | no reward/catalog/exchange path | API_MISSING | Product API required. |
| Schedule (`1g`, `1o`) | no schedule/calendar router/path | API_MISSING | Domain/API required. |
| Album/Photo (`1h`, `1p`, `1w`, `2b`) | no album/photo/upload router/path | API_MISSING | Media storage/upload/authorization required. |
| Notification (`1n`) | notification + admin notification paths | API_READY | Frontend adapter/read-state behavior required. |
| Conversation (`1d`, `1t`, `2g`) | chat plus Wagle room/message/read-state/realtime paths | API_READY | Deferred Wagle policies constrain wiring. |
| Admin (`1e`, `1m`, `1v`, `1z`, `2a`, `2e`, `2i`) | admin player/mission/deduction/point/feedback/config/summary paths | ADAPTER_REQUIRED | Canonical DTO and privilege mapping absent from previews. |

Counts: API_READY **6**; ADAPTER_REQUIRED **2**; API_PARTIAL **1**;
API_MISSING **4**; POLICY_REQUIRED **0**; STATIC_ONLY **0**; NOT_VERIFIED **0**.

## G. Objective dependencies

| PREREQUISITE | BLOCKS | DOES_NOT_BLOCK |
| --- | --- | --- |
| Resolve `1y`/`2d` duplicate IDs | Routes and API mapping for five screens | Existing routed previews |
| Tablet layout contract per mobile family | Tablet acceptance; safe shell/dock extraction | Mobile route smoke |
| Schedule, Album/Photo/upload, Todo, Reward API contracts | Real-data wiring for those families | Static previews |
| Family/member context and role adapter | Home/admin/family binding | Page-local visual ports |
| Wagle D6-P1…P8 policy decisions | Messaging interaction/realtime wiring | Static chat preview |
| Explicit `1a` marker mapping | Exact coverage accounting | `/login` `1a-1` preview |

## Validation and limits

| Check | Result |
| --- | --- |
| `npm run lint` | PASS |
| `npm run build` (`tsc -b && vite build`) | PASS; 343 modules transformed |
| `git diff --check` | PASS |
| Runtime | db, backend, frontend healthy |
| Active route smoke | `/`, `/login`, `/dashboard`, `/admin/points`: HTTP 200 |
| Preview route smoke | 35/35 HTTP 200 |
| Product source changed by audit | 0 |
| Commit / push | 0 / 0 |

Not verified: tablet visual fidelity for every route, exact per-screen font
weight use, real-data length behavior, and authenticated/mutating API outcomes.

