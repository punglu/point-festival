# MONGLE W7.1 Screen Ownership and Topology Freeze

## 1. Verdict

`MONGLE_W7_1_SCREEN_OWNERSHIP_TOPOLOGY_FREEZE_CONDITIONAL`
`SCREEN_OWNERSHIP_BASELINE_FROZEN`
`REACT_CANONICAL_PORT_TOPOLOGY_READY`
`PRODUCT_INTEGRATION_TOPOLOGY_PARTIALLY_FROZEN`
`READY_FOR_W7_2_REMAINING_REACT_CANONICAL_PORT`
`NOT_READY_FOR_FINAL_PRODUCT_INTEGRATION`

All 69 live labels and all 66 live canonical-ID groups are classified. The ownership baseline and detached W7.2 port topology are frozen; final product-route and integration topology remains conditional on the explicitly listed PM decisions.

## 2. Baseline

Observed 2026-08-02: `/Users/mac/mac_Project/mongle_ui`, `dev-newmarkp`, `3294c902a88a846d75e0896741784f75aa827fbe`; 54 pre-existing dirty paths. No product, route, React, CSS, directory, API, backend, package, Docker, or Git-history mutation was made.

## 3. Authority Inputs

The Wave 7.0 report and its 76-row authority matrix are the only screen-coverage SSOTs. This task uses their 69 live labels / 66 live IDs / 36 React-confirmed / 28 missing / 5 conflict evidence. `MONGLE_W6_TOKENIZED_SCREEN_INVENTORY.md` and the partial tokenized HTML were not used as full coverage sources.

## 4. Classification Rules

An existing `App.tsx` route or nested `AdminDashboard` route is `EXISTING_*`; a detached `/__wave6/*` route is not a product route. A mockup was treated as a modal/state/tab when its own copy describes a confirmation, empty/error, progress, or action outcome. “Detail” becomes a nested route only where entity refresh/share/back behavior supports that decision. Candidate paths are explicitly marked rather than presented as existing directories.

## 5. Product Navigation Tree

```text
Public / Auth
├─ / AuthPage: 1a profile selector → 1j PIN → 1j-1 lockout
├─ /login: 1a-1 password login
└─ proposed auth flow: 2d recovery → email verification

Family Context
├─ /family: 1b home
├─ proposed family destinations: 1g schedule, 1h album, 1i todo, 1n notifications,
│  1q members, 1v rules, 1f profile, 2k settings, 1r onboarding, 2w invite acceptance
└─ child views/modals: 1o, 1p, 1w, 2f, 2n–2r, 2u–2z, 3a, 3f–3l

Markpoint user
└─ /markpoint: 1c point festival → 1k mission detail, 1l/2j reward, 1s/2c/2h outcomes

Wagle
└─ /wagle: 1d conversation → 1t settings, 2b media, 2g reply; proposed 3c board → 3d/3e

Admin Dashboard
├─ /admin: 2i parent dashboard → 1x report, 2x stats → 3b filter
├─ /admin/missions: 2e management → 1m approvals, 1z/2l/2m dialogs
├─ /admin/points: 1e point management → 2o policy
├─ /admin/players: 2a user detail
└─ /admin/notifications: 2t announcement
```

## 6. Screen Composition Trees

```text
AuthPage
├─ 1a profile selector [STATE_VARIANT]
├─ 1j PIN entry [STATE_VARIANT]
└─ 1j-1 account lock [STATE_VARIANT]

MarkpointUser (1c)
├─ 1k mission detail [NESTED_ROUTE] → 1s rejection [MODAL_DIALOG]
├─ 1l reward exchange [NESTED_ROUTE] → 2h confirmation [MODAL_DIALOG]
├─ 2j reward shop [NESTED_ROUTE]
└─ 2c level-up [MODAL_DIALOG]

Admin MissionView (2e)
├─ 1m approval queue [TAB_VIEW]
├─ 1z basic mission form [MODAL_DIALOG]
├─ 2l create mission [MODAL_DIALOG]
└─ 2m edit/detail mission [MODAL_DIALOG]

Family Album (1h)
├─ 1w search result [STATE_VARIANT]
├─ 1p photo detail [NESTED_ROUTE]
├─ 2v upload progress [STATE_VARIANT]
└─ 2y sharing settings [NESTED_ROUTE]
```

## 7. Ownership Summary

