# Current Relay

Current Task: MONGLE-W6-1-GOVERNANCE-AND-AVATAR-FIX-001 (PM-directed, this session)

- Status: IN PROGRESS — PM issued a multi-part decision covering (1) a Wave 6.1
  Foundation E2E Closeout Addendum, (2) independent QA dispatch for three
  Wave 6.1 tasks, (3) A1 visual code fixes in the isolated A1 worktree, (4) a
  new Avatar status-dot clipping fix task, (5) task registration for a
  DATA/Backend session not yet reported. Items (2) governance commit and A1
  integration are explicitly PM-gated on independent QA PASS / PM Visual Gate
  and are NOT started.
- Intended scope: `agent-system/active.md`, `agent-system/handoffs/active/
  MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001.md` (addendum only, append),
  `frontend/src/shared/components/Avatar/**` and its tests, new task records
  for `MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001` and
  `MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001`. A1 code changes happen
  only inside the separate isolated worktree
  `/Users/mac/mac_Project/mongle_ui-a1-visual-worktree` (branch
  `w6-2-a1-visual`), not here.
- Forbidden scope: backend/DB/migration files, PHASE2-DORAN-MESSAGING-* task
  records (owned by the parallel DATA/Backend-contract session), rewriting
  any existing handoff/QA evidence content (append-only), Wave 6.1 governance
  commit and A1 integration (both PM-gated, not yet authorized), push.
- High-risk writer ownership: `agent-system/active.md` and
  `frontend/src/shared/components/Avatar/**` are single-writer for this task
  for the duration of this session's work.
