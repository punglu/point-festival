# MONGLE-COMBINED-NAMING-AND-FRONTEND-INDEPENDENT-QA-001

## 1. Executive Verdict

```text
COMBINED_NAMING_INDEPENDENT_QA_FAIL
NAMING_OR_RUNTIME_DEFECTS_REMAIN
NOT_READY_FOR_NEXT_WAVE
```

The required current-source Playwright coverage could not complete. The first
execution ran a stale `mc_phase1-frontend` image and failed; the harness did
not rebuild that service. Rebuilding the current frontend image was then
blocked in the local Docker BuildKit environment. A required E2E result is not
replaced by static checks or the host build.

## 2. Environment / Git Baseline

- observed_at: 2026-08-01; branch `dev-newmarkp`; start HEAD
  `0d9280c3d3a9254f20c09ba958eb3876e957d245`.
- Start `git diff --check`: clean. Existing dirty W2/W4, naming, agent-state,
  and frontend changes were preserved.
- No commit, push, merge, rebase, branch change, reset, restore, checkout,
  clean, or stash was performed.

## 3. Writer State

This task registered in `agent-system/active.md` and `relay/current.md` before
writing. It owns this report and the recorded QA-state updates. The prior
naming task had released its frontend writer claim.

## 4. Authoritative Inputs

Read: bootstrap/rules/active/relay, both naming reports and handoffs, parent
independent-QA report, allowlist, Target Domain/API records, Test Policy,
tests guide, frontend package/configuration, E2E Playwright configuration, and
the actual source/diff named below.

## 5. Changed-file and Rename Audit

`git diff --find-renames --name-status` measured Wagle-path/component renames,
`WagleLanding`, Naran route/storage changes, generated OpenAPI, the E2E spec,
and the backend seam test. The Wagle move is represented as Git renames (`R`/
`RM`), not asserted as an unmeasured `git mv` claim.

## 6. Wagle Frontend Zero Gate

Direct `rg -n -i 'doran|도란' frontend/src` returned zero lines; no
`*doran*` frontend source path exists.

```text
ACTIVE_FRONTEND_DORAN_IDENTIFIER_COUNT: 0
ACTIVE_FRONTEND_DORAN_FILE_IMPORT_COUNT: 0
ACTIVE_FRONTEND_DORAN_SERVICE_CODE_COUNT: 0
ACTIVE_FRONTEND_DORAN_API_REFERENCE_COUNT: 0
ACTIVE_FRONTEND_DORAN_COMPONENT_COUNT: 0
ACTIVE_FRONTEND_DORAN_TYPE_COUNT: 0
ACTIVE_FRONTEND_DORAN_CSS_COUNT: 0
ACTIVE_FRONTEND_DORAN_TEST_EXPECTATION_COUNT: 0
```

## 7. Naran Runtime Zero Gate

No active Naran runtime/API/backend literal was found. Five frontend-source
hits are prohibited-name/task-retirement comments only; the retired storage
value is assembled from two string parts in its dedicated migration source.
The E2E mentions are negative-route guards and a frozen task ID.

```text
ACTIVE_RUNTIME_NARAN_IDENTIFIER_COUNT: 0
ACTIVE_NARAN_ROUTE_COUNT: 0
ACTIVE_NARAN_FILE_PATH_COUNT: 0
ACTIVE_NARAN_IMPORT_COUNT: 0
ACTIVE_NARAN_COMPONENT_COUNT: 0
ACTIVE_NARAN_TYPE_COUNT: 0
ACTIVE_NARAN_STORAGE_KEY_COUNT: 0
ACTIVE_NARAN_CSS_COUNT: 0
ACTIVE_NARAN_API_REFERENCE_COUNT: 0
ACTIVE_NARAN_TEST_EXPECTATION_COUNT: 0
ACTIVE_BACKEND_NARAN_COUNT: 0
CURRENT_TARGET_DOCUMENT_NARAN_COUNT: 0
```

## 8. Split Legacy-key Audit

`activeFamilyStorageMigration.ts` evaluates the retired namespace as
`'na' + 'ran'`, producing `naran.activeFamily.<accountId>`; canonical is
`mongle.activeFamily.<accountId>`. They are distinct. The source limits the
retired form to migration read/purge and logout cleanup; normal store reads and
writes use only `mongle.activeFamily.*`.

## 9. Storage Migration QA

Source inspection confirms canonical-wins, copy-forward-before-purge,
malformed/inaccessible purge-without-adoption, idempotency, and canonical-only
subsequent writes. The browser assertions covering those branches were not
accepted as PASS because the current-source E2E execution did not complete.

## 10. Route Retirement QA

`App.tsx` registers `/`, `/dashboard`, `/admin/*`, `/wagle`, `/family`, and
`*`; it registers no `/naran` route, alias, or redirect. The actual browser
negative-route assertions require a valid current-image Playwright rerun.

## 11. Account-context / Wagle Seam

