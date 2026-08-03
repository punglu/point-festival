# Task QA Evidence — MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001

```text
Task:
MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001

Targets:
MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001
MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001

Verdict:
FAIL
```

**Verdict is FAIL, driven by exactly one item: the board-room duplicate-
creation race is a confirmed, reproducible `PRODUCT_DEFECT`, not a `KNOWN_
CONDITION`.** Per this task's own governing instruction, a confirmed
product defect here blocks moving to W7.6 until fixed — it is reported as
FAIL rather than CONDITIONAL specifically so it is not read as "safe to
proceed." Every other item independently verified this pass (F1's fix,
its regression tests, its Playwright evidence-gap fix, `2t`'s
reproducibility given a documented precondition, 2 consecutive clean
backend suite runs, the 3×3 viewport regression) is genuinely clean. Two
additional findings outside the original F1/F2/F3/F5 scope are also
reported per this task's own Omission Guard.

## Baseline

```text
worktree:   /Users/mac/mac_Project/mongle_ui
branch:     dev-newmarkp
HEAD:       f8003c50f2db4df5f3af1276f921812038cfb3bc  (start == end, unchanged)
dirty at start: 18 tracked modified + 2 untracked (BrandCharacter/, a
  pre-existing unrelated `_scratch_screen_audit.cjs` scratch file left
  over from an earlier, unrelated ad hoc session)
untracked at start: frontend/src/shared/components/BrandCharacter/,
  tests/e2e/_scratch_screen_audit.cjs, tests/e2e/scripts/run-w75-full-spec.sh
stash: none (start and end)
start manifest: SHA-256 of 13 key files recorded before any QA action
end manifest: identical hashes on all 13 files except
  tests/e2e/test-results/.last-run.json (see Baseline Integrity below) —
  zero product-code, test-code, migration, or seed changes made by this
  QA pass
QA modifications: 2 new files only —
  agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-001.md (recovered artifact)
  agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md (this file)
```

## Traceability Recovery

```text
Original QA artifact:     agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-001.md
Recovery status:          RECOVERED_FROM_REPORTED_INDEPENDENT_QA_RESULT
Recovery basis:           prior task's own citation of the original verdict
                          and F1/F2/F3/F5 findings; this pass's own fresh
                          reproduction; Developer remediation's own report
Recovered document path:  agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-001.md
Limitations:              no original file, log, screenshot, or raw
                          execution record survives anywhere in this
                          repository or its git history; F4/F6 (named in
                          this task's own instruction template) have no
                          basis anywhere and are recorded as
                          NOT_REPRODUCED / NEVER_DOCUMENTED, not invented
```

## Popular Posts (F1)

All independently re-verified against a fresh disposable Postgres +
throwaway backend (`mc_qa_f1_db`, port 15489, torn down after use), using
real accounts (`owner.a` / Family Alpha, `member.b` / Family Beta with a
Wagle role and subscription seeded directly for this test since Beta had
neither by default).

```text
week:            200 — post present, correct reaction/comment counts
month:           200 — post present, correct reaction/comment counts
all:              200 — includes the 45-day-backdated post that week/month exclude
default:          200 — hits the identical week-range code path (router default)
invalid:          422 — Literal["week","month","all"] validation, unchanged
cross-family:     403 ("활성 가족 구성원 권한이 필요합니다") — a Family-B
                  member cannot reach Family-A's popular endpoint at all;
                  Family-B's own popular endpoint independently confirmed
                  to return [] with zero Family-A data present
period:           PASS — week/month correctly exclude a 45-day-backdated
                  post; all correctly includes it
sorting:          PASS — a post with combined score 2 (1 reaction + 1
                  comment tie) ranks above two score-0 posts, tie-broken
                  by created_at DESC
reaction count:   PASS — exact count (1) confirmed after one toggle
comment count:    PASS — exact count (1) confirmed after one reply
empty:            PASS (re-confirmed conceptually from Developer's own
                  evidence and this task's own code read of the `if
                  board_room is None: return []` early-exit path)
500 occurrences:  0 across every case tested
```

