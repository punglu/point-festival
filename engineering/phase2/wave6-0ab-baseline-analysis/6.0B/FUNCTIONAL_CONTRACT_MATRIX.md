# Functional Contract Matrix

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Section 18). Full data: `functional_contract_matrix.csv` (40 rows across A1-A5).

Classification legend: `MUST_PRESERVE / MAY_RECOMPOSE_VISUALLY / CURRENT_TEMPORARY / FIXTURE_ONLY / DEFERRED / KNOWN_GAP / PM_POLICY_REQUIRED / NOT_VERIFIED`.

## By screen

- **A1 (로그인)**: core flow (player fetch → select → PIN → session → role-based redirect, admin entry) is
  `MUST_PRESERVE`, confirmed directly in `pages/Auth/index.tsx`. The approved source's A1-S1 ("순수
  ID/PW 로그인") has **no current equivalent** at all — classified `KNOWN_GAP`, not silently assumed
  covered by the existing admin ID/PW form (which is a distinct, admin-only path).
- **A2 (가족 홈/Shell)**: Account/Family Context, Header, Dock visibility filtering, service eligibility,
  logout, and the dual canonical/legacy storage-key contract are all `MUST_PRESERVE` — each is backed by
  either direct code (`useFamilyContextStore.ts`, `MongleAppShell.tsx`) or a passing `specs-mongle` test.
  The actual **A2 home-screen content itself is `MISSING`** — `/family` is a stub (see route map).
- **A3 (마크포인트)**: mission/points/deduction/level/cheer/approval-flow are all `MUST_PRESERVE`, backed by
  a real typed API client (`dashboardApi.ts` interfaces: `MissionResponse`, `DailyPointResponse`,
  `DeductionResponse`, `CheerResponse`, `PointCycleSummary`, etc.) and by this project's own operational
  history (CLAUDE.md Phase 7 patch log references real bugfixes to this exact approval flow). Internal
  hook-level detail (filtering/refresh/error-handling) was **not** read this session — marked
  `NOT_VERIFIED` rather than assumed working.
- **A4 (와글와글 GROUP)**: every single functional item is `FIXTURE_ONLY` or `CURRENT_TEMPORARY`. Room
  selection, composer send/pending/failed/retry, the 3 loading/empty/error preview states, and the
  desktop auto-select-first-room behavior are all driven by static fixture data or dev-only query-param
  toggles — **no real API call exists behind any of it**. This is the largest FUNCTION_BLOCKER-class gap
  in the whole audit: the approved screen (A4) depicts a real messaging surface, but the current
  implementation, however visually close (see TIER1_HTML_VISUAL_DELTA), has no live functionality.
- **A5 (관리자 포인트)**: auth/RBAC, point data, filter, and (importantly) row-action **dialogs**
  (`AddDeductionModal`, `EditDeductionModal`) are all `MUST_PRESERVE` and, per `TIER1_HTML_VISUAL_DELTA.md`,
  the current implementation is already functionally *ahead* of the approved source here (the approved
  PNG has no dialog visual at all). Pagination/mutation/error-state detail was not read this session
  (`NOT_VERIFIED`).

No functional meaning was changed or reinterpreted in this pass — every classification is grounded in a
specific file/line or a specific passing/available test, and every gap in that grounding is marked
`NOT_VERIFIED` rather than inferred favorably.
