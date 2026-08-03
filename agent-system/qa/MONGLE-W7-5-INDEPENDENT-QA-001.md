# Task QA Evidence — MONGLE-W7-5-INDEPENDENT-QA-001

```text
Artifact Status:
RECOVERED_FROM_REPORTED_INDEPENDENT_QA_RESULT

Original Repository Artifact:
MISSING

Recovery Basis:
- 이전 독립 QA 실행 보고 (developer remediation instruction's own citation
  of a CONDITIONAL verdict and F1/F2/F3/F5 findings against this Task ID)
- 현재 코드 재현 (this recovery pass's own independent reproduction)
- Developer remediation evidence (MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001,
  self-reported REMEDIATION COMPLETE / CONDITIONAL / READY_FOR_FOCUSED_
  INDEPENDENT_RE_QA)
- 이번 focused independent re-QA 결과 (MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001)
```

**This document did not exist in this repository, in `git log --all`, or in
any task registry (`active.md`, `graduated/*.md`, `relay/current.md`) before
this recovery pass.** No original file, log, screenshot, or raw execution
record from the originally-reported Independent QA run survives anywhere
in this worktree or its history. This document does not claim to
reconstruct that original run's own exact commands, timestamps, or byte-for-
byte evidence — it distinguishes, for every claim below, whether it is:

```text
REPORTED_PREVIOUSLY        — cited only in a later task's own prose,
                              never independently confirmed by this document
INDEPENDENTLY_REPRODUCED_NOW — verified fresh, in this recovery pass or the
                              focused re-QA pass that prompted it, against
                              current source and a live disposable database
NOT_REPRODUCED              — asserted somewhere, but this document found no
                              basis to confirm or deny it
```

## 1. Original Independent QA — reported summary (REPORTED_PREVIOUSLY)