Code audit (`backend/app/domains/wagle/service.py::list_popular_posts`):
the old `(:days || ' days')::interval` string-concatenation pattern is
gone; the fix (`:days * INTERVAL '1 day'`) keeps `days` a genuine bound
parameter, contains no string-built SQL, and the inline comment's stated
intent matches the query exactly. Family scope (`board_room` resolved via
`WagleRoom.family_group_id == family_id`) is unchanged by the fix.

## Test Verification

```text
Popular focused tests:  15/15 pass (8 pre-existing + 7 new). Audited the
  7 new tests' own assertion bodies line by line: every one asserts real
  HTTP status plus real response-payload content (message_id membership,
  exact reaction_count/comment_count values, membership in/out of a
  date-filtered list) against a real PostgreSQL/asyncpg backend — no
  mocks, no status-code-only assertions. Not a TEST_DEFECT pattern.
  (Per this task's own instruction, the fix was NOT reverted by this QA
  pass to re-confirm the developer's own "revert reproduces the original
  error" claim — that claim is recorded as REPORTED_PREVIOUSLY, not
  independently re-verified by this pass, to avoid risking dirty-worktree
  damage.)

Playwright (04-w75-data-wiring.spec.ts, 3c/3d/3e block): read directly.
  Confirmed present: `page.waitForResponse(...'/wagle/board/popular'...)`,
  `expect(popularResponse.status()).toBe(200)`,
  `expect(popularPayload.some(p => p.message_id === postId)).toBeTruthy()`,
  and every subsequent visibility assertion scoped to
  `page.getByTestId('wagle-board-popular-overlay')`, never the page at
  large. Structurally incapable of passing on a 500 or an empty fallback
  the way the prior page-wide `page.getByText(postTitle)` assertion was.

Backend Run 1: 382 passed, 0 failed, 0 errors, 375.80s
  (mc_qa_suite_db, port 15488, HEAD f8003c5, 2026-08-03 21:14:20 KST)
Backend Run 2: 382 passed, 0 failed, 0 errors, 376.37s
  (same DB, immediately following, 2026-08-03 21:20:52 KST)
  Test count independently collected via `pytest --collect-only` before
  either run: 382 (not trusted from developer's own report).

Static:
  Typecheck (tsc --noEmit):     PASS, clean
  Lint (npm run lint / eslint): PASS, clean
  Build (vite build):           PASS, clean, 1.01s
  git diff --check:             PASS, 0 whitespace errors
  agent-system/tools/check_all.py: PASS, 0 W7.5-specific warnings
```

## 2t / F2 Reproducibility

Ran `tests/e2e/scripts/run-w75-full-spec.sh` exactly as documented in
`tests/README.md`, with no prior manual setup, **4 independent times**:

```text
Attempt 1 (cold start):        FAILED — "relation admin_auth does not
  exist". Root cause: the script's own `docker exec -i ... < database/
  init.sql >/dev/null 2>&1 || true` (line 64) silently swallowed a load
  failure (the disposable Postgres container was not yet fully ready to
  accept schema-creation commands despite `pg_isready` reporting ready);
  `0000_legacy_schema_baseline` is an intentional Alembic no-op assuming
  init.sql already ran, so `admin_auth` (an init.sql-only table, not
  created by any migration) never existed, and the later `UPDATE
  admin_auth SET password = ...` step crashed with an uninformative error
  that gives no hint of the real, silently-swallowed root cause.
Attempt 2 (immediately after):  FAILED — asyncpg.exceptions.
  ConnectionResetError during `alembic upgrade head`'s own DB connection,
  again consistent with the freshly-started disposable Postgres container
  not yet being fully ready, immediately following attempt 1's teardown.
Attempt 3 (after ~5s pause):    PASSED — 10 passed, 0 skipped, 0 failed, 16.8s
Attempt 4 (after ~5s pause):    PASSED — 10 passed, 0 skipped, 0 failed, 16.8s
```

