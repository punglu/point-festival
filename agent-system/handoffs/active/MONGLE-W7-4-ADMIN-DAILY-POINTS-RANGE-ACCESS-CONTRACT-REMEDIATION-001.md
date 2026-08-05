# MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001

- Task ID: `MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001`
- Branch: `dev-newmarkp`
- Start HEAD: `97bc09d` (local); implementation performed against `281d45a` (`origin/dev-newmarkp`, contains the DEFECT-001/002 admin-auth remediation this fix builds on) in a detached QA worktree, since local `dev-newmarkp` does not yet contain `281d45a` and merge/rebase/commit were out of scope for this session
- End HEAD: unchanged (`97bc09d`) — no commit/push performed, per this task's own PASS criteria (`commit/push 0`)
- Implementation location: written and verified in a detached worktree at `281d45a` first (since local `dev-newmarkp` lacked that commit), then confirmed byte-identical for both touched files between `97bc09d` and `281d45a` (`git diff 97bc09d..281d45a` touches neither file) and applied via `git apply` directly onto this real `dev-newmarkp` working tree — the worktree was removed, but the code itself now lives here as the uncommitted diff below, not only as an artifact
- Existing dirty at start: none (`dev-newmarkp` clean)
- Scope: fix `/api/daily-points/range` 403-for-every-Admin gap disclosed in `MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-RUNTIME-COMPLETION-001`. Out of scope: Wagle DEFECT-003, `frontend/Dockerfile` npm→pnpm, Auth/Family/Markpoint Independent QA, W7.6.

## Confirmed root cause (reproduced before fixing)

`/api/daily-points/range` (`backend/app/domains/daily_point/router.py`) is gated by `Depends(get_current_player)`, which requires `role == "player"` and then self-scopes via `require_self_player_id`. `AdminDashboard/hooks/useAdminData.ts` calls this same route once per player inside a `Promise.all` on every `/admin` mount to build the balancing view. Reproduced against a live isolated stack (`docker-compose.phase1.yml -p mongle`, backend `281d45a`):

| Identity | `/api/daily-points/range` | Note |
|---|---|---|
| Account-native Admin (`admin.a`) | 403 `플레이어 권한이 필요합니다` | `get_current_player` rejects `role=="account"` outright |
| legacy Admin (`dad`) | 403 (same) | `get_current_player` rejects `role=="admin"` outright |
| legacy player (self) | 200 | unaffected — this is the route's real, intended audience |
| legacy player (another player_id) | 403 | `require_self_player_id` — correct, pre-existing |
| non-Admin Account | 403 | correct, pre-existing |
| unauthenticated | 401 | correct, pre-existing |

Because the failing calls sit inside `Promise.all`, the whole `try` block in `useAdminData.loadDashboardData` rejects on the first Admin session's first player — `players`/`missions`/`notifications` (fetched earlier in the same function) still render, but `dailyPoints` stays `[]` forever, so `PlayerStatusCard`'s point total and level bar always read `0pt`/`Lv.1` for every player regardless of real data.

## Authorization contract analysis

The route serves two genuinely different scopes under one path: a player reading their own data (self-only, `get_current_player` + `require_self_player_id`) and Admin reading *any* player's data for balancing (cross-player, no self-restriction). Widening `get_current_player` itself was rejected — it would let any Admin token bypass the self-only guarantee that route's real audience (players) relies on, and the task explicitly prohibits "모든 로그인 사용자 허용" / "role 문자열만 임의 비교". Chosen: **direction C** — a new Admin-scoped route under `/api/admin/*`, mirroring the codebase's own existing pattern (`GET /api/admin/daily-points` already exists beside the player-only `GET /api/daily-points/`), reusing the unchanged `get_daily_points_range` service function (no new query, no point-policy change), gated by `get_current_admin` — the same DEFECT-001/002-fixed dual-credential bridge already used by every other `/api/admin/*` route.

## Changed files