The only surviving trace of the original Independent QA run is its own
citation inside the Developer remediation task's instruction text
(`MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001`, itself carried out and
reported in this same worktree's session history). That instruction stated:

```text
Task:            MONGLE-W7-5-INDEPENDENT-QA-001
Target:          MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001
Verdict:         CONDITIONAL
```

Findings the remediation instruction described (**REPORTED_PREVIOUSLY** —
this document did not independently witness the original QA session that
produced these):

- **F1** — `GET .../wagle/board/popular?range=week` and `?range=month`
  returned HTTP 500 (`asyncpg.exceptions.DataError: invalid input for query
  argument $2: 30 (expected str, got int)`), root-caused to
  `list_popular_posts` binding an integer `days` value into
  `(:days || ' days')::interval`, a string-concatenation expression
  PostgreSQL has no `integer || text` operator for.
- **F2** — `2t` (admin notification send) had no independently reproducible
  path: it required `MONGLE_W75_ADMIN_PASSWORD`, which nothing in the
  repository generated, so an Independent QA agent following only the
  repository's own documented commands could not exercise it and it
  reported as `SKIPPED`.
- **F3** — full backend suite reproducibility across 2 consecutive runs
  showed non-identical results (`Run 1: 373 passed, 2 failed`; `Run 2: 375
  passed, 0 failed`), naming
  `test_wagle_realtime_wave3.py::test_dispatcher_never_touches_the_durable_
  message_when_delivery_fails` and
  `test_wagle_realtime_wave3.py::test_expired_lease_is_reclaimed_after_a_
  worker_dies_mid_delivery` as the non-deterministically failing tests.
- **F5** — the QA execution process itself had run `rm -rf tests/e2e/
  test-results` then `git checkout -- tests/e2e/test-results`, altering
  the pre-existing dirty/deletion state of that path from what it was when
  the QA session began.

No **F4** or **F6** finding is referenced anywhere in this repository, in
any task's own instruction text, or in any document this recovery pass
could locate. This document does **not** invent content for an F4 or F6 —
their status is **NOT_REPRODUCED / NEVER_DOCUMENTED_IN_THIS_REPOSITORY**,
stated plainly rather than filled in with a plausible-sounding guess.

## 2. Developer Remediation — summary (REPORTED_PREVIOUSLY, partially INDEPENDENTLY_REPRODUCED_NOW via the focused re-QA below)

`MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001` self-reported:

```text
Verdict: REMEDIATION COMPLETE / CONDITIONAL
Declared: READY_FOR_FOCUSED_INDEPENDENT_RE_QA
```

Its own summary: F1 fixed (5-line diff, `:days * INTERVAL '1 day'`) with 7
new regression tests; a Playwright stale-DOM false-positive fix for the
same feature's E2E coverage, which in turn surfaced a new, previously
undocumented board-room duplicate-creation race, disclosed and fixed at
the test level only; F2 resolved via a new automated runner script
(`tests/e2e/scripts/run-w75-full-spec.sh`); F3 re-run twice consecutively
(382/382 both times, count risen from 375 due to the 7 new tests); F5
restored via `git checkout --` on the one affected tracked file. Full
detail in `agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md`'s
own "Phase I" section and `engineering/phase2/
MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_REPORT.md`'s §15.

## 3. This focused Independent Re-QA — results (INDEPENDENTLY_REPRODUCED_NOW)

Full detail, exact commands, exact evidence: see this task's own record,
`agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md`. Summary:

- **F1**: independently reproduced fixed. Code audit found no trace of the
  original `(:days || ' days')::interval` pattern; a fresh isolated stack
  confirmed `week`/`month`/`all`/default all return 200, invalid range
  still 422, period filtering / cross-family isolation (403, zero leakage)
  / sort order / reaction+comment aggregation all independently verified
  against real DB state. The 7 new regression tests were read in full and
  confirmed to assert real DB-level outcomes (not status-code-only or
  mocked), then executed independently: 15/15 pass.
- **F1 Playwright evidence gap**: independently confirmed fixed by reading
  the spec file directly — a real `waitForResponse` + payload assertion +
  overlay-scoped text check now exists, structurally incapable of passing
  on a stale/empty response the way the prior page-wide text assertion was.
- **Board-room race** (the new item Developer remediation's own stricter
  test surfaced): independently audited and reproduced. `create_room`'s
  GROUP-room branch has no existing-room lookup, no unique constraint, and
  no `IntegrityError` handling — unlike its own DIRECT-room branch, which
  has all three. `wagle_rooms` carries no unique constraint on
  `(family_group_id, title)`. 10 iterations of 5 concurrent find-or-create
  requests against a fresh isolated database produced duplicate rooms in
  **10 of 10 iterations**, most producing 5 distinct rooms from 5
  concurrent requests (i.e., the check-then-act pattern caught the race
  in 0 of the requests, not merely some). **Classification: `PRODUCT_
  DEFECT`, `CODE_RESOLVABLE`.** This is more severe than the single
  Playwright test's own accidental trigger suggested — it is not a narrow
  edge case but a near-certainty under any genuine concurrent access to a
  Family's first board visit.
- **F2**: independently re-run the documented runner 4 times with no
  manual steps. 2 of 4 attempts (both run back-to-back with no pause)
  failed on disposable-Postgres-container readiness races (one silently
  swallowed `init.sql` failure via the script's own `|| true`, one
  `asyncpg.exceptions.ConnectionResetError`); 2 of 4 attempts (with a short
  pause beforehand) passed cleanly, 10/10, 0 skipped. **Not reliably
  "reproducible with zero manual steps" as claimed** — it is reproducible
  given a brief pause between invocations, which is itself an
  undocumented precondition.
- **F3**: independently re-run twice on a freshly created disposable
  database. See §4 below for exact counts (test collection independently
  confirmed at 382 before either run, not assumed from the developer's own
  reported number).
- **New finding, outside the original F1/F2/F3/F5 scope**: while auditing
  the `service_actor.py` bcrypt fix's safety per this re-QA's own Section
  12, found that `backend/app/domains/auth/service.py`'s `authenticate_
  admin` (the **legacy admin login** endpoint, `POST /api/auth/admin/
  login`, fully unauthenticated) still calls `bcrypt.checkpw` with **no
  length guard and no schema-level `max_length`** on `AdminLoginRequest.
  password` — reproduced a real 500 (`ValueError: password cannot be
  longer than 72 bytes`) using a 153-byte real JWT as the password value
  against the seeded `dad` account. The modern Account-native login
  (`family/auth_service.py`'s `verify_password`) already wraps this exact
  call in `try/except (ValueError, TypeError): return False` and was
  independently confirmed safe against the same input; the legacy player
  PIN login is schema-bounded to 4 characters and is not exposed to this
  class of input at all. This is a live, reachable, unauthenticated
  robustness defect the F1 remediation did not address because it never
  touched `auth/service.py`.

## 4. Backend full-suite reproducibility (INDEPENDENTLY_REPRODUCED_NOW)

Test collection was independently counted before either run (`pytest -q
--collect-only`) rather than trusting the developer's own reported number:
**382 tests collected**, confirmed to equal 375 (the pre-F1 count) + 7 (the
new Popular Posts regression tests added by the remediation), matching
independently.

Both runs used a dedicated, disposable `postgres:16.9-alpine` container
(`mc_qa_suite_db`, port 15488, `database/init.sql` + `alembic upgrade
head`), never the shared `mc_phase0`/`mc_phase1` stacks or the persistent
dev DB, torn down after both runs completed.

```text
RUN_ID:      QA-BACKEND-FULL-001
DATE_TIME:   2026-08-03 21:14:20 KST
HEAD:        f8003c50f2db4df5f3af1276f921812038cfb3bc
Python:      3.11.15
Postgres:    16.9 (aarch64-unknown-linux-musl, Alpine)
COMMAND:     DATABASE_URL=<throwaway :15488> JWT_SECRET=<throwaway>
             python3.11 -m pytest -q   (backend/)
RESULT:      382 passed, 0 failed, 0 errors, 1 warning (unrelated Pydantic
             deprecation), 375.80s

RUN_ID:      QA-BACKEND-FULL-002 (same DB, immediately following run 1)
DATE_TIME:   2026-08-03 21:20:52 KST
HEAD:        f8003c50f2db4df5f3af1276f921812038cfb3bc (unchanged)
COMMAND:     identical to run 1, fresh JWT_SECRET only
RESULT:      382 passed, 0 failed, 0 errors, 1 warning (same), 376.37s
```

**Both runs fully clean, identical results — independently confirms the
developer's own reported 382/382 twice.** `KNOWN-W7-5-WAGLE-CONCURRENCY-001`
did not manifest in either of these 2 runs, consistent with (not
contradicting) its own documented intermittent shape across the task's
full run history — 2 more clean runs narrow, but do not retire, that
already-registered condition. `FULL_SUITE_REPRODUCIBILITY: PASS` for these
2 runs specifically; the condition itself remains `KNOWN_CONDITION`, not
declared resolved.

## 5. Unresolved items as of this recovery

- Board-room GROUP-type duplicate-creation defect — confirmed `PRODUCT_
  DEFECT`, not yet fixed in product code (only test-level mitigation
  exists). Per this task's own directive, this blocks moving to W7.6
  until addressed.
- Legacy admin-login bcrypt length-guard gap — confirmed live defect,
  newly found, not yet triaged or scheduled.
- F2 runner reliability under rapid re-invocation — confirmed real but
  narrower than a product defect; a documentation/tooling robustness gap.
- The 13 PM/design gates and 1 infrastructure gate from the original
  W7.5 Decision Package remain untouched and unresolved by this QA pass,
  as expected — this pass's scope was Developer remediation verification
  only.

## 6. Final verdict for this recovered artifact

See `agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md` for the
authoritative, current verdict. This recovered document is a traceability
record, not itself a new judgment — it exists so a reader following the
citation chain (`W7-5-DATA-AND-BEHAVIOR-WIRING-001` →
`W7-5-INDEPENDENT-QA-001` → `W7-5-INDEPENDENT-QA-REMEDIATION-001` →
`W7-5-FOCUSED-INDEPENDENT-RE-QA-001`) finds a real file at every link,
honestly labeled where the chain's second link could not be reconstructed
from anything other than later tasks' own citations of it.