**Finding**: the runner is reliable given a short pause between
invocations, but is **not** reliably "reproducible with zero manual
steps" as `tests/README.md` states without qualification — 2 of 4
attempts run back-to-back failed on disposable-database startup timing,
not on anything related to `2t` or the application itself. This is a
tooling/documentation robustness gap, not a product defect: no attempt
that reached the actual Playwright run ever produced anything but
10/10, 0 skipped. Per this QA role's restriction, the script itself was
not modified to add a readiness-wait fix; the gap is reported for
Developer or PM disposition. Verified during the passing runs: the
admin password is generated locally, its bcrypt hash is written directly
into the disposable DB, the plaintext exists only in the script's own
process environment for the one Playwright invocation, and it is not
present in `/tmp/mc_w75_spec_runner_backend.log` or
`/tmp/mc_w75_spec_runner_frontend.log` (checked directly, both times).

## Board Room Race

```text
Concurrency method:     5 concurrent async HTTP clients per iteration,
                        each independently logging in as owner.a (fresh
                        device_id) and performing the app's own exact
                        find-or-create sequence (GET rooms, filter by
                        title, POST create if none found) against a
                        freshly seeded disposable database
                        (mc_qa_f1_db, port 15489)
Iterations:              10, each targeting a distinct, never-before-seen
                        room title (__qa_race_room_<i>__) to guarantee a
                        genuine first-creation race each time
Requests per iteration:  5
Duplicate rows:          10 of 10 iterations produced more than 1 distinct
                        room ID for the same title; 9 of 10 iterations
                        produced exactly 5 distinct rooms (i.e., every
                        single one of the 5 concurrent requests created
                        its own separate room — the existing-room check
                        caught the race in 0 of 5 requests, not merely
                        some)
Different IDs:           yes, per above — no request ever received a
                        shared/deduplicated room ID from a concurrent
                        peer
Errors:                  0 (no 500s, no IntegrityErrors surfaced to any
                        caller — the duplication is entirely silent)
Final classification:    PRODUCT_DEFECT, CODE_RESOLVABLE
Product impact:          `wagle_rooms` has no unique constraint on
                        `(family_group_id, title)`; `create_room`'s GROUP-
                        type branch (used by the `__family_board__`
                        sentinel) has no existing-room lookup and no
                        IntegrityError handling at all, unlike its own
                        DIRECT-type branch, which has both a pre-check
                        query and a proper rollback-and-refetch pattern on
                        IntegrityError. Any two genuinely concurrent first
                        visits to a Family's board (two browser tabs, two
                        devices, or the frontend's own mount effect racing
                        this task's own Playwright test script, as
                        Developer remediation's own work discovered) will,
                        essentially always under real concurrency, create
                        multiple `__family_board__` rooms. `list_popular_
                        posts`'s own `WHERE title = ... .scalars().first()`
                        lookup then has no way to know which duplicate
                        holds the real content, and can silently rank an
                        empty or wrong room — the exact failure mode
                        Developer's own Playwright fix exposed, now proven
                        far more severe (near-certain under concurrency,
                        not a rare timing accident) than a single test
                        run could show.
```

