# MONGLE_NARAN_REMAINING_ALLOWLIST

TASK ID: MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001

## Search command and scope

```
grep -rniIE "naran|나란" . \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=test-results --exclude-dir=.pytest_cache
find . -iname "*naran*" -not -path "./.git/*" -not -path "*/node_modules/*" -not -path "*/test-results/*"
```

Run before Pass 2 (189 content occurrences across 27 files, 16 filename/dirname matches) and again after Pass 2 (residual, below).

## Residual occurrence count (after Pass 2)

157 content-line occurrences across 20 files. Every one classified below — **zero unclassified, zero `ACTIVE_INTERNAL_RENAME` leftovers, zero `UNKNOWN_REQUIRES_GATE`.**

## Classification table

| File | Occurrence type | Classification | Reason kept |
|---|---|---|---|
| `frontend/src/App.tsx` | `/naran/doran`, `/naran/family` route path strings (×2) | `ROUTE_CONTRACT_KEEP` | URL/route contract — explicit prohibition, out of scope (see follow-up task) |
| `frontend/src/platform/shell/MongleAppShell.tsx` | `/naran/doran`, `/naran/family` route strings (×6) | `ROUTE_CONTRACT_KEEP` | Same |
| `tests/e2e/specs-mongle/01-shell.spec.ts` | `/naran/doran`, `/naran/family` in `page.goto(...)` (×3) | `ROUTE_CONTRACT_KEEP` | Same — test inputs mirror the real route, not renamed |
| `frontend/src/shared/stores/useFamilyContextStore.ts:20` | `` `naran.activeFamily.${accountId}` `` localStorage key | `EXTERNAL_OR_PERSISTED_CONTRACT` | Persisted browser storage key — renaming would silently reset every existing user's selected-Family state on their next visit. Explicitly named as an off-limits category (§3.C) requiring a dedicated PM-approved migration, not a side effect of this task. **Not touched.** |
| `agent-system/handoffs/archive/2026-07/PHASE1-NARAN-PLATFORM-SHELL-001.md` | Entire file: Task ID, filename, body | `HISTORICAL_RECORD_KEEP` | Archived, `Lifecycle: COMPLETED` handoff tied to specific commit hashes (`9cce458...`→`1f3b839...`). Task ID and archive filenames are permanent, per §3.E. |
| `agent-system/qa/PHASE1-NARAN-PLATFORM-SHELL-001.md` | Entire file: Task ID, filename, body | `HISTORICAL_RECORD_KEEP` | QA evidence record for the same Task ID, same reasoning. |
| `agent-system/graduated/2026-07.md:17` | Ledger row citing `PHASE1-NARAN-PLATFORM-SHELL-001`, "Naran Shell..." description | `HISTORICAL_RECORD_KEEP` | Graduated-task ledger row, commit-anchored (`1f3b839`), Task-ID keyed. |
| `agent-system/qa/COVERAGE_MAP.md` — Journey ID `E2E-NARAN-SHELL-001` + prose | `HISTORICAL_RECORD_KEEP` (ID/prose) | Ledger primary key + dated evidence description, commit-anchored (`1f3b839a3c...`). Not renamed, matching the Task-ID precedent. |
| `agent-system/qa/COVERAGE_MAP.md` — 2 file-path cells in the same row | `CURRENT_DOC_UPDATE` (already applied) | The two paths (`specs-naran/01-shell.spec.ts`, `playwright.naran.config.ts`) were mechanically updated to their new `specs-mongle`/`playwright.mongle.config.ts` locations so the "index, not a backlog" stays accurate — with an inline note explaining the discrepancy with the (unchanged) historical ID/prose. The third path, `tests/e2e/naran-shell-capture-manifest.md`, was **not** renamed (see next row) so it is left as-is. |
| `tests/e2e/naran-shell-capture-manifest.md` | Entire file: title, body, all rows | `HISTORICAL_RECORD_KEEP` | Evidence manifest pinned to one `source_commit` (`9cce458...`) describing PNG captures that were literally labeled "Naran Shell" at that commit. Not a live/regenerated template — renaming would misrepresent what was actually captured. |
| `engineering/phase2/DORAN_FOUNDATION_GAP_ANALYSIS.md:29` | "...Naran Shell 25/25..." self-test evidence quote | `HISTORICAL_RECORD_KEEP` | Dated addendum (`R2-B2 addendum (2026-07-26)`) quoting a specific self-test result count under the name the Shell had at that time. Changing the quoted name would misrepresent historical evidence. |
| `engineering/phase2/FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md` | 8 occurrences: "나란 공통 시각 foundation", "확정 명칭은 플랫폼 나란", "나란·도란·마크포인트" etc. | `HISTORICAL_RECORD_KEEP` (flagged for PM awareness, not a blocker) | Commit-pinned (`origin/dev @ 1dbbec5...`), dated (`2026-07-26`) design-contract snapshot; its own §1.3 authority table states later explicit PM decisions override its recorded naming. Treated conservatively as a frozen snapshot rather than rewritten — see note below. |
| `engineering/phase2/DORAN_MESSAGING_CONTRACT.md:15` | "Naran is the Platform, Doran is its..." | `CURRENT_DOC_UPDATE` (already applied) | `Status: APPROVED CONTRACT / canonical R2` — a live canonical document explaining current architecture. Updated to "Mongle is the Platform..."; `doran.*`/`doran_*`/`room_admin` contract text on the same line is untouched. |
| `engineering/phase2/DORAN_PERFORMANCE_AND_SYNC.md:78` | "completed Naran Shell DOM audit..." | `CURRENT_DOC_UPDATE` (already applied) | Same canonical-R2 status; updated to "Mongle Shell". |
| `engineering/phase1/ACCOUNT_FAMILY_RBAC_CONTRACT.md:10` | "...target authorization contract for the Naran platform." | `CURRENT_DOC_UPDATE` (already applied) | `Status: APPROVED DECISIONS / v0.1` — live current contract; updated to "Mongle platform". |
| `engineering/phase2/MONGLE_ROUTE_AUDIT.md`, `MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`, `MONGLE_NAMING_INVENTORY.md`, `MONGLE_FE_ROUTE_ALIGNMENT_REPORT.md`, `MONGLE_E2E_DORAN_SUBSCRIPTION_SEED_ALIGNMENT_REPORT.md`, `MONGLE_FE_E2E_HARNESS_RESTORE_REPORT.md` | Dense `NaranAppShell.tsx:NNN`-style evidence citations, `specs-naran` path references | `APPROVED_DOCUMENTED_EXCEPTION` | These are dated, git-state-anchored investigative reports (each with its own Start Gate, HEAD, verdict). Rewriting dozens of exact file:line citations risks introducing transcription errors into evidence tables. Per the task's own explicit escape hatch ("필요한 경우 수정 대신 supplement/note를 추가"), a short namespace-rename supplement note was added near the top of each of these 6 files instead of retroactively editing every citation. |
| `CLAUDE.md:581` | "...나란히 배치" | `NOT_A_NARAN_OCCURRENCE` (false positive) | The Korean adverb "나란히" (side-by-side) contains "나란" as a substring but is grammatically and semantically unrelated to the "나란" brand name. Confirmed by reading full sentence context. Not touched. |
| `frontend/index.html:22,27`, `frontend/public/manifest.json:4` | "...나란히 연결하는 플랫폼..." | `NOT_A_NARAN_OCCURRENCE` (false positive) | Same adverb, same reasoning. |
| `backend/scripts/phase1_seed_synthetic.py:76` | Code comment quoting the route `/naran/doran` | `ROUTE_CONTRACT_KEEP` | Comment accurately describes the still-valid, unchanged route. |
| `tests/e2e/scripts/start-mongle-phase1.sh`, `stop-mongle-phase1.sh`, `mongle-phase1-teardown.ts` | No remaining `naran` text (renamed to `mongle-phase1-*` and cross-references updated) | N/A — fully renamed, listed only to confirm 0 residual | — |

