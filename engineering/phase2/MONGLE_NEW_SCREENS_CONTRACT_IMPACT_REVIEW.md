# New-Screen (0a–0g) and Logo Kit Contract Impact Review

> **Status vocabulary superseded by the approved Decision Freeze (2026-08-01).**
> D1–D8 are now `APPROVED` / `FROZEN` and are **not** reopened by this review.
> Every `PM_DECISION_REQUIRED` marker below is to be read as
> `DEFERRED_TO_RELEVANT_TASK_START_GATE` for **screen-level and API-level detail
> the frozen decisions do not cover** — for example the additional optional
> signup surfaces in 0b, discovery privacy in 0g, membership state-machine edge
> cases, and the wordmark asset approval. It is never a claim that the
> underlying D1–D8 decision is still open. Current task-level status lives in
> `MONGLE_IMPLEMENTATION_BACKLOG.md`, and the reconciled reading of this
> review's D1–D7 implications is in the Decision Freeze's own 0a–0g addendum.

**Status:** `READY_FOR_PM_TARGET_DECISION_REVIEW_WITH_NEW_SCREEN_EVIDENCE`
**Kind:** Documentation-only impact review. Not a product-code, test, DB, or
migration task. Does not touch `agent-system/` shared files.
**Baseline this review folds into:** `MONGLE_TARGET_DECISION_FREEZE.md` (Target
Decision SSOT) and `MONGLE_TARGET_DECISION_PACKAGE_RECONCILIATION_REPORT.md`
(`READY_FOR_PM_TARGET_DECISION_REVIEW`, Gates 1–5 PASS, unchanged by this
review).

## 0. Purpose and boundary

`docs/temp/logo and additional pages/` added 9 new pre-login/pre-group screens
and a Mongle wordmark/monogram/app-icon asset kit. This review reads that
source against the current Target Decision Package and records what it
implies for D1–D8, the domain boundary map, the backlog, and the test matrix.
It does not decide anything, does not write product code, and does not
re-open DATA-A or the architecture reconciliation — both are treated as
complete per their own terminal status (`MONGLE_TARGET_DECISION_PACKAGE_RECONCILIATION_REPORT.md`
Gate 5, `da7ea74` merge). All new-screen-derived rows below stay
`PM_DECISION_REQUIRED`, matching the existing convention in every document
this review amends.

## 1. Input sources

- `docs/temp/logo and additional pages/신규화면-적용가이드라인.md` — flow order and token-reuse rule.
- `docs/temp/logo and additional pages/가족 플랫폼 신규화면 (Standalone).html` — bundler artifact; only the embedded static markup (9 `<div id="0a">`…`<div id="0g">` blocks) was read as screen reference. The artifact's own unpacking/runtime code is not product source and is not referenced further.
- `docs/temp/logo and additional pages/mongle_logo_kit_v1/` (`README.md`, `manifest.json`, `mongle-logo.css`, `MONGLE_LOGO_GUIDE.html`, `assets/`, `reference/`).
- Current repository state used for comparison: `frontend/src/styles/global.css` (Wave 6.1 token freeze), `frontend/src/pages/Auth/*` (legacy PIN/PlayerSelect login), `frontend/src/shared/components/MainLogo/`, `frontend/src/pages/AdminDashboard/components/AdminBrandLogo/`.

## 2. Screen-by-screen Contract Impact Matrix

### 2a. Overview, actor, route candidates

