# MONGLE_W6_1_E2E_HARNESS_PROVENANCE

Task: MONGLE-W6-1-E2E-HARNESS-RECOVERY-001
Type: Read-only provenance record (no restoration performed — nothing was missing)

## Subject file

`tests/e2e/scripts/start-mongle-phase1.sh`

## Finding

The file is **not missing**. It exists in the current working tree, is tracked,
executable (`755`), and byte-identical to the blob committed in history.

The earlier "missing script" conclusion (recorded in
`MONGLE_W6_1_EXECUTION_BLOCKERS.md` and repeated in this session's prior turn)
was caused by checking the wrong path: `scripts/start-mongle-phase1.sh`
(relative to repo root) instead of the actual path,
`tests/e2e/scripts/start-mongle-phase1.sh`. Playwright resolves
`webServer.command` relative to the directory containing the config file
(`tests/e2e/`), so the config's `./scripts/start-mongle-phase1.sh` correctly
resolves to `tests/e2e/scripts/start-mongle-phase1.sh` — which is present.

## Origin commit

```
commit 7f1ce9eedaea2b0397cbb5131e33fee2291e789d
Author: iamsonmac@gmail.com
Date:   Thu Jul 30 00:22:44 2026 +0900
Subject: feat(mongle): rebrand Naran->Mongle namespace, restore E2E harness,
         migrate canonical routes+storage
```

Introduced as a `new file mode 100755`, size 23 lines. This commit's own
message states the script was "restored from git history (commit 92bd75c^)"
during an earlier, prior-approved harness-restore task
(`MONGLE-FE-E2E-HARNESS-RESTORE-001`, referenced in the script's own header
comment and in the Playwright config's leading comment).

## Ancestry

- `7f1ce9e` is an ancestor of current HEAD (`496364999c0dbca13153e611c4fb09614ee9af2e`).
- No other commit, branch, or tag touches this path
  (`git log --all --full-history` returns exactly one commit).
- No unreachable/dangling copies exist (`git fsck --no-reflogs --unreachable`
  returned nothing).
- Single worktree only (`git worktree list` shows one entry, this checkout).

## Integrity check

```
git cat-file -p efe4583...   -> sha256 14142e5e64a2334fa7376ba98d2935d097d478fe6cdbe536f0ee09bf09225aff
tests/e2e/scripts/start-mongle-phase1.sh -> sha256 14142e5e64a2334fa7376ba98d2935d097d478fe6cdbe536f0ee09bf09225aff
```

Identical. Working tree matches the committed blob exactly — no drift, no
local edit, no restoration action taken or needed.

## Consumer/infrastructure cross-check

- `tests/e2e/playwright.mongle.config.ts` — header comment explicitly names
  this file and `docker-compose.phase1.yml` as the harness it restores.
  `webServer.command: './scripts/start-mongle-phase1.sh'` resolves correctly.
- `docker-compose.phase1.yml` — present at repo root, defines exactly the
  three services the script drives: `db`, `backend`, `frontend`.
- `.env.phase0.example` — present at repo root, referenced by the script via
  `--env-file`.
- `backend/scripts/phase1_seed_synthetic.py` — present, is the seed script
  the script execs inside the `backend` container.

All referenced files exist. No contract mismatch found.

## Classification

**A. EXACT_COMMITTED_SOURCE_FOUND** — with the caveat that no restoration was
required because the file was already correctly present; the prior turn's
"missing file" claim is retracted here as a path-lookup error, not a repo
state fact.
