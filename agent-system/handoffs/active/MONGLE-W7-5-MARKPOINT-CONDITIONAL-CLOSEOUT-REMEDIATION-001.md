# Handoff — MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001

- Task ID: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001

## Origin

Opened directly by PM from the 3 disclosed findings of
`MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001` (verdict
`CONDITIONAL`, not a code defect in the Markpoint fix itself):
`QA-F-001` (commit/push documentation staleness), `QA-F-002` (deducted-side
KST-boundary test coverage gap), `QA-F-003` (pre-existing OS-timezone
fragility in two Markpoint tests). PM's own direction, verbatim scope:

```text
1. commit 328d877 및 origin 반영 사실을 문서에 정정
2. commit 범위가 Markpoint remediation과 일치하는지 감사
3. today_deducted 결정론적 경계 회귀 테스트 추가
4. 기존 date.today() 기반 테스트 2개를 명시적 KST anchor로 안정화
5. Docker 가능 환경에서 E2E 1회 smoke
6. Backend 전체 suite 동일 DB 2회 연속
```

Registration check per `rules.md` Invariant 9: no existing `active.md`/
`graduated/*.md` entry, alias, or prior git history already covers this
narrow closeout scope — the parent QA task's own entry only records the 3
findings as disclosed, not remediated.

## Scope 1 — commit audit