| Screen | Name | Product purpose | Primary actor | Precondition | Entry (candidate) | Exit (candidate) |
|---|---|---|---|---|---|---|
| 0a | 온보딩 1/3 | pre-login product intro | anonymous visitor | none | app cold start | "시작하기"/"건너뛰기" → 0a-2, or "로그인" → existing legacy Auth screen |
| 0a-2 | 온보딩 2/3 | role/point concept intro | anonymous visitor | 0a seen or skipped | 0a | 0a-3 |
| 0a-3 | 온보딩 3/3 | record/album concept intro, CTA | anonymous visitor | 0a-2 seen or skipped | 0a-2 | "시작하기" → 0b; "로그인" → existing legacy Auth screen |
| 0b | 회원가입 | account creation intake | anonymous visitor | none (direct nav also possible) | 0a-3 or app "회원가입" entry | success → 0c (screen defines no group-owned/no-group branch itself — see 2c gap) |
| 0c | 그룹 없음 (선택 허브) | post-signup group entry hub | authenticated, no group | signup success AND no group membership | 0b success; login success with no group | 0d, 0e (via card), "나중에 하기" (destination undefined — guideline marks this `미정`) |
| 0d | 그룹 만들기 | create new group | authenticated, no group | 0c reached | 0c "가족 그룹 만들기" | success → existing home, creator is admin |
| 0e | 초대 코드로 참여 | join by invite code | authenticated, no group | code in hand | 0c card, 0g "코드 직접 입력", 0f "다른 가족 코드 입력" | submit → 0f |
| 0f | 승인 대기 | await group-admin approval | join applicant | 0e submitted, or 0g request sent | 0e, 0g | approved → existing home; cancelled → 0c |
| 0g | 그룹 둘러보기 | discover/search joinable groups | authenticated, no group | **no explicit entry point exists on 0c itself** (see gap below) | undefined | "참여 요청" → 0f; "코드 입력" → 0e; "새로 만들기" → 0d |

**Gap, PM-reviewed 2026-07-31 — status recorded, not yet actionable:** the
guideline's flow diagram routes 0c → 0g, but the actual 0c markup contains
only two action cards ("가족 그룹 만들기", "초대 코드로 참여하기") plus
"나중에 하기" — no "그룹 둘러보기" entry point. This is a confirmed real gap,
not an implementer's misreading.

PM recommendation (direction, not yet an approved decision): add a "그룹
둘러보기" entry card or secondary CTA to 0c, keep 0g as-is — rather than
removing 0g — because 0g already exists as a built screen, a no-group user
needs a discovery path, it covers users without a code, and it preserves
more of the existing screen asset/flow than deleting 0g would. This
recommendation does not authorize implementation; it is scoped by the
following decisions, all still open:

- **D1** — how far group discovery may be exposed (public directory vs.
  invite-only vs. contact-scoped).
- **D3** — what a no-group Session is permitted to see/do, which determines
  whether an unauthenticated-of-group user may browse a discovery list at
  all.
- **D4** — who may expose or approve entry into a group via discovery.
- **D7** — the discovery Route/API contract itself.

Status of record:

```text
0g SCREEN:              VALID_TARGET_REFERENCE
0c -> 0g ENTRY PATH:    PM_DECISION_REQUIRED
IMPLEMENTER-ADDED CTA:  PROHIBITED — do not add a 0c entry card
                        unilaterally; wait for D1/D3/D4/D7.
```

### 2b. State model per screen

| Screen | Auth state | Session state | Group context state | Membership state | Loading | Empty | Failure | Pending |
|---|---|---|---|---|---|---|---|---|
| 0a/0a-2/0a-3 | UNAUTHENTICATED | NONE | N/A | N/A | N/A (static) | N/A | N/A | N/A |
| 0b | UNAUTHENTICATED → (success) AUTHENTICATED | NONE → CREATED | NONE | NONE | not defined in markup | N/A | **not defined** (duplicate email/phone, verification failure, terms not accepted — no failure state exists in the mockup) | phone/email verification pending — **not defined** |
| 0c | AUTHENTICATED | ACTIVE_NO_GROUP | NONE | NONE | N/A | screen default IS the empty state ("아직 소속된 가족 그룹이 없어요") | N/A | N/A |
| 0d | AUTHENTICATED | ACTIVE_NO_GROUP → ACTIVE_WITH_GROUP | NONE → NEW | NONE → ACTIVE (creator role) | not defined | N/A | duplicate group name — **not defined in markup** | N/A |
| 0e | AUTHENTICATED | ACTIVE_NO_GROUP | NONE (preview only, not yet joined) | NONE → PENDING (on submit) | code-complete auto-lookup loading — **not defined** | N/A | **not defined** — screen shows only the success ("확인됨") state; invalid code, expired code, already-a-member all have no markup | transitions to 0f on submit |
| 0f | AUTHENTICATED | ACTIVE_NO_GROUP | target group referenced, inactive | PENDING | N/A | N/A | rejected-state screen — **not defined** | screen itself is the PENDING-state UI |
| 0g | AUTHENTICATED | ACTIVE_NO_GROUP | NONE | NONE → PENDING (on request) | search-result loading — **not defined** | no-result state — **not defined** | N/A | N/A |