## `/naran` route: why it stays (explicit, per task §3.B)

`/naran/doran` and `/naran/family` are live, reachable, user-facing URLs (confirmed reachable and unbroken by the cold-start E2E runs in this task and the two preceding tasks). Renaming a URL changes what users, bookmarks, and any external references resolve to — a materially different and riskier class of change than an internal symbol rename. Per the task's explicit boundary (§3.B) and its own named follow-up (`MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001`), this is out of scope here.

## Historical records: why they stay (explicit, per task §3.E)

Task IDs (`PHASE1-NARAN-PLATFORM-SHELL-001`, `E2E-NARAN-SHELL-001`), archived handoff/QA filenames, and commit-anchored evidence quotes are permanent identifiers of *what happened, when, under what name, verified by whom*. Rewriting them to use the platform's current name would misrepresent the historical record — e.g. `DORAN_FOUNDATION_GAP_ANALYSIS.md`'s "Naran Shell 25/25" is a direct citation of a self-test's own output at a specific commit; the Shell really was called that at the time the test ran.

## Persisted/infra contract discovery: full result

Systematically checked and found **clear** (no `naran` occurrences) in: `nginx.conf`, `vite.config.ts`, `docker-compose.yml`, `docker-compose.prod.yml`, `docker-compose.phase1.yml`, `.env.phase0.example`, `frontend/public/manifest.json`'s `id`/`start_url`/`scope` fields, all `backend/app/**.py` application code, all DB models/migrations. The **only** persisted-key match found anywhere in the repository is the single `localStorage` key documented above — everything else in the EXTERNAL_OR_PERSISTED_CONTRACT category (Docker volume/network names, PWA identity fields, CI/CD config) was searched and confirmed absent, not assumed absent.

## Follow-up recommendation (not executed, per task instruction to only propose)

`MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001` — scope: `/naran/...` → new canonical URL policy, legacy-path redirect, deep-link compatibility, PWA `start_url`/`scope`/`id` implications, and (separately, likely its own even-later task) a deliberate, impact-analyzed `localStorage` key migration for `naran.activeFamily.*` with a read-old-key-then-write-new-key fallback so existing users don't silently lose their selected Family on the day of the switch.
