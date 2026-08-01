- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001
- Independent from implementer: true
- Verdict: CONDITIONAL
- Target commits: `1f505ea4341ace8bc770ec12f3f665d7a093fe7f`,
  `78913b48e1147073f3b1c56b39de9eea28d5d9cf`
- Current reason: the independent re-check confirms the malformed-`sid`
  correction. A complete independent backend-suite run remains outstanding;
  the re-check was stopped after it had progressed through 32 tests without a
  result summary, so it is not reported as a pass or failure.

## Direct evidence

`git show 1f505ea` confirms role widening and that both Account entry points
delegate to the shared resolver. A fresh volume-less PostgreSQL 16.9 instance
was initialized from `database/init.sql` and migrated `0000 -> 0011`.
`test_bg1_credential_surface_unification.py` passed 5/5 on a fresh isolated
run. An intervening run was invalidated because an earlier locally launched
pytest process still held the same DB; after stopping it and recreating the
DB, the 5/5 result reproduced.

Independent direct resolver attacks on the recreated DB:

```text
missing_sid=HTTP_401
bad_sid=ValueError
session_account_mismatch=HTTP_401
revoked_session=HTTP_401
```

`rg 'Depends(get_current_user)' backend/app --glob '*.py'` found 38 usages.
Raw `user['sub']` conversion is behind a player-only gate in
`get_current_player`, player/admin gates in feedback, or follows Account-role
dispatch into the shared resolver in family service. The legacy-token
authorization-lost expectation in `02-wagle-realtime.spec.ts` belongs to the
separate Account-native websocket gateway and is not inverted by this HTTP
change. `check_all.py` completed with only pre-existing governance warnings.

## Required correction

Catch `TypeError`/`ValueError` for `sid` parsing and return 401; add an HTTP
regression using a validly signed Account-role token whose `sid` is
non-numeric. This Task cannot close BG-1 until independently rechecked.

## Independent re-verification after `78913b4`

The correction was read directly in
`app/domains/family/auth_service.py`: `sid` is converted only inside a
`try` block that catches both `TypeError` and `ValueError` and returns 401.
`family.dependencies.get_current_account` and the Account branch of
`family.service.resolve_current_account` still both call this single resolver.

Two fresh, isolated PostgreSQL 16.9 databases (port 15435, no shared volume)
were each initialized from `database/init.sql`, migrated `0000 -> 0011`, and
executed `backend/tests/test_bg1_credential_surface_unification.py`:

```text
run 1: 6 passed, 1 warning, 5.25s
run 2: 6 passed, 1 warning, 5.19s
```

The added HTTP regression exercises both `/api/me` and `/api/account-context`
with a validly signed Account token carrying `sid="bad"`; both return 401.
Independent direct malformed-claim probes also returned 401 for an uppercase
`Account` role, missing `sid`, non-numeric `sid`, and list-valued `sid`.
The existing targeted tests independently cover session/account mismatch,
revoked session, suspended account, and a numeric Account/legacy Player ID
collision. `rg` again found 38 `Depends(get_current_user)` call sites.

An attempted complete backend-suite run on the second disposable DB emitted 32
successful progress markers but did not complete after 105 seconds; it was
stopped to avoid leaving a QA process or database contention behind. This is
not evidence of a test failure, nor evidence of full regression success.

The disposable database container and Python 3.11 virtual environment were
removed after the run. No product code was changed by this QA session.