### 2c. Contract linkage

| Screen | Related PM decision(s) | Related epic | Related vertical slice task | Required target-test tag | Implementation status |
|---|---|---|---|---|---|
| 0a/0a-2/0a-3 | D2 (로그인 링크의 목적지), D7 (route) | E1 | `MONGLE-W1-ONBOARDING-INTRO-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED |
| 0b | D2 (credential types v1 scope), D7 | E1 | `MONGLE-W1-ACCOUNT-SIGNUP-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED |
| 0c | D1 (Group existence is the branch condition itself), D3 (No-Group Session contract), D7 (제한 모드 홈 route) | E1 | `MONGLE-W1-GROUP-SELECTION-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED |
| 0d | D1 (group physical model), D4 (creator→admin role binding) | E1 | `MONGLE-W1-GROUP-CREATION-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED |
| 0e | D4 (who may issue/validate a code), D7 (validate-code API contract) | E1 | `MONGLE-W1-GROUP-CODE-JOIN-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED |
| 0f | D4 (approval authority), Membership lifecycle (§4) | E1 | `MONGLE-W1-MEMBERSHIP-PENDING-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED |
| 0g | D1 (is group discovery a public directory — privacy implication), D3 (no-group Session browse permission), D4 (who exposes/approves discovery entry), D7 (0c→0g route contract) | E1 | `MONGLE-W1-GROUP-DISCOVERY-UI-001` | TARGET_PRODUCT | PM_DECISION_REQUIRED — screen itself `VALID_TARGET_REFERENCE`, 0c entry path `PM_DECISION_REQUIRED` |

**Accessibility, recorded once for all 9 screens rather than per-row:** the
source renders back/skip affordances as bare glyphs (`‹`, `›`) with no visible
accessible-name pattern, the invite-code entry as styled `<div>`s rather than
real input semantics, and the "전체 동의"/약관 checkboxes as styled `<span>`s
rather than real checkbox controls. None of this is copied into product code
by this review; it is a requirement each vertical slice task must satisfy
per the Frontend Guide's accessibility gate, not a property of the mockup.

## 3. PM decision impact (evidence only, no decision made)

This section adds evidence to existing rows in `MONGLE_TARGET_DECISION_FREEZE.md`.
It does not change any decision's status; every row there stays
`PM_DECISION_REQUIRED`.

- **D1 (Group semantics):** the new screens exclusively show "가족 그룹"
  (family group) — they are evidence that v1 UI copy is family-framed, not
  evidence that the platform must be permanently family-only. 0g's group
  "둘러보기"/검색 surface additionally raises a privacy question D1 did not
  previously carry: is a joinable-group list a public/contact-scoped
  directory, or invite-only discovery? This needs its own sub-answer under D1
  before 0g can be built.
- **D2 (Account credential / managed account):** 0b's markup exposes four
  concrete signup affordances — email+password, phone+SMS verification,
  Google, Apple — plus a required combined terms/privacy consent step. Per
  the existing D2 decision framing, exposure in the mockup is not automatic
  v1 approval of all four; each needs its own `V1_REQUIRED` /
  `V1_OPTIONAL` / `DEFERRED` / `REFERENCE_ONLY` classification under D2 before
  `MONGLE-W1-ACCOUNT-SIGNUP-UI-001` can start.