`git show --stat 328d877` re-run fresh (not reused from the parent QA
session's own cached result): exactly 7 files —
`backend/app/domains/markpoint_target/service.py`,
`backend/tests/test_markpoint_core_gap_wave5.py`, and 5 `agent-system/`
governance files (`active.md`, `relay/current.md`, `qa/COVERAGE_MAP.md`, one
new handoff, one new QA evidence file). No file outside the Markpoint
remediation's own declared scope. Confirmed clean, no action required.

## Scope 2 — documentation correction (QA-F-001)

Per `rules.md` Invariant 5 (write-once evidence; a correction appends, it
does not rewrite), a `## Correction (...)` section was appended to both:

- `agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`
- `agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`

Each correction states the actual commit/push fact (`328d877`, confirmed
reachable from `origin/dev-newmarkp`), explicitly labels the original "no
commit/push" claim `STALE / INCORRECT` (accurate when written, not now), and
states no history was rewritten. The original claim text above each
correction is untouched.

## Scope 3 — deducted-side deterministic regression test (QA-F-002)

Added `test_projection_kst_boundary_independent_of_server_local_timezone_deducted_side`
to `backend/tests/test_markpoint_core_gap_wave5.py`, placed immediately
after its earned-side sibling. Mirrors that test's structure exactly:
explicit fixed KST dates (`2026-06-15`/`2026-06-14`), an explicit UTC
instant constructed via `service.KST` that crosses the KST/UTC boundary
(`2026-06-15 00:00 KST` = `2026-06-14 15:00 UTC`), one `MANUAL_DEBIT`
(amount `-18`) ledger row, and two `own_projection` calls asserting
`today_deducted == 18` for the KST-correct anchor and `== 0` for the
UTC-adjacent one. No existing assertion touched; this is a pure addition.

## Scope 4 — remove `date.today()` from the two pre-existing tests (QA-F-003)

`test_projection_derives_every_figure_from_the_ledger`'s `anchor =
date.today()` and `test_projection_isolates_date_boundaries`'s `today =
date.today()` both replaced with `datetime.now(service.KST).date()`. Only
the anchor-computation line changed in each test — confirmed via `diff`
against the committed HEAD blob that **zero assertion lines** were touched
(30/12/18/30/12/7/7 all unchanged). A short comment at each site explains
why, citing `QA-F-003`. `test_projection_reflects_a_reversal` (a third,
similarly-shaped `date.today()` use) was deliberately **not** touched — PM's
own scope named only "기존 두 테스트" (the two originally-failing tests from
`RE-QA-F-003`), and that third test was never flagged by the parent QA pass
as a finding. Touching it would be undirected scope expansion.

## Scope 5 — E2E smoke in a Docker-capable environment

**Not performed.** This remediation session ran in the same WSL environment
as the parent QA pass, which still has no Docker installed
(`docker: command not found`, re-confirmed). PM's own instruction
acknowledged this is a real gap, not a WSL-environment-constraint-equals-PASS
substitution: "WSL 환경 제약을 PASS로 간주하지는 않습니다." Recorded here as
`ENVIRONMENT_REQUIRED`, genuinely outstanding, not silently dropped. The
prior diff audit (Scope 1) already confirms this remediation — like the
original Markpoint fix — touches zero files under `tests/e2e/`, so there is
no reason to expect the E2E runner's own behavior to have changed; that is
a reason for lower risk, not a substitute for the smoke run itself.

## Scope 6 — Backend full suite, two consecutive runs

Fresh disposable database (`mc_qa_markpoint_verify`, native local PostgreSQL
16, recreated from `database/init.sql` + `alembic upgrade head` through
`0021` — the same disposable-DB procedure the parent QA pass used, not
reused/carried over from that session, which had already been dropped).

```text
collect-only: 405 tests (404 + 1 new deducted-side test)

Closeout Run A: 405 passed, 0 failed, 0 errors, 943 warnings, 772.22s
Closeout Run B: 405 passed, 0 failed, 0 errors, 943 warnings, 718.37s
  (immediately following Run A, same DB, no reset/recreation/selection
  change, no code change between the two)
```

Both clean on the first attempt; `KNOWN-W7-5-WAGLE-CONCURRENCY-001` did not
recur in either run. Targeted re-verification before the full-suite pair:
the 2 fixed tests + the 1 new test, 3 consecutive iterations, 3/3 passed
each time; the same 3 tests re-run under `TZ=Asia/Seoul`, `TZ=UTC`, and
`TZ=America/New_York` — **all 3 environments now pass**, closing `QA-F-003`
(previously 1/3 passed under `America/New_York`, per the parent QA report).
Core Markpoint suite (`test_markpoint_core_gap_wave5.py` +
`test_markpoint_target_wave5.py`): 64 passed (63 prior + 1 new), 96.72s.

## Baseline integrity

```text
product code modified by this task:  0 (backend/app/domains/markpoint_target/
                                       service.py untouched — no product
                                       code change was in this task's scope
                                       or needed; the fix was already
                                       verified correct)
test code modified:                   backend/tests/test_markpoint_core_gap_
                                       wave5.py only, confirmed via diff
                                       against HEAD to contain exactly the
                                       2 anchor-line replacements + 1 new
                                       appended test, 0 assertion changes
governance docs modified:             active.md, relay/current.md, the 2
                                       corrected Markpoint documents (append
                                       only, originals preserved), this
                                       handoff, its own QA evidence,
                                       COVERAGE_MAP.md
git diff --check:                     clean
existing pre-session dirty state:     unchanged (.gitignore, deleted
                                       frontend/package-lock.json, frontend/
                                       vite.config.ts, dev.sh, frontend/
                                       pnpm-lock.yaml — all this session's
                                       own earlier, unrelated dev-server
                                       setup work, not part of this task)
disposable QA database:               created, used, dropped (confirmed
                                       absent via pg_database query)
persistent local dev stack:           untouched, confirmed still responding
                                       (this session's own separate dev.sh
                                       stack on :8000/:5174)
```

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md

`CLOSEOUT GATE: PASS` means only that the four documentation obligations are
synchronized — it does NOT mean this task's own work has independent QA
PASS (this is Developer self-check, per this repository's own standing
rule that the implementer never awards its own final QA PASS), nor does it
mean Scope 5 (E2E smoke) is complete — it is explicitly not, and remains
the one genuinely open item in this task's own scope. W7.5 overall remains
`CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`; W7.6 remains
`BLOCKED`.

## Not independently measured / estimates disclosed

- Scope 5 (E2E smoke) was not performed at all — disclosed above as
  `ENVIRONMENT_REQUIRED`, not estimated or assumed.
- No independent QA has yet re-verified this closeout task's own 4
  completed scopes (1-4, 6); this handoff records Developer self-check only.

No commit, push, merge, or rebase was performed by this task.
