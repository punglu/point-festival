- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001
- Independent from implementer: true
- Verdict: BLOCKED
- Target commit: 1f505ea4341ace8bc770ec12f3f665d7a093fe7f
- Reason: `auth_service.resolve_account_from_session_claim()` calls
  `int(session_id)` outside a malformed-claim error boundary. A signed
  Account-role payload with `sid="bad"` raises unhandled `ValueError` rather
  than returning 401.

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