This is a genuine, reproducible defect. Per this task's own governing
instruction ("board room race가 실제 제품 결함으로 확인되면 W7.6으로
넘어가지 말고 먼저 수정해야 합니다"), this is the basis for the overall
`FAIL` verdict.

## bcrypt Fix Focused Audit (Section 12)

`service_actor.py`'s length guard (`len(secret_bytes) > 72`) is correctly
placed before both `bcrypt.checkpw` call sites, applies only to the
Service-Principal ingress path, does not weaken any check, and does not
introduce a meaningful timing oracle (an oversized-input rejection reveals
only that the caller's own input was too long, not anything about
credential validity). `test_wagle_service_binding.py::test_01_user_jwt_
blocked_from_service_ingress` independently confirmed to exercise exactly
this path and pass. No `TEST_COVERAGE_CONCERN` for this specific fix — a
real, pre-existing, still-passing test protects it.

**New finding, independently discovered while performing this exact
audit** (outside F1/F2/F3/F5's declared scope, but squarely inside
Section 12's own instruction to check whether the bcrypt fix's *sibling*
paths are safe): `backend/app/domains/auth/service.py::authenticate_admin`
(the legacy admin login endpoint, `POST /api/auth/admin/login`, fully
unauthenticated) still calls `bcrypt.checkpw` with **no length guard**,
and `AdminLoginRequest.password: str` (`backend/app/domains/auth/
schema.py`) has **no `max_length`** at all. Reproduced directly: a 100-byte
ASCII password against a non-existent username correctly short-circuits
to 401 before reaching bcrypt (the `if not admin: raise 401` check runs
first), but the same oversized value against a genuinely seeded admin
account (`dad`, restored via `database/init.sql` after this QA's own
earlier full-suite run had truncated it) produces:

```text
ValueError: password cannot be longer than 72 bytes, truncate manually if
necessary (e.g. my_password[:72])
  at backend/app/domains/auth/service.py:189, in authenticate_admin
```

This endpoint requires no prior authentication to reach — any caller who
can guess or already knows a valid admin username (`dad`/`mom` are the
only two seeded) can trigger this 500 with zero valid credentials.
Checked the two sibling paths for the same class of defect: the modern
Account-native login (`family/auth_service.py::verify_password`) already
wraps the identical `bcrypt.checkpw` call in `try/except (ValueError,
TypeError): return False` and was independently confirmed safe against
the same 150-byte input (returns a clean 401); the legacy player PIN login
(`LoginRequest.pin`) is schema-bounded to exactly 4 characters and cannot
be exposed to this input shape at all. This is a live, reachable,
previously undocumented defect the F1/bcrypt remediation did not address
because it never touched `auth/service.py`. Reported as a Finding, not
fixed, per this QA role's restriction.

## Wagle Focused 3×3 Viewport Regression

```text
Viewports:  390×844, 820×1180, 1180×820
Screens:    3c (board post), 3d (comment), 3e (reaction + Popular Posts)
```

Independently re-implemented (not reusing Developer's own since-deleted
script) against a fresh disposable stack (port 18093/5193/15487, torn
down after use). All 9 checks (3 screens × 3 viewports) clean:

```text
Fatal errors:          0
Horizontal overflow:   0 (checked after board load, after post appears,
                       after comment thread renders, and after the
                       Popular overlay opens — 4 checkpoints × 3 viewports)
Popular endpoint 500s: 0 — every viewport's Popular fetch returned 200
                       with the test's own post present in the payload
Console/page errors:   0
```

`FULL_W7_4_PRODUCT_ENTRY_64: DEFERRED`. `FULL_W7_4_RESPONSIVE_192:
DEFERRED_TO_W7_6_INTEGRATED_REGRESSION`. Neither is claimed as executed by
this pass.

## Baseline Integrity

```text
Product code modified by QA:   0 (SHA-256 identical to start-of-QA
  manifest for backend/app/domains/wagle/service.py and every other
  product file checked)
Test code modified by QA:      0 (SHA-256 identical for
  backend/tests/test_w75_phase_d_board_reactions.py,
  tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts,
  tests/e2e/scripts/run-w75-full-spec.sh)
Dirty files damaged:           0 — the 18 tracked-modified files and the
  BrandCharacter/ + run-w75-full-spec.sh untracked entries present at QA
  start remain exactly as they were; the pre-existing, unrelated
  tests/e2e/_scratch_screen_audit.cjs scratch file (present before this
  QA task began, from an earlier unrelated session) was left untouched,
  not deleted, per this task's own no-cleanup-of-existing-files posture
test-results residue:          tests/e2e/test-results/.last-run.json
  drifted from HEAD's committed value during this QA pass's own 4
  Playwright executions (each run of `run-w75-full-spec.sh` regenerates
  this file as a documented side effect) — NOT restored via `git
  checkout --`, per this task's own explicit prohibition on QA
  performing that restoration. This is expected, previously-disclosed
  runtime-artifact drift (the same behavior Developer's own remediation
  pass documented and repeatedly restored), not a novel `QA_PROCESS_
  INCIDENT` — recorded here factually rather than either hidden or
  treated as new damage. No other file under tests/e2e/test-results/
  shows drift; no leftover per-test artifact directories exist (each
  Playwright run's own start clears this directory).
Credential residue:            0 — no plaintext secret found in any log
  file this QA pass produced; the F2 runner's own admin password was
  confirmed absent from both its backend and frontend logs
Temporary infra:               all disposable containers (mc_qa_f1_db,
  mc_qa_suite_db, mc_qa_viewport_db) and all throwaway backend/frontend
  processes started by this QA pass confirmed removed via `docker ps -a`
  and `lsof` immediately after each use; persistent dev stack
  (mongle-db-1/mongle-backend-1/mongle-frontend-1) untouched throughout
```

## Documentation

```text
Matrix:                 unchanged by this QA pass (F1/F2/F3/F5 and this
  pass's own findings change no screen-wiring status; correctly left
  untouched)
Report:                 read, cross-checked, unchanged by this QA pass
  (§15's own F1/F2/F3/F5 summary matches this pass's independent findings
  wherever both cover the same claim)
Decision Package:       read, cross-checked — 13 PM/design gates + 1
  infrastructure gate = 14 total, consistent across every location
  checked (Decision Package itself, active.md, Handoff)
Developer QA:            read in full (agent-system/qa/MONGLE-W7-5-
  DATA-AND-BEHAVIOR-WIRING-001.md's own "Phase I" section) — 382 test
  count, 7 new tests, and the board-room-race disclosure all
  independently confirmed accurate; not modified by this QA pass
Recovered Independent QA: agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-001.md
  — new this pass, per Section 5's own instruction
Handoff:                 read, cross-checked, unchanged by this QA pass
Coverage Map:            read, cross-checked (382/382 figures, 13-run
  KNOWN_CONDITION history, `E2E-W7-5-FULL-SPEC-001`/`API-W7-5-BOARD-
  REACTIONS-001` rows) — all consistent with this pass's own findings;
  not modified by this QA pass (this pass's own 2 additional clean
  backend runs and the board-room-race/legacy-admin-bcrypt findings are
  recorded in this report instead, for Developer or PM to fold into the
  Map on its next legitimate update)
Active:                  read, cross-checked, unchanged by this QA pass
Relay:                   read, cross-checked, unchanged by this QA pass
README:                  read — confirmed the F2 runner's documented
  "Expected result: 10 passed, 0 skipped, 0 failed" does not disclose the
  rapid-re-invocation flakiness this pass found; a precision gap, not a
  false statement (the claim is true once the DB is actually ready)
```

## Findings

```text
ID:                    RE-QA-F-BOARD-ROOM-RACE
Severity:              HIGH
Category:              product-defect
File/test:             backend/app/domains/wagle/service.py::create_room
                        (GROUP-room branch); wagle_rooms table (no unique
                        constraint on family_group_id+title)
Evidence:               10/10 concurrency iterations produced duplicate
                        rooms; see "Board Room Race" section above for
                        full method and counts
Reproduction:           5 concurrent async HTTP clients per iteration,
                        10 iterations, against a fresh disposable DB;
                        script used for reproduction was written fresh
                        for this QA pass and is not part of the
                        repository's own test suite
Impact:                 list_popular_posts and any other title-based
                        board-room lookup can silently resolve to the
                        wrong (possibly empty) duplicate room; affects
                        real concurrent multi-device/multi-tab usage,
                        not only test execution
Required remediation:   a unique constraint on wagle_rooms
                        (family_group_id, title) where title is the
                        reserved sentinel (new migration required, out
                        of this and the prior remediation's declared
                        scope) plus an IntegrityError-based get-or-create
                        retry in create_room's GROUP branch, matching the
                        pattern its own DIRECT branch already uses
```

```text
ID:                    RE-QA-F-ADMIN-LOGIN-BCRYPT
Severity:              MEDIUM
Category:              product-defect (availability/robustness, not an
                        authentication bypass)
File/test:              backend/app/domains/auth/service.py:189
                        (authenticate_admin); backend/app/domains/auth/
                        schema.py (AdminLoginRequest.password, no
                        max_length)
Evidence:               reproduced 500 with a 153-byte real JWT as the
                        password value against the seeded "dad" account;
                        exact traceback recorded above
Reproduction:           POST /api/auth/admin/login with
                        {"username": "dad", "password": "<>72 bytes>"}
                        against any environment with a real admin_auth
                        row for that username
Impact:                 unauthenticated callers who know or guess a valid
                        admin username can trigger repeated 500s; no
                        authentication bypass (never grants a session)
Required remediation:   add max_length to AdminLoginRequest.password (or
                        the same try/except pattern already used in
                        family/auth_service.py::verify_password)
```

```text
ID:                    RE-QA-F-2T-RUNNER-FLAKY
Severity:              LOW
Category:              test-infrastructure / documentation precision
File/test:              tests/e2e/scripts/run-w75-full-spec.sh;
                        tests/README.md
Evidence:               2 of 4 independent runs failed on back-to-back
                        invocation; see "2t / F2 Reproducibility" above
Reproduction:           run the script twice in immediate succession
                        with no pause
Impact:                 a QA agent following only the documented command
                        with no additional knowledge has a real chance of
                        hitting a confusing failure unrelated to the
                        actual test content
Required remediation:   either a readiness-wait loop before init.sql load
                        (matching the pg_isready loop already used for
                        the backend/frontend readiness checks) or an
                        explicit documented pause between consecutive
                        invocations
```

## 5-Gate Independent QA Self-Check

- **Hallucination Guard**: no Developer-reported number was copied without
  independent re-derivation — the 382 test count was re-collected via
  `pytest --collect-only`, not assumed; the "10/10" F2 claim was
  re-executed 4 times, not read as-is; the board-room race was
  independently reproduced with a fresh concurrency script, not inferred
  from Developer's own single-test disclosure; F4/F6 (named in this
  task's own instruction template) are explicitly marked NOT_REPRODUCED
  rather than invented.
- **Omission Guard**: 3 findings are reported beyond the declared F1/F2/
  F3/F5 scope (board-room race severity re-classification, the sibling
  legacy-admin bcrypt defect, F2 runner flakiness) — none were folded
  silently into a passing summary.
- **Miswork Guard**: zero product code changes, zero test code changes,
  zero migration/seed changes made by this QA pass — verified by SHA-256
  comparison against the start-of-QA manifest, not merely asserted. The
  fix was not reverted to re-confirm Developer's own revert-and-reconfirm
  claim, per this task's own explicit restriction.
- **Axis Alignment**: F1 independently confirmed fixed does not imply
  W7.5 overall PASS; 2 clean backend runs do not imply
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001` is resolved; test-level serialization
  of the board-room lookup (Developer's own `waitForLoadState`
  workaround) is explicitly not conflated with the underlying product
  race being fixed; a 3-viewport clean regression is not represented as
  the full 192-combination sweep; the recovered Independent QA document
  is labeled as recovered, never presented as if the original artifact
  had been found.
- **Freshness/Evidence Consistency**: every count and status in this
  report was produced by a command run in this session against current
  HEAD (`f8003c5`) and live disposable databases/browsers, not carried
  forward from either the Developer remediation's own report or the
  citation of the original Independent QA run.

## Final Declaration

```text
MONGLE_W7_5_FOCUSED_INDEPENDENT_RE_QA_FAIL
POPULAR_POSTS_DEFECT_INDEPENDENTLY_VERIFIED_FIXED
POPULAR_POSTS_REGRESSION_COVERAGE_INDEPENDENTLY_VERIFIED
PLAYWRIGHT_2T_REPRODUCIBILITY_INDEPENDENTLY_VERIFIED_WITH_CAVEAT
BACKEND_FULL_SUITE_REPRODUCED_TWICE
QA_TRACEABILITY_ARTIFACT_RECOVERED
BOARD_ROOM_RACE_CONFIRMED_PRODUCT_DEFECT — BLOCKS_W7_6_UNTIL_FIXED
NEW_FINDING_ADMIN_LOGIN_BCRYPT_500 — UNADDRESSED
OVERALL_W7_5_REMAINS_CONDITIONAL_HUMAN_GATE
NOT_READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION
```

Not declared, per this task's own explicit restriction, regardless of the
above: `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`FULL_PRODUCT_BEHAVIOR_WIRING_COMPLETE`, `PM_DECISIONS_RESOLVED`,
`W7_4_PRODUCT_ENTRY_64_OF_64_REVERIFIED`,
`W7_4_RESPONSIVE_192_OF_192_REVERIFIED`. Overall W7.5 remains `CONDITIONAL
/ HUMAN_GATE`. Recommended next step: a bounded fix task for the board-room
race (and, at PM's discretion, the newly found admin-login bcrypt gap)
before any W7.6 common-component extraction work begins. Commit and push
were not performed.