- **D3 (Session / active context):** the 0b→0c split makes explicit that
  Session creation and Group-context selection are two separate moments
  (an authenticated account can exist with zero groups). This is concrete UI
  evidence for the "No-Group Session" state D3 already anticipates, plus a
  new candidate state this source surfaces: a **pending-membership session
  context** (0f), where the account is authenticated, has zero *active*
  memberships, but has exactly one *pending* one.
- **D4 (Scoped RBAC):** 0d lets the creator pick "부모 (관리자)" or "자녀" as
  their own role at group-creation time. A creator who self-selects "자녀"
  and still becomes the group's only member is a role/authority edge case
  the current D4 framing does not cover and needs an explicit answer.
  0e/0f/0g additionally require deciding who may issue an invite code and who
  is the approval authority for a join request (not necessarily the same
  actor).
- **D7 (Route / API scope):** none of the following exist yet as approved
  route or API surface and must not be treated as decided by this review:
  `/onboarding/*`, `/signup`, `/groups`, `/groups/new`, `/groups/join`,
  `/groups/discover`, `/groups/pending`; account signup, external-identity
  signup, phone/email verification, list-available-memberships, create-group,
  join-with-code, discover-joinable-group, create/read/approve/reject
  membership-request, select-active-membership-context.

## 4. Membership lifecycle — candidate states (evidence, not a decision)

0e/0f/0g together show that Membership needs more than an active/inactive
flag. Candidate states surfaced by the screens: `PENDING`, `ACTIVE`,
`REJECTED`, `SUSPENDED`, `LEFT`, `CANCELLED`. None is approved by this review.
Also surfaced, as scenarios the eventual state machine must answer rather
than as an answer itself: applicant vs. approval-authority actor split;
cancel-while-pending (0f "요청 취소"); re-apply after rejection or
cancellation; invite-code expiry; duplicate-code submission; an account
already active in one group attempting to join or be pending in a second
group at the same time.

## 5. Screen Token Normalization Matrix

Guideline rule preserved: no new raw color/radius/shadow value is registered
as a token by this review. Classification order applied:
`MAP_TO_EXISTING_TOKEN` → `COMPOSE_EXISTING_TOKENS` →
`REMOVE_DECORATIVE_VARIATION` → `PM_TOKEN_DECISION_REQUIRED`. None of the raw
values below appear anywhere in current `frontend/src/**/*.css` (checked by
grep) — they are new to this source, not already-adopted patterns.

