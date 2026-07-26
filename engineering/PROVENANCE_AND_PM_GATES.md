# Provenance, Adoption, and Approved Decisions

**Status: APPROVED_WITH_DECISIONS / v0.1 — 2026-07-26.**

## Directly reviewed Drive sources

| Source | Document ID | Local treatment |
| --- | --- | --- |
| Outlook Hub — BE development guide | `1A-Zrt39eBYbcbgt3C_Un-sRthoRiXCJwfyibr5u2DwU` | Adopt security/query/thin-router lessons; reject synchronous/Cloud-SQL-specific mechanics. |
| Outlook Hub — FE development guide | `1Vx-HfWThxwVL9bquKZLUVN4dPf6DjoUrxnksDb2iUgo` | Adapt component audit/accessibility ideas; reject its product-specific desktop/token prescriptions. |
| Viblot — Cross-Cutting Norms DRAFT | `1-w7Vtqm7irNzK-80v7A5vMyo2YLNIs27kE8SoksqMl8` | Adapt dependency, local-first, and responsibility principles; retain DRAFT status. |
| Viblot — Backend Guide DRAFT | `10YP2hG4FmhZjrtIYjYFSYGB982wLz4qEjqqIP7SZxVI` | Adapt service/rules distinction; do not adopt unmeasured contracts/transaction design. |
| Viblot — Frontend Guide DRAFT | `1tslRpButW0Zrkb0bbM42-MmjPVMnPeQWYOr9s_pBKaQ` | Adapt server authority, transport boundary, and local-first promotion. |
| Family-platform integrated README draft | `1c23qVHWbUkCaYyDR_mVb5v2pC6cNnCDza-wNOHDVLww` | Localized as `engineering/README.md`. |
| Family-platform Common Norms draft | `1zcXXbyQAYl4wlWM_hN-PDYjn9XQSBfgxjwYtYR_kIxk` | Localized after source audit. |
| Family-platform Backend draft | `1FJwiI6t96GA_wIqt8Y95y4olGpldsDJRtG5GwK1DwjU` | Localized with actual async/commit findings. |
| Family-platform Frontend draft | `1aWAhKpws6WeeRjRSOgOVOUPgalrZ2eg65itzNZ0XzhQ` | Localized with current page/shared layout. |
| Family-platform Testing draft | `1Hn-yD_-xfE27zz7yu85sLqsvmQyAaCeCJn9jVQll4Qk` | Localized with existing Coverage Map and isolated runtime. |
| Family-platform provenance draft | `1qiyPD2PhSLCggpCpQlcBMnplhUCHYRph_A-aWPZMjKc` | Replaced by this source-backed adoption record. |

## Adoption matrix

| Topic | Outlook treatment | Viblot treatment | Family-platform position |
| --- | --- | --- | --- |
| Thin router/service separation | ADAPT | ADOPT principle | TARGET, with current exceptions retained |
| Transaction ownership | PM_GATE conflict | PM_GATE conflict | PM_GATE-01 |
| Pure rules/guards | limited | ADAPT | core state changes only; PM_GATE-05 scope |
| Pydantic v2 | ADOPT direction | stack-independent | TARGET; current settings file is legacy `class Config` |
| API response envelope | REJECT global retrofit | candidate only | PM_GATE-02 |
| Migrations | reject Cloud SQL/process recipes | deferred | PM_GATE-03; current init.sql bootstrap |
| Contracts/generated types | reject DB-name copying rule | ADAPT | PM_GATE-04 |
| Shared UI | reject Outlook visual values/layout | ADAPT local-first | current shared/page architecture retained |
| QA | ADAPT evidence rigor | ADAPT risk boundaries | approved risk-based policy |
| Generated artifacts | ADOPT | ADOPT | change source then regenerate |

## APPROVED DECISION-01 — transaction boundary

**Current evidence:** async `AsyncSession` is used, but `await db.commit()` is found in routers and services. Representative paths include `domains/chat/router.py`, `domains/mission_template/router.py`, `domains/auth/service.py`, `domains/daily_point/service.py`, and `domains/mission/service.py`.

**Approved:** a top-level use-case Unit of Work owns the transaction and performs one commit or rollback. Routers/services/helpers are no-commit. Existing mixed code is LEGACY and is migrated only with its changed domain.

## APPROVED DECISION-02 — API response contract

**Current evidence:** current routers use typed models, lists, and dictionaries; no global envelope is measured. **Approved:** preserve those shapes; new singleton APIs use typed direct bodies, new lists prefer `{items,total,cursor?}`, and standardized errors are introduced incrementally.

## APPROVED DECISION-03 — migration SSOT

**Approved:** `database/init.sql` remains bootstrap and Alembic becomes incremental SSOT after a frozen baseline. First operating use requires schema comparison, backup, and restore rehearsal.

## APPROVED DECISION-04 — contracts/OpenAPI

**Approved:** OpenAPI-generated types are used at Phase 0–1 API boundaries; local feature/view models remain. A contracts package is deferred until independent WebSocket or multi-runtime versioning warrants it.

## APPROVED DECISION-05 — rules/guards scope

**Approved:** pure rules apply to approval, points/levels, authority, subscription, chat membership, and irreversible/audited transitions. BE guards cover auth, RBAC, ownership, tenant boundary, and IDOR; FE rules remain UX-only.

## Rejected direct imports

- Outlook's synchronous SQLAlchemy, Cloud SQL/search-path operational commands, and product-specific BaseResponse/UI/token prescriptions are not local rules.
- Viblot's `contracts` package, automatic registration, fixed module tree, and DRAFT-specific Human Gate/state model are not current repository contracts.
- Neither external source permits deriving a production/PWA/device PASS from a source-only audit.

## Deferred follow-up candidates

- Isolated API+DB regression fixtures for mission, point aggregate, RBAC, and soft-delete invariants.
- Physical iPhone/iPad/Android-tablet evidence and PWA/push contract audit.
- A PM-approved migration and API-contract strategy before structural expansion.
