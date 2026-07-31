# MONGLE_W6_SCREEN_SPEC_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 18. One block per A1-A5, synthesizing every prior
document in this set.

---

## A1 — Login / Profile / PIN

1. **Canonical route**: `/` (per `6.0B/CURRENT_SCREEN_ROUTE_MAP.md`)
2. **Mobile source**: `screen_login_approved.png` (Tier 1M) + `standalone-src.html` zones (Tier 3,
   `COMMITTED_DERIVED_EVIDENCE` only — file itself not present, see `D13`)
3. **Tablet source**: **`1a`/`1a-1` (프로필 선택 / ID·PW 로그인) have NO tablet variant** — confirmed by
   direct scan this session. `1j`(PIN입력)/`1j-1`(계정잠금)/`1u`(PIN변경)/`2s`(PIN최초설정)/`1r`(온보딩)/
   `2d`(비밀번호찾기) all have tablet coverage.
4. **Desktop source**: none
5. **Semantic zones**: profile-card grid (mobile) → **no tablet equivalent exists yet**; PIN keypad,
   lock-notice, onboarding steps → tablet-covered
6. **Preserved functions**: PIN-entry interaction confirmed via live spec code
   (`tests/e2e/specs/02-mission.spec.ts` `beforeEach`: player-card click → 4-digit PIN sequence → URL
   redirect) — this exact sequence must survive any Wave 6.1 rebuild
7. **Rebuild zones**: PIN/lock/onboarding sub-screens (tablet source exists to build from)
8. **Keep-as-is zones**: none frozen yet (A1 top-level screen has no tablet source at all)
9. **Remove presentation artifacts**: fake status bar, phone frame, home-indicator bar (mobile source,
   per `6.0A/ASSET_MANIFEST.md`) — confirmed forbidden regardless of which mobile HTML is authoritative
10. **Fixture boundary**: n/a (auth is real, API-backed per current route/auth architecture — not
    re-verified in depth this session, `NOT_REVERIFIED`)
11. **Asset dependency**: none new; brand logo only
12. **Token dependency**: brand-600, canvas, ink/text-primary (all `SOURCE_CONFLICT`-flagged, see Token
    Freeze), input focus-ring contract (already `FROZEN_COMPONENT_TOKEN`-equivalent per
    `COMPONENT_STYLE_CONTRACT.md` Input Field section, unchanged from prior sessions)
13. **Component dependency**: `Avatar` (profile cards), `Button` (currently 0 consumers — A1 is a
    plausible first real consumer for the login CTA)
14. **Responsive delta**: **`BLOCKED_BY_SOURCE`** for the top-level login/profile screen — no tablet
    layout evidence exists to freeze a delta from
15. **Loading/empty/error/permission**: `NOT_VERIFIED` this session
16. **Accessibility**: `NOT_VERIFIED` this session
17. **Screenshot viewport**: mobile 390×844 only for now (tablet blocked)
18. **Visual approval criteria**: PNG-match for mobile; tablet criteria `DEFERRED` until a tablet source
    exists for this specific screen
19. **Functional regression criteria**: PIN-entry sequence (item 6) must still pass once
    `docker-compose.phase0.yml`/`D12` is resolved or the newer suite gains equivalent coverage