- `backend/app/domains/admin/router.py` — new `GET /api/admin/daily-points/range` (import `get_daily_points_range`; route body is a single pass-through call, no new logic)
- `frontend/src/pages/AdminDashboard/api/adminApi.ts` — `getDailyPointsRange` now calls `/api/admin/daily-points/range` instead of `/api/daily-points/range`

No other file touched. No DB schema/migration change. No change to `get_daily_points_range`, `require_self_player_id`, `get_current_player`, or the existing player-facing route.

```diff
diff --git a/backend/app/domains/admin/router.py b/backend/app/domains/admin/router.py
index 7159971..fc286c9 100644
--- a/backend/app/domains/admin/router.py
+++ b/backend/app/domains/admin/router.py
@@ -47,7 +47,7 @@ from app.domains.deduction.service import (
 )
 
 from app.domains.daily_point.schema import DailyPointAdjust, DailyPointResponse
-from app.domains.daily_point.service import adjust_daily_point, get_daily_points_admin
+from app.domains.daily_point.service import adjust_daily_point, get_daily_points_admin, get_daily_points_range
 
 from app.domains.cheer.schema import CheerCreate, CheerResponse
 from app.domains.cheer.service import upsert_cheer
@@ -243,6 +243,27 @@ async def admin_list_daily_points(
     return await get_daily_points_admin(db, player_id, target_date)
 
 
+# MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001: the
+# player-facing `/api/daily-points/range` requires `get_current_player` and
+# self-scopes to the caller's own player_id, so it 403s for every Admin
+# session (Account-native or legacy alike) regardless of which player_id is
+# requested — Admin's balancing view needs an arbitrary player's range, not
+# its own. Rather than widen the player route's authorization (which would
+# let any Admin token bypass the self-only guarantee that route documents
+# for its real audience), this is a separate Admin-scoped route reusing the
+# same `get_daily_points_range` query unchanged: same data, same shape,
+# authorized by `get_current_admin` instead.
+@router.get("/daily-points/range", response_model=list[DailyPointResponse])
+async def admin_list_daily_points_range(
+    player_id: int = Query(...),
+    start_date: date = Query(..., alias="start"),
+    end_date: date = Query(..., alias="end"),
+    db: AsyncSession = Depends(get_db),
+    _: dict = Depends(get_current_admin),
+):
+    return await get_daily_points_range(db, player_id, start_date, end_date)
+
+
 @router.post("/daily-points/adjust", response_model=DailyPointResponse)
 async def admin_adjust_daily_point(
     data: DailyPointAdjust,
diff --git a/frontend/src/pages/AdminDashboard/api/adminApi.ts b/frontend/src/pages/AdminDashboard/api/adminApi.ts
index a8603fc..4e7ad92 100644
--- a/frontend/src/pages/AdminDashboard/api/adminApi.ts
+++ b/frontend/src/pages/AdminDashboard/api/adminApi.ts
@@ -79,7 +79,7 @@ export const adminApi = {
     httpClient.get<DailyPoint[]>('/api/admin/daily-points', { params, signal }),
 
   getDailyPointsRange: (playerId: number, start: string, end: string, signal?: AbortSignal) =>
-    httpClient.get<DailyPoint[]>('/api/daily-points/range', { params: { player_id: playerId, start, end }, signal }),
+    httpClient.get<DailyPoint[]>('/api/admin/daily-points/range', { params: { player_id: playerId, start, end }, signal }),
 
   adjustDailyPoint: (data: { player_id: number; date: string; delta: number }, signal?: AbortSignal) =>
     httpClient.post<DailyPoint>('/api/admin/daily-points/adjust', data, { signal }),
```

## Verification result (Developer self-check, live isolated stack — `docker-compose.phase1.yml -p mongle`, DB 15434, backend 18001)

**New `/api/admin/daily-points/range`**
- Account-native Admin (`admin.a`): 200, real data
- legacy Admin (`dad`): 200, real data
- legacy Admin, null `player_id`: 200 (regression-relevant: DEFECT-002 bridge unaffected)
- legacy player: 401
- non-Admin Account (`owner.a`): 401
- unauthenticated: 401