Against the isolated backend, authenticated `GET /api/account-context` returned
Alpha with `{ "service_code": "wagle", "status": "active" }`. Frontend
consumers compare `serviceStatus('wagle')` and `service.service_code ===
'wagle'`. The backend focused suite was blocked locally because host Python
lacks `pytest_asyncio`; its prior result is not adopted.

## 12. Generated OpenAPI

Live isolated OpenAPI exposed `/api/account-context`, 11 Wagle paths and 9
Markpoint paths; no Doran or Naran path was returned. Generated declarations
contain 0 Doran, 0 Naran, and 11 `/wagle/` path occurrences.

## 13. Clean Production Build

Host `npm run build`: PASS (`tsc -b` + Vite, 313 modules, 0.80s). This is
**not** claimed as the required clean install. The isolated clean Docker build
could not finish because the builder stalled; the repository has no frontend
`.dockerignore`, so the normal Dockerfile context also includes host
`node_modules`. No build/deployment configuration was changed by this QA.

## 14. Playwright Environment

The configured isolated `mc_phase1` database/backend/frontend harness was
started. It uses a disposable named volume and the teardown script removed the
containers, network and volume after each attempted run.

## 15. Playwright Results

`npx playwright test --config playwright.mongle.config.ts` executed against a
stale frontend image and exited failed; `.last-run.json` recorded 41 failures.
The observed stale page rendered Wagle unavailable despite the current backend
response. Inspection found `start-mongle-phase1.sh` built only db/backend and
reused frontend. A minimal harness correction was made, but a current-image
rebuild stalled in Docker BuildKit before frontend creation; therefore no
current-source Playwright PASS/FAIL count exists.

## 16. Frontend Test Matrix

- `npx tsc --noEmit`: PASS.
- `npm run lint`: PASS.
- `node --test src/shared/tokens/tokenContract.test.mjs`: PASS, 29/29.
- `npm run build`: PASS (host dependency tree only).
- Component-test harness: absent in repository.
- Current-source Playwright: BLOCKED/invalidated as described in §15.

## 17. Minimum Backend Contract Regression

Focused test command `python3 -m pytest -q tests/test_frontend_service_code_contract.py`
did not collect: `ModuleNotFoundError: pytest_asyncio` in the host Python.
This is `ENVIRONMENT`; no prior 3/3 result is copied. The live isolated API
seam observation is recorded in §11.

## 18. Historical-context Preservation

The legacy storage source is preserved as split input; E2E negative paths use
the retired platform name as input; frozen `E2E-NARAN-SHELL-001` remains a
Coverage ID; the closed allowlist declares no active exception. No global
historical-document replacement was made by this QA.

## 19. Allowlist Closeout

`MONGLE_NARAN_REMAINING_ALLOWLIST.md` declares
`ACTIVE_NARAN_ALLOWLIST: EMPTY`, `ACTIVE_NARAN_ROUTE_EXCEPTION: NONE`, and
`ACTIVE_NARAN_STORAGE_EXCEPTION: NONE`; storage migration source is explicitly
not an active exception.

## 20. Defects Found

1. `start-mongle-phase1.sh` did not rebuild the frontend, so Playwright could
   test a stale image instead of the worktree source.
2. The runner's Docker BuildKit stalled while building a current frontend
   image. This is an environmental blocker, not attributed to product code.

## 21. Corrections Applied

The E2E start command now requests a frontend build. No product naming,
route, storage, API, migration, or OpenAPI implementation was changed.

## 22. Regression Results

Static frontend regressions pass. Required current-source E2E and focused
backend regression remain unverified due the exact blockers above.

## 23. Five-Gate Review

- 환각: PASS — no unexecuted build/E2E/backend test is reported PASS.
- 누락: FAIL — current-source Playwright and clean install are incomplete.
- 오작업: PASS — no alias/fallback or permanent storage fallback added.
- 축혼동: PASS — migration source, negative guards and history are separated.
- 신선도/오탈자: CONDITIONAL — static/API evidence is current; runtime E2E is not.

## 24. Changed-file Manifest

QA-owned: this report, task registration/relay state, Coverage Map status, and
`tests/e2e/scripts/start-mongle-phase1.sh` minimal current-image correction.
All pre-existing implementation changes remain user/other-task owned.

## 25. Residual Risks

The required E2E flow and clean install/build are not independently proven on
the current source. Re-run after Docker BuildKit is operational, with the
isolated frontend image built from a clean context, then run the focused
backend seam test in the documented Python environment.

## 26. Lifecycle / Graduation

Lifecycle remains `IN_PROGRESS`; no Naming task, Track, integration task or
parent bundle is graduated by this QA.

## 27. Final Verdict

```text
COMBINED_NAMING_INDEPENDENT_QA_FAIL
NAMING_OR_RUNTIME_DEFECTS_REMAIN
NOT_READY_FOR_NEXT_WAVE
```