| Raw value | Usage location | Semantic purpose | Existing token candidate | Mapping confidence | Visual risk | New token required | Final status |
|---|---|---|---|---|---|---|---|
| `#7B4BEE` | CTA button gradient start (paired with `#5A35DF`) | brand gradient accent | `--color-brand-500` (`#6B46F2`) | MEDIUM | LOW–MEDIUM | maybe (reusable `--gradient-brand`) | COMPOSE_EXISTING_TOKENS |
| `#C6A9F5` / `#B58EF0` / `#A579EC` | onboarding hero background, 3-stop gradient | onboarding atmosphere | none — nearest family members are `--color-brand-200`/`400`/`500` but stops don't correspond | LOW | MEDIUM (signature visual element) | yes, if hero gradient is kept | PM_TOKEN_DECISION_REQUIRED |
| `#4A3F72` | hero/body subtext | text-secondary | `--color-ink-700` (`#434A68`) | HIGH | LOW | no | MAP_TO_EXISTING_TOKEN |
| `#8A83A8` | meta/tertiary text | text-tertiary | `--color-ink-500` (`#757C98`) | MEDIUM–HIGH | LOW | no | MAP_TO_EXISTING_TOKEN |
| `#B8B3CC` | input placeholder text | placeholder | no exact token; closer/paler than `--color-ink-500` | LOW–MEDIUM | LOW | maybe | COMPOSE_EXISTING_TOKENS |
| `#E6E2F4` | input/card border | hairline border | `--color-line` (`#E8E6F2`) | HIGH | NONE | no | MAP_TO_EXISTING_TOKEN |
| `#22C55E` (fg) / `#EEFBF2` (bg) | "확인됨" success chip | success state | fg → `--color-success` (`#2FBE78`); bg → none (no success-soft/tint token exists) | fg HIGH / bg LOW | LOW | bg tint only | fg MAP_TO_EXISTING_TOKEN, bg PM_TOKEN_DECISION_REQUIRED |
| `#FFC93C` / `#F1983A` | onboarding-2 reward star badge gradient | reward accent | `--color-reward` (`#F1B83A`) close to darker stop only | MEDIUM | LOW–MEDIUM | partial | COMPOSE_EXISTING_TOKENS (base), PM_TOKEN_DECISION_REQUIRED (light stop) |
| `#F4F2FD` | pill/chip background ("인증요청" button, tip box) | soft brand tint | `--color-brand-50` (`#F8F5FF`) or `--color-brand-100` (`#EEE8FF`) | MEDIUM–HIGH | LOW | no | MAP_TO_EXISTING_TOKEN |
| `#E3DBFB` | tip-icon inner chip background | soft brand tint (deeper) | `--color-brand-200` (`#D9CCFF`) | MEDIUM | LOW | no | MAP_TO_EXISTING_TOKEN |
| `#9B7BF5` / `#7C5AEF` | group-avatar initial badge gradient | avatar accent | `--color-brand-400` (`#8B6DF5`) / `--color-brand-500` (`#6B46F2`) | HIGH | LOW | no | MAP_TO_EXISTING_TOKEN / COMPOSE_EXISTING_TOKENS |
| `#EEE8FF` | plus-icon chip background | soft brand tint | exact match: `--color-brand-100` | VERY HIGH | NONE | no | MAP_TO_EXISTING_TOKEN (already a token, no gap) |
| `#FBFAFE` | bottom-sheet surface | elevated surface | near-exact match `--color-surface-soft` (`#FBFAFF`); also the literal already-decided `--admin-sidebar-bg` value | VERY HIGH | NONE | no | MAP_TO_EXISTING_TOKEN |
| `#5A35DF`, `#17103A`, `#F7F6FC` | brand accent, ink, canvas throughout | — | exact matches: `--color-brand-600`, `--color-ink-900`, `--color-canvas` | VERY HIGH | NONE | no | already tokens, no gap |

Radius/shadow observation (not a full matrix, given the user's explicit raw-value
list was color-only): button/input radius (16–18px) and card radius (24px)
already correspond to `--radius-control`/`--radius-card`. The phone-frame
44px corner is mockup device chrome, not a screen element, and is
`NOT_APPLICABLE`. The bottom-sheet radius (34px top / 44px bottom) exceeds
`--radius-hero`/`--radius-dialog` (28px each) — flagged `PM_TOKEN_DECISION_REQUIRED`
only if/when a bottom-sheet pattern is actually implemented; no action needed
while these screens remain reference-only.

## 6. Logo kit classification

```text
MONGLE_LOGO_KIT_V1:            BRAND_ASSET_SSOT
LEGACY_POINT_FESTIVAL_LOGOS:   LEGACY_ASSET
```

Basis: the kit's own `README.md`/`manifest.json` document direct pixel
extraction from the approved brand board (`method: "direct pixel extraction;
no wordmark redraw"`, SHA-256-pinned source), not a redraw — consistent with
the product name already being decided as 몽글/Mongle
(`MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md` Layer 1). This is therefore not a
re-open of the "should we rebrand to Mongle" question; that is already
settled. **What this classification does not do**: it does not authorize
swapping `MainLogo.tsx` / `AdminBrandLogo.tsx` / favicon assets away from the
current legacy 포인트 잔치 files (`frontend/src/assets/logos/auth-logo.png`,
`frontend/public/logo*.png`, `frontend/public/favicon*`). That is a product-code
change and is explicitly out of scope for this review (§10) — and per PM
direction received during this review, **any actual component/asset swap
requires a separate, explicit PM approval at the time it's implemented**,
since the visual design may still change before then.

