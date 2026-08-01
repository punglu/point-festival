# QA Evidence — MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001
- Closeout Contract: v1

Self-check evidence for the BG-1 credential-surface fix. See the handoff
(`agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md`)
for full narrative; this file records the raw evidence.

## 1. Starting point re-measurement

Before any edit in this task, the pre-existing (uncommitted, unregistered)
fix in `app/dependencies.py` / `family/service.py` was re-measured live
against a fresh disposable Postgres container + real HTTP calls, replacing
the stale claims in `agent-system/qa/artifacts/wave6/BLOCKER_MEASUREMENT.md`:

```text
endpoint                                           account    legacy
/api/account-context                               200        403
/api/families/1/wagle/room-summaries               403        403   (auth cleared; resource-level 403, needs Wagle participant seed)
/api/me/markpoint/projection?family_id=1           200        401
/api/me/markpoint/weekly?family_id=1               200        401
/api/families/1/markpoint/missions                 403        401
/api/families/1/markpoint/config                   200        401
```

`/api/account-context` flip (401→200) confirms the fix is real and working,
not merely claimed.

## 2. Root-cause defect in the as-found fix

`family/service.py::resolve_current_account`'s new Account branch
duplicated `family/dependencies.py::get_current_account`'s Session-liveness
check verbatim (own docstring admitted as much: "That is the same check
`family.dependencies.get_current_account` performs"). Two independent
copies of a security check is the defect — extracted to
`auth_service.resolve_account_from_session_claim`, both call sites now
delegate. See handoff for the exact diff.

## 3. Safety enumeration (identity-confusion / IDOR check)

All 38 `Depends(get_current_user)` usages across
`app/dependencies.py`, `app/domains/{config,auth,wagle,family,feedback,cheer}/router.py`
traced. Result: zero unsafe direct `user["sub"]` extraction reachable by an
`account`-role token without an intervening role gate or
`resolve_current_account` call. Detail in the handoff's "Safety review"
section. `chat/admin/mission_template` use an unrelated, separate
`get_current_user` (`app.domains.auth.dependencies`) — out of scope,
unaffected.

## 4. Test evidence

Environment: disposable `postgres:16.9-alpine` container, port 15435, user
`mc_phase2` / db `mc_festival_phase2` (matches `tests/conftest.py`'s
hardcoded expectation), `database/init.sql` + `alembic upgrade head` → `0011`.
Python 3.11 venv (`/opt/homebrew/bin/python3.11`) with
`requirements.txt` + `requirements-dev.txt` installed — the system default
Python (3.9) cannot import this codebase's models (`str | None` PEP 604
syntax requires 3.10+).

```text
tests/test_account_auth_wave1.py                         33 passed
tests/test_wagle_realtime_wave3.py + family/account tests 41 passed
tests/test_bg1_credential_surface_unification.py (new)     5 passed
tests/ (full suite, second clean run)                     317 passed, 0 failed, 0 errors
```

First full-suite run (while a prior background full-suite process was still
contending for the same DB connections) showed 3 failed / 11 errors, all in
`test_wagle_realtime_wave3.py` (PIN lockout/isolation), `test_wagle_service_binding.py`,
`test_wagle_reliable_service_slice.py` — none touch the files this task
changed. Re-ran those three files standalone: 86/86 passed. Re-ran the full
suite again once the DB was uncontended: 317 passed, 0 failed, 0 errors.
Treated as pre-existing batch/connection-contention flakiness in this test
suite, not a regression from this change — recorded here rather than
silently dismissed, per this repository's own standard against trusting an
unexplained result.

## 5. New test file: what each test proves

`backend/tests/test_bg1_credential_surface_unification.py`:

1. `test_account_context_accepts_an_account_native_token` — the fix itself.
2. `test_revoked_session_is_rejected_identically_by_both_entry_points` — the
   specific property the shared-function refactor exists to guarantee:
   `/api/me` (`get_current_account`) and `/api/account-context`
   (`get_current_user` → `resolve_current_account`) reject the same revoked
   Session identically. This is the test that would have caught the as-found
   version's duplication risk if the two copies had ever diverged.
3. `test_deactivated_account_is_rejected_via_the_legacy_shaped_entry_point` —
   Account.status != "active" enforced on the `get_current_user` path too.
4. `test_widened_role_set_does_not_bypass_a_route_that_only_accepts_player_or_admin` —
   `/api/feedbacks/` still 403s an `account`-role token.
5. `test_account_id_colliding_with_a_legacy_player_id_is_not_confused` —
   worst-case IDOR scenario (Account.id == Player.id, both row 1 of a
   freshly truncated table): still 403, never treated as that player.

## 6. Environment teardown

`docker rm -f mongle-bg1-fixdb` confirmed removed; throwaway venv at
`/private/tmp/mongle_bg1_venv` deleted. Zero residue.

## 7. Verdict

`BG1_FIX_CONFIRMED_WORKING` / `ROOT_CAUSE_DUPLICATION_REMOVED` /
`NO_IDENTITY_CONFUSION_DEFECT_FOUND` / `REGRESSION_CLEAN_317_0_0` /
`INDEPENDENT_QA_PENDING`. This is self-check evidence from the session that
made the change; independent QA has not run.