| Owner aggregate | Labels |
| --- | ---: |
| AUTH_FLOW | 7 |
| FAMILY_CONTEXT | 35 |
| USER_DASHBOARD (Markpoint user) | 7 |
| WAGLE | 7 |
| ADMIN_DASHBOARD | 13 |

## 8. Route Decision Summary

| Route requirement | Labels |
| --- | ---: |
| Existing route / nested route | 13 |
| New route / nested route required | 30 |
| No route | 24 |
| Route decision required | 2 |

Existing product evidence covers `/`, `/login`, `/family`, `/markpoint`, `/wagle`, and nested admin views. New requirements are topology targets, not route changes authorized by this task.

## 9. Integration Action Summary

| Integration action | Labels |
| --- | ---: |
| Merge/keep/replace existing product surface | 14 |
| New route/nested view | 33 |
| Modal or state variant | 18 |
| PM decision required | 4 |

## 10. React Preview-to-Product Mapping

36 marked React pages are UI-only sources: 35 have detached preview routes, while `1a-1` has `/login`. Product mapping is `PREVIEW_REFERENCE_ONLY` unless an existing product surface is separately evidenced. Existing product visual replacement/merge targets are explicit in the Matrix; no preview was promoted or moved.

## 11. Responsive Family Mapping

Every live ID remains `MOBILE_TABLET_PORTRAIT_LANDSCAPE` except desktop-primary admin compositions (`1e`, `1m`, `1v`, `1z`, `2a`, `2e`, `2i`, `2l`, `2m`, `2o`, `2p`, `2t`, `2x`, `3b`). The 132 tablet labels remain variants of the 66 IDs, never additional destinations.

## 12. Conflict Resolution Proposals

- `1y-network-error`: shell-owned cross-domain state; `1y-notification-empty`: 1n state; `1y-search-empty`: 1w state. These are proposed internal identifiers only.
- `2d-password-recovery` is the recovery parent; `2d-email-verification` is its child state. URL restoration policy is unresolved.
- `1a` maps to existing `AuthPage` player selection and `1a-1` maps to `/login`; their final unified-or-separate public-auth policy requires PM confirmation.

## 13. PM Decisions Required

| Decision | Related IDs | Question / recommendation |
| --- | --- | --- |
| W7.1-D1 | 1a, 1a-1 | Keep player selector and password login separate entry modes until PM selects a unified public-auth flow. |
| W7.1-D2 | 1y labels | Adopt the three proposed internal IDs; do not mutate source canonical IDs. |
| W7.1-D3 | 2d labels | Decide whether recovery and verification have separate URLs. Recommendation: recovery route with verification state until restore/share need is specified. |
| W7.1-D4 | 1f, 2k, 2z | Confirm profile/settings URL hierarchy. |
| W7.1-D5 | 1r, 2w | Confirm onboarding/invite public-versus-authenticated entry policy. |
| W7.1-D6 | 3c–3e | Confirm whether board is a Wagle destination or a separate family service. |
| W7.1-D7 | 3f–3l | Confirm product policy for locale/theme/account deletion/global search/widgets before product integration. |

## 14. Inputs for Wave 7.2

Every unimplemented label has an internal ID, domain, owner, primary role, parent, integration direction, target, and responsive family in the Matrix. The new `W7_2_PORT_READY` column is `YES` for all 28 React-missing labels; conflict labels are `NOT_APPLICABLE`, not missing implementation candidates. The seven PM groups are split as follows:

| Decision class | Decision IDs | W7.2 effect |
| --- | --- | --- |
| PORT_BLOCKING_DECISION | none | No decision changes the detached canonical visual baseline required by W7.2. |
| PRODUCT_INTEGRATION_ONLY_DECISION | W7.1-D1 through D7 | Blocks final product route, navigation, policy, and integration changes only. |

W7.2 may build detached canonical React/CSS/fixture baselines only. It must not add product routes, navigation, API wiring, or final product integration until the applicable PM decision is resolved.

## 15. Validation

The Matrix was reconciled to 69 rows / 66 IDs. `frontend/npm run lint`, `frontend/npm run build`, and `git diff --check` are recorded in task QA evidence. Docker and runtime smoke were not run.

## 16. Final Freeze Declaration

`SCREEN_OWNERSHIP_BASELINE_FROZEN` means owner, parent, role, route requirement, integration direction, and responsive family are evidence-based inputs for W7.2. `PRODUCT_INTEGRATION_TOPOLOGY_PARTIALLY_FROZEN` means final route and integration policy is deliberately not frozen. No implementation-completion claim is made.