**Text logo, not character logo:** per PM direction, when integration is
eventually approved, the prioritized reference asset is the **wordmark
(text) logo** — `assets/wordmark/svg/mongle-wordmark-primary-exact.svg`
(light backgrounds) / `mongle-wordmark-white-exact.svg` (dark backgrounds) —
not a character/mascot lockup. This is already consistent with how the kit
itself is scoped: per its own `README.md`, "캐릭터 파일은 이 키트의 배포
자산으로 복제하지 않았다" (character files are not shipped as distributable
assets in this kit; only wordmark, monogram, and app-icon are). The
character-lockup reference image in `previews/` and the mascot pin image
used inside the new onboarding screens remain reference/UX material only,
per the guideline's own "다른 화면에 남용 금지 (캐릭터 상품화 방지)" rule.

Reference checklist confirmed present in the kit for the eventual
integration task: wordmark (SVG/PNG/WebP, transparent + light/dark
background variants), monogram, app icon, minimum-size and clear-space specs,
CSS usage pattern (`mongle-logo.css`), Primary-Exact-preservation and
no-redraw constraints, and the "마스코트 핀 이미지 오남용 금지" rule.

## 7. Backlog addendum

Eight new rows were appended to `MONGLE_IMPLEMENTATION_BACKLOG.md`'s existing
table, matching its existing column shape and `BLOCKED: PM_DECISION_REQUIRED`
convention: `MONGLE-W1-ONBOARDING-INTRO-UI-001`,
`MONGLE-W1-ACCOUNT-SIGNUP-UI-001`, `MONGLE-W1-GROUP-SELECTION-UI-001`,
`MONGLE-W1-GROUP-CREATION-UI-001`, `MONGLE-W1-GROUP-CODE-JOIN-UI-001`,
`MONGLE-W1-GROUP-DISCOVERY-UI-001`, `MONGLE-W1-MEMBERSHIP-PENDING-UI-001`,
`MONGLE-W1-AUTH-BRAND-INTEGRATION-001`. None of these are opened as
`agent-system/active.md` Task IDs by this review — they are backlog planning
rows only, consistent with every other row in that document.

## 8. Test matrix addendum

Target journeys implied by the 9 screens were appended to
`MONGLE_DOD_AND_TEST_MATRIX.md` as `TARGET_PRODUCT`-class examples, all
`PM_DECISION_REQUIRED` pending D1–D4/D7: onboarding complete; signup success;
signup failure; external-identity signup cancelled; duplicate
identity/verification; post-signup no-group state; single-group auto
selection; multi-group selection; group creation; duplicate group name
handling; valid-code join; invalid code; expired code; already-a-member;
group discovery; join-request creation; approval pending; approval granted;
join rejected; join-request cancelled; cross-group access denied;
unauthorized-approval attempt.

## 9. Documents amended by this review

`MONGLE_TARGET_DECISION_FREEZE.md`, `MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md`,
`MONGLE_EPIC_FEATURE_DECOMPOSITION.md`, `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`,
`MONGLE_IMPLEMENTATION_BACKLOG.md`, `MONGLE_DOD_AND_TEST_MATRIX.md`,
`MONGLE_TARGET_DECISION_PACKAGE_RECONCILIATION_REPORT.md` — each received a
short append-only addendum cross-referencing this document; no existing
row, decision, or Gate verdict in any of them was rewritten.

## 10. Out of scope (confirmed not done)

No product code, test code, DB/migration, or `agent-system/` shared file
(`active.md`, `relay/current.md`, `decisions/`, `qa/`, `handoffs/`) was
touched. The bundler artifact was not ported as-is and no inline style was
copied into any component. No new raw color/radius/shadow was registered as
an approved token. No Auth method, Group naming, or Route/API surface was
decided. No logo was redrawn and no legacy-vs-Mongle branding decision was
made or re-opened. No commit, push, merge, rebase, or PR was performed.

## 11. Five gates