20. **Hard Stop**: do not build a tablet A1 top-level screen from guesswork — no source exists
21. **Implementation readiness**: **`READY_FOR_MOBILE_ONLY`** for the top-level login/profile screen;
    **`READY_WITH_PM_DECISION`** for the PIN/lock/onboarding sub-screens (both viewports covered, `D9`
    for A1-S1's status still open)

---

## A2 — Family Home

1. **Canonical route**: `/family`
2. **Mobile source**: `screen_family_home_approved.png` (Tier 1M, MATERIAL delta already found per 6.0A)
3. **Tablet source**: `1b` 홈 — full coverage, both orientations, zone-mapped in depth this session
4. **Desktop source**: none
5. **Semantic zones**: nav, greeting header, hero promo card, recent-activity feed (+landscape-only
   embedded mission mini-widget), service tile grid (+6 landscape-only disabled tiles)
6. **Preserved functions**: **currently none to preserve** — `/family` is a 15-line stub per `6.0B`
   (`NOT_REVERIFIED` this session, carried as-is)
7. **Rebuild zones**: all of them — A2 is 0% implemented
8. **Keep-as-is zones**: none (nothing exists yet)
9. **Remove presentation artifacts**: same as A1
10. **Fixture boundary**: n/a — no implementation exists to have a fixture/real split yet
11. **Asset dependency**: **`ASSET_BLOCKED`** — hero illustration + service-tile icons are `SOURCE_MISSING`
    in both mobile and tablet sources (`D5`, re-confirmed this session); tablet's own A2 uses the same
    emoji/logo workaround, not a resolution
12. **Token dependency**: canvas, brand-600 (hero CTA), the landscape-only tile grid's disabled-state
    opacity (`.55`, one-off literal per mobile source's `ONE_OFF_LITERAL_REGISTER.md` precedent)
13. **Component dependency**: `Card` (single-consumer today — A2 could be its 2nd consumer, revisit
    promotion after), `Avatar`, a new mission-mini-widget component (landscape-only, `TABLET_ONLY_PRESENTATION`,
    not approved-mobile-confirmed)
14. **Responsive delta**: see Delta Matrix A2 rows — `NAVIGATION_RELOCATION`, `COLUMN_RECOMPOSITION`,
    2 `TABLET_ONLY_PRESENTATION` sub-zones needing PM confirmation before being treated as approved design
15. **Loading/empty/error/permission**: `NOT_VERIFIED` (no implementation exists)
16. **Accessibility**: n/a yet; when built, follow the `DoranLanding.tsx` pattern (Functional Deep Audit
    §D) as the reference standard, not the sparser UserDashboard/AdminDashboard style
17. **Screenshot viewport**: 390×844 (mobile, blocked on assets), 768×1024 + 1024×700 (tablet, same block)
18. **Visual approval criteria**: cannot be met until `D5` assets are sourced
19. **Functional regression criteria**: n/a (nothing to regress)
20. **Hard Stop**: **do not ship emoji as if it were the approved design** (explicit prohibition, both
    Section 17 of this task and `D5`'s own recommendation)
21. **Implementation readiness**: **`BLOCKED_BY_ASSET`** + **`BLOCKED_BY_FUNCTION`** (both axes, per
    `6.0AB`'s original classification, unchanged and now double-confirmed by the tablet source)

---

## A3 — Markpoint (포인트 잔치)

1. **Canonical route**: `/dashboard`
2. **Mobile source**: `screen_point_festival_approved.png` (Tier 1M, mostly low delta per 6.0A)
3. **Tablet source**: `1c` 포인트 잔치 — full coverage, zone-mapped in depth this session
4. **Desktop source**: none
5. **Semantic zones**: header (+landscape-only logout pill, `TABLET_ONLY_PRESENTATION`), player-summary
   card, cheer-messages card (**landscape-only presence** — absent in the portrait read, `VISIBILITY_CHANGE`
   not explained by any density rule), mission list (list↔grid recomposition), nav (**absent in
   landscape**, present in portrait — internal inconsistency, Delta Matrix Open Item 1)
6. **Preserved functions**: real, mature — `useDashboard.ts` (Functional Deep Audit §A): date navigation,
   3-tab UI, ranking toggle, config-driven cheer senders (with hardcoded 2-parent fallback), mission
   approval/proposal/feedback mutations, all AbortController-guarded
7. **Rebuild zones**: tablet-specific layout only (2-column landscape, 2-up-grid portrait mission tiles) —
   data layer needs zero change per the Functional Deep Audit's "zero responsive dependency" finding
8. **Keep-as-is zones**: all mutation/data logic in `useDashboard.ts`
9. **Remove presentation artifacts**: same as A1; tablet source itself has none for A3 (no fake chrome
   observed in either A3 orientation read this session)
10. **Fixture boundary**: n/a — real API throughout
11. **Asset dependency**: mission-icon emoji (same `D5` gap as A2, lower urgency since A3 already ships
    with emoji today, per `6.0A`'s framing that A3 has "legacy emoji debt" unlike A2)
12. **Token dependency**: brand-600/ink (`D2`/`D3`), mission-status-pill tone colors (already
    `FROZEN_SEMANTIC_TOKEN`-equivalent via success/warning/danger surfaces, unchanged)
13. **Component dependency**: mission-row component (currently screen-local per CLAUDE.md's
    `MissionList`/`MissionProgressBar`), needs a tile-mode variant for portrait tablet's 2-up grid —
    `REUSE_WITH_VARIANT`
14. **Responsive delta**: see Delta Matrix A3 rows; **2 open items require PM confirmation before
    implementation**: the landscape-only logout button and landscape-only cheer-messages card have no
    mobile precedent at all
15. **Loading/empty/error/permission**: loading = single boolean, **no distinct error-state UI**
    (Functional Deep Audit §A, `CONFIRMED_GAP`) — a tablet A3 error zone would be **new UI**, not
    preserved from mobile
16. **Accessibility**: sparse (Functional Deep Audit §D), not yet at the `DoranLanding.tsx` standard
17. **Screenshot viewport**: 390×844, 768×1024, 1024×700 — all sourced, ready to capture once built
18. **Visual approval criteria**: PNG match (mobile) + tablet-HTML match (tablet), pending resolution of
    the 2 open items in #14 (don't approve them as "matching design" without a PM nod)
19. **Functional regression criteria**: mutation flows in `useDashboard.ts` (item 6) must not regress;
    `02-mission.spec.ts`'s existence/visibility assertions are the nearest current automated check
    (currently non-runnable, `D12`)
20. **Hard Stop**: do not silently add the landscape-only logout/cheer-card zones as "confirmed design"
21. **Implementation readiness**: **`READY_WITH_PM_DECISION`** (function is ready now; 2 visual open
    items and the token `SOURCE_CONFLICT`s are the gating decisions, not missing evidence)

---

## A4 — Wagle GROUP (가족 대화)

1. **Canonical route**: `/wagle` (+ legacy `/naran/doran` → `/wagle` redirect, unchanged, non-negotiable
   per Doran contract)
2. **Mobile source**: `screen_family_chat_approved.png` (Tier 1M, lowest structural delta of the 5)
3. **Tablet source**: `1d` 대화 — full coverage, zone-mapped in depth this session
4. **Desktop source**: none dedicated, but current code already branches at `≥701px` (Functional Deep
   Audit §E) — useful corroborating data point for the breakpoint question, not itself authoritative
5. **Semantic zones**: room-list sidebar (landscape-only, 280px), message thread (bubble contract
   `FROZEN_COMPONENT_TOKEN`, 3-way agreement), composer, nav (**absent both orientations checked** — see
   Open Item 1, consistent at least internally for this one screen, unlike A3 where portrait keeps a dock)

   Correction on internal consistency: A4 landscape has no nav chrome (matches A3 landscape); A4 portrait
   **does** retain BottomDock per the zone read (see Delta Matrix `A4,nav` row: portrait = "BottomDock 4
   items") — so A4's inconsistency is the same shape as A3's (landscape drops nav, portrait keeps it), not
   a unique case.
6. **Preserved functions**: **the single most consequential item in this entire freeze** —
   `DoranLanding.tsx` is 100% fixture (Functional Deep Audit §E), zero live `doranApi` calls, compose
   always fails via a hardcoded timeout. The Doran service-code/API-path contract itself
   (`SERVICE_CODE="doran"`, `/api/families/{family_id}/doran`, `backend/app/domains/doran/**`) is
   explicitly non-negotiable and **out of this task's modification scope** regardless of visual outcome.
7. **Rebuild zones**: tablet layout (room-list pane, 2-column composition) — visual-only, since the data
   layer is fixture and stays fixture until Wave 7 (Doran REST) per Section 18's own instruction
8. **Keep-as-is zones**: the "exactly-once" auto-select guard (`didAutoSelectRef`), the
   `SERVICE`-kind-read-only rendering, the room `kind` taxonomy (GROUP/DIRECT/SERVICE) — all confirmed
   real, deliberate current behavior (Functional Deep Audit §E), not to be casually rewritten during a
   visual pass
9. **Remove presentation artifacts**: none observed specific to A4's tablet screens
10. **Fixture boundary**: **must be stated explicitly in any Wave 6.1 A4 deliverable**: `VISUAL_READY`
    achievable now; `FUNCTION_BACKEND_DEFERRED` (Doran REST is Wave 7) — never claim live backend
11. **Asset dependency**: none blocking (bubble/room-list assets are all inline SVG/CSS, no missing files)
12. **Token dependency**: `own`/`other`/`system` bubble colors — already `FROZEN_COMPONENT_TOKEN`
13. **Component dependency**: the 10 `platform/doran/components/*` — `REUSE_WITH_VARIANT`/`DEFER_PROMOTION`
    per Component Boundary Freeze; the tablet room-list pane is the "2nd surface" that would justify
    revisiting `RoomItem`'s domain-local status, but only once actually built in React (not from the
    design source alone)
14. **Responsive delta**: `NAVIGATION_RELOCATION` (room-list appears landscape-only), `SAME_COMPONENT_NEW_DENSITY`
    for bubbles/composer — see Delta Matrix A4 rows
15. **Loading/empty/error/permission**: `DoranLanding.tsx` already implements all 4 states explicitly
    (`disabled`/`loading`/`empty`/`error` via `EmptyState`/`LoadingState`/`ErrorState`) — **strongest
    state-coverage of any screen in this audit**, must be preserved verbatim in a tablet rebuild
16. **Accessibility**: **best-practice reference for the whole app** (Functional Deep Audit §D) —
    `aria-label`, `role="list"/"listitem"`, `aria-labelledby` all present and correct
17. **Screenshot viewport**: 390×844, 768×1024, 1024×700 — all sourced
18. **Visual approval criteria**: PNG + tablet-HTML match; D6 scope decision (GROUP-only vs. current
    3-kind fixture scope) must be made before finalizing what "matches" means
19. **Functional regression criteria**: **must explicitly state non-regression does NOT mean "backend
    works"** — the only regression risk is UI-mechanic (auto-select-once, read-only SERVICE rendering),
    not data correctness, since there is no real data path yet
20. **Hard Stop**: do not change the Doran API contract path or `SERVICE_CODE` value under any
    circumstance; do not present A4 as functionally complete once visually rebuilt
21. **Implementation readiness**: **`VISUAL_READY`** / **`FUNCTION_BACKEND_DEFERRED`** (explicit dual-axis
    classification per Section 22's A4-specific instruction)

---

## A5 — Admin Point (관리자 · 포인트 관리)

1. **Canonical route**: `/admin/*` (RBAC-protected via `AdminProtectedRoute`/`get_current_admin`)
2. **Mobile source**: `screen_admin_point_approved.png` (Tier 1M, best overall match of the 5)
3. **Tablet source**: `1e` 포인트관리 — full coverage, zone-mapped in depth this session (landscape only;
   portrait not read this session, `NOT_VERIFIED`)
4. **Desktop source**: the mobile-labeled A5 PNG is itself desktop-shaped (1448×1086, near-match aspect
   per 6.0A) — A5 is unique among A1-A5 in already having a desktop-like Tier 1M source
5. **Semantic zones**: near-white icon rail (80px, 3 destinations), toolbar (CSV 내보내기/포인트 지급/차감
   추가), 4-card stat grid (3 neutral + 1 amber callout), filter chips + search, **5-column data table**
   with sticky header and inline 승인/반려 action pills on pending rows
6. **Preserved functions**: real, mature, **already exceeds the approved source** —
   `useAdminData.ts`/`approveMission`/`rejectMission` (Functional Deep Audit §B) are working, toast-backed,
   reload-on-success. Also newly documented: an undocumented `POST /api/mission-templates/generate`
   Lazy-Init side-effect fires on every mount — must not be silently dropped by a tablet rebuild.
7. **Rebuild zones**: the transaction-list presentation specifically — current code uses a card-list
   pattern (per CLAUDE.md's `P-HOTFIX-ADMIN-VIEWS-002` history, `.deductionCard`), tablet source shows a
   real grid data table. This is a **visual rework**, not a data-layer change (Component Boundary Freeze:
   flagged `RECOMPOSE` as likely a new `AdminDataTable` component)
8. **Keep-as-is zones**: all mutation logic, RBAC route guard, cycle-range data loading
9. **Remove presentation artifacts**: n/a specific to A5
10. **Fixture boundary**: n/a — fully real
11. **Asset dependency**: none blocking
12. **Token dependency**: **`D8` (sidebar tone) is A5's single biggest open item** — now evidenced by 2
    independent sources (approved PNG + tablet HTML, both near-white) against current code's dark sidebar
13. **Component dependency**: `AdminSidebar`-equivalent (`RECOMPOSE` pending `D8`), `StatCard`
    (`REUSE_WITH_VARIANT`, needs tone-prop check), new `AdminDataTable` (`RECOMPOSE`)
14. **Responsive delta**: `SAME_COMPONENT_NEW_WIDTH` (sidebar), `COLUMN_RECOMPOSITION` (table) — directly
    confirms the task prompt's own general claim ("Admin screens become real data tables at tablet width")
    for this specific screen, evidenced not assumed
15. **Loading/empty/error/permission**: loading = boolean in `useAdminData`; RBAC enforced at route level,
    not re-checked client-side in the hook (trusts the guard) — `EVIDENCE_BACKED`
16. **Accessibility**: not evaluated in the 3 AdminDashboard files read this session beyond the sparse
    6/74-file finding in Functional Deep Audit §D — `NOT_VERIFIED` at the A5-specific level
17. **Screenshot viewport**: 390×844, 1024×700 (landscape only sourced this session), 1440×900
18. **Visual approval criteria**: must not silently repaint Admin to light theme as a side effect of A5
    work — `D8` needs its own explicit sign-off per the task prompt's own instruction, not bundled
19. **Functional regression criteria**: `approveMission`/`rejectMission`/toast/reload flow (item 6) and
    the Lazy-Init template-generation call must both survive
20. **Hard Stop**: **do not delete the current edit/delete/approve/reject functionality because the
    visual source shows something simpler** — current code is already ahead of the approved source here,
    per the task prompt's own explicit A5 instruction
21. **Implementation readiness**: **`READY_WITH_PM_DECISION`** (function is more than ready; `D8` is the
    sole real gate, table-recompose is a design task not a decision gate)

---

## Closeout Update (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정) — final per-screen readiness

All open items D1-D15 referenced by the per-screen blocks above are now individually resolved (see
`MONGLE_W6_PM_DECISION_REGISTER.md` "PM Closeout Final Resolution"). Final readiness supersedes each
block's own item 21 as follows:

| Screen | Prior readiness (this document, above) | **Final readiness (closeout)** | Basis |
|---|---|---|---|
| **A1** | `READY_FOR_MOBILE_ONLY` (top-level) / `READY_WITH_PM_DECISION` (PIN/lock/onboarding sub-screens) | **`A1 = MOBILE_ONLY_FIRST`**, no tablet layout invented for the top-level login/profile screen (`D9`: `RESOLVED_BY_SEQUENCE_ADJUSTMENT`). Sub-screens with tablet coverage remain ready; the top-level screen stays mobile-only until a real tablet source exists. | `D9`, Implementation Sequence Freeze closeout |
| **A2** | `BLOCKED_BY_ASSET` + `BLOCKED_BY_FUNCTION` | **`A2 = BLOCKED_BY_ASSET` + `BLOCKED_BY_FUNCTION`, unchanged.** `D5` is now `LOCALIZED_BLOCKER` (A2 primary) — still a real, disclosed block on this screen specifically; sourcing delegated to `MONGLE-W6-ASSET-SOURCING-001`. | `D5` |
| **A3** | `READY_WITH_PM_DECISION` | **`A3 = READY_FOR_FIRST_MOBILE_TABLET_PAIR`.** Both open zones (landscape-only logout pill, landscape-only cheer-messages card) are now covered by `D15`'s nav/tablet-presentation resolution framework and no longer block "ready" status; token dependencies (`D2`/`D3`) are `PM_RESOLVED`. A3 is confirmed as the **first mobile+tablet pattern-setting pair** (Implementation Sequence Freeze closeout), superseding the original prompt's A1-first assumption per this document's own prior recommendation. | `D2`, `D3`, `D15`, Implementation Sequence Freeze closeout |
| **A4** | `VISUAL_READY` / `FUNCTION_BACKEND_DEFERRED` | **`A4 = VISUAL_READY` + `FUNCTION_BACKEND_DEFERRED` + GROUP-only scope (`D6`: `PM_RESOLVED`).** Visual work (tablet room-list pane, 2-column composition) may proceed on the GROUP-kind room only; DIRECT/SERVICE remain out of scope for Wave 6. Doran REST integration remains Wave 7, unchanged — never to be reported as functionally complete. | `D6` |
| **A5** | `READY_WITH_PM_DECISION` | **`A5 = READY_FOR_IMPLEMENTATION`.** `D8` is `PM_RESOLVED` (bright `#FBFAFE` sidebar) — the sole real gate this document's own item 21 named is now closed. Existing edit/delete/approve/reject functionality, RBAC guard, and the Lazy-Init template-generation call **must be preserved** exactly as this document's items 6-8/19-20 already specified — closeout does not relax any of those. | `D8` |

No screen's Hard Stop clause (item 20 in each block above) is weakened by this closeout — A2's
no-emoji-as-approved-design prohibition, A4's Doran-contract-untouched prohibition, and A5's
no-functionality-deletion prohibition all remain in force verbatim.