**AdminDashboard (Playwright, disposable spec, deleted after use)**: after crediting player 3 (`아빠`) +15 via the pre-existing `/api/admin/daily-points/adjust`, `/admin`'s "플레이어 현황" card shows `15pt` (previously always `0pt`) for both Account-native and legacy Admin sessions, holds across a full reload, and renders without horizontal overflow at 390×844 / 820×1180 / 1180×820.

**Regression**
- existing player-only `GET /api/daily-points/range`: self 200 unchanged, other-player 403 unchanged (self-only guarantee intact), Account-native Admin still 403 on this route specifically (deliberately not widened)
- `GET /api/admin/daily-points` (existing single-day admin endpoint): 200, unaffected
- `GET /api/account-context` 403 `mapping_required` (null-player legacy Admin, DEFECT-002): unaffected
- `git diff --check`: exit 0
- `python3 agent-system/tools/check_all.py`: same warning set as pre-change baseline, 0 new

**Static/build**
- `pnpm lint`: 0 warnings/errors
- `pnpm build` (`tsc -b && vite build`): passed, no new TS errors

**Backend pytest** (fresh isolated DB, `postgres:16.9-alpine` on 15435 + `alembic upgrade head` + `database/init.sql`)
- Full suite: 404 passed, 1 failed — `test_wagle_reliable_service_slice.py::test_outbox_07_two_workers_no_double_claim`. This is the pre-existing, already-registered `KNOWN-W7-5-WAGLE-CONCURRENCY-001` condition in `agent-system/qa/COVERAGE_MAP.md` (Wagle's own `asyncio.gather`-driven concurrency tests, non-deterministic under host timing, unrelated to any change made by any task including this one).
- Isolation confirmed unrelated to this change: `git stash`ed both changed files, re-ran `test_wagle_reliable_service_slice.py` alone — same single failure on unmodified `281d45a` code. Restored the change, re-ran twice more — same single failure both times, no additional failures. The one run that showed 5 failures in the same file was a standalone-file-run-only anomaly not reproduced on 2 immediate retries with the identical (fixed) code, consistent with the registered `KNOWN_CONDITION`'s documented shape, not a regression this change introduced.

## DB safety

Isolated official test DB (`mongle_phase1_pg_data`, `mc_festival_phase0`), no persistent/operating DB touched. QA-only rows created and deleted, final state confirmed equal to baseline:
- `admin_auth`: +1 marker (`qa_marker_null_player_admin_range_fix`, `player_id=NULL`) → deleted → 2 rows (baseline)
- `daily_points`: +1 row (`player_id=3`, `2026-08-03`, `earned=15`, via the pre-existing adjust endpoint, to prove the fix surfaces real data) → deleted → 0 rows (baseline)
- separate ad hoc Postgres container for backend pytest (`mc_phase2_qa_db`, port 15435): created and fully removed after use

## Documents

- Created: this handoff; `agent-system/qa/MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001.md` (Developer QA Evidence)
- Updated (append-only): `agent-system/qa/COVERAGE_MAP.md`, `agent-system/active.md`, `agent-system/relay/current.md`
- Not modified: any prior QA finding's own body (the `KNOWN-W7-5-WAGLE-CONCURRENCY-001` row referenced above is cited, not edited)

## Remaining risks

- No automated backend test added for the new route itself (mirrors the existing `/api/admin/daily-points` route's own lack of a dedicated pytest — same pattern, not a new gap this task introduced, but worth flagging for Independent QA).
- `frontend/Dockerfile` npm→pnpm mismatch (found during the prior runtime-completion QA) is still unfixed — out of scope here, blocks the official container frontend build; this session verified via native `pnpm run dev` instead, same as the prior QA session.
- Product code sits uncommitted in `dev-newmarkp`'s actual worktree at `/Users/mac/mac_Project/mongle_ui` (2 files) — no commit/push performed per this task's own constraints; PM action needed to land it (and, separately, to bring `281d45a` itself onto local `dev-newmarkp`).

## Declaration

`DEVELOPER_SELF_CHECK_COMPLETE` — this session modified product code; Independent QA PASS is not self-declared.

Next Task: `MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-001`