- **Gate 1 (hallucination):** every signup affordance shown in 0b is recorded
  as evidence requiring its own D2 classification, not asserted as an
  approved v1 requirement. No API or DB object referenced above is claimed
  to exist; §3's route/API list is explicitly marked not-yet-approved. The
  logo kit's SSOT basis was checked against its own README/manifest
  (SHA-256-pinned, direct-extraction method), not assumed. No raw value in
  §5 was promoted to an approved token. **PASS**
- **Gate 2 (omission):** all 9 screens appear in §2's three tables; D1/D2/D3/D4/D7
  are all linked in §3; the pending-membership lifecycle is in §4; route,
  API, test, token, and logo impacts are all covered (§3, §5, §6, §7, §8).
  **PASS**
- **Gate 3 (wrong action):** no product code was edited; no inline mockup
  style was copied into a component; no new token was registered; no
  `agent-system/` file was touched. **PASS**
- **Gate 4 (center of gravity):** all 9 screens are read as Mongle
  Account/Group flows, consistent with `MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md`
  Layer 1 — not as a regression to the legacy Player/PIN flow. No new
  `WAIT_FOR_DATA_A_RESULT`-style wait state was introduced; DATA-A and
  architecture reconciliation are treated as their own terminal status says.
  The review stayed scoped to this source's impact and did not re-open the
  full architecture reconciliation. **PASS**
- **Gate 5 (staleness/evidence):** `MONGLE_TARGET_DECISION_FREEZE.md` was
  used as SSOT and left untouched in its decision rows; the actual current
  `docs/temp/.../신규화면-적용가이드라인.md` and screen markup were read
  directly (not recalled from a prior summary); legacy 포인트 잔치 assets
  were not treated as the Target brand asset. Backlog and test-matrix
  additions match the 9 screens 1:1. **PASS**

## 12. Completion checklist

```text
NINE_SCREENS_MAPPED:                              DONE
D1_D2_D3_D4_D7_IMPACTS_RECORDED:                  DONE
MEMBERSHIP_PENDING_LIFECYCLE_DEFINED_AS_DECISION: DONE (candidates only, not decided)
TOKEN_NORMALIZATION_COMPLETE:                     DONE
LOGO_KIT_CLASSIFIED:                              DONE
VERTICAL_UI_TASKS_CREATED:                        DONE (backlog rows only)
TARGET_JOURNEYS_ADDED:                            DONE
NO_PRODUCT_CODE_CHANGE:                           CONFIRMED
NO_SHARED_AGENT_FILE_CHANGE:                      CONFIRMED
FIVE_GATES_PASS:                                  CONFIRMED
```

## 13. Final verdict

PM-confirmed 2026-07-31: `PASS`. Status `READY_FOR_PM_TARGET_DECISION_REVIEW_WITH_NEW_SCREEN_EVIDENCE`
confirmed correct as-is (no regression to `WAIT_FOR_DATA_A_RESULT`).

`READY_FOR_PM_TARGET_DECISION_REVIEW_WITH_NEW_SCREEN_EVIDENCE`

0c → 0g gap PM ruling (see §2a): confirmed a real gap. PM recommendation
recorded — add a 0c entry card/CTA into 0g, keep 0g — scoped to D1/D3/D4/D7
and not yet an approved decision.
`0g SCREEN: VALID_TARGET_REFERENCE` / `0c->0g ENTRY PATH: PM_DECISION_REQUIRED`
/ `IMPLEMENTER-ADDED CTA: PROHIBITED` until those decisions land.

Next authorized action: `PM_REVIEW_RECONCILED_TARGET_DECISIONS` — specifically
D1 (group semantics incl. discovery privacy and the 0c→0g exposure question),
D2 (per-credential v1 classification), D3 (pending-membership session context,
plus what a no-group Session may browse), D4 (creator role edge case,
code-issue/approval authority, plus who exposes/approves discovery entry),
and D7 (route/API surface for
`/onboarding`, `/signup`, `/groups/*`). Any component-level logo integration
requires a separate PM approval at implementation time, per PM direction
recorded in §6.
