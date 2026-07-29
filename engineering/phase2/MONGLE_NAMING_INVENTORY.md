# MONGLE_NAMING_INVENTORY

TASK ID: MONGLE-FE-ROUTE-ALIGNMENT-001 — Wave 3
**No product code was modified in Wave 3.** Every occurrence below was located by direct grep across `frontend/src`, `frontend/index.html`, `frontend/public/manifest.json` — none assumed.

> **Namespace rename note (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, added after this document was written):** the active internal identifier `NaranAppShell` (component, file, CSS module, `data-testid`) was subsequently renamed to `MongleAppShell`, and the test directory `specs-naran`/config `playwright.naran.config.ts` were renamed to `specs-mongle`/`playwright.mongle.config.ts`. File:line citations below reflect the repository state at the time this document was written and are **not** retroactively updated — see `MONGLE_TECHNICAL_NAMESPACE_ALIGNMENT_REPORT.md` for the rename's own evidence trail.

## 0. PM naming/URL decision, recorded for reference (mid-task addendum)

The PM fixed the following naming/URL scheme during this task, to be recorded but **not** acted on beyond documentation this wave:

```
공식 한국어명: 몽글
공식 영문 제품명: Mongle Home
짧은 브랜드명: Mongle
잠정 대표 URL: https://www.mongle.life
향후 내부 기술 식별자(별도 마이그레이션 대상): mongle
현재 내부 식별자(유지): doran
```

Explicit non-actions this wave, per the PM's own follow-up message:
- No domain string (`mongle.life` or otherwise) is hardcoded anywhere in this repository — confirmed by grep (`mongle.life`, `PUBLIC_APP_URL`, `VITE_APP_URL`: 0 hits before and after this task).
- No `doran`→`mongle` internal-identifier migration is performed — that is explicitly scoped as a separate future task pending impact analysis.
- The `mongle.life` → `www.mongle.life` redirect is operations/infra work, out of this FE task's scope.
- If/when a real domain needs wiring into the app, the PM's own recommended pattern (`PUBLIC_APP_URL` for server/deploy layer, `VITE_PUBLIC_APP_URL` for browser-read Vite code) should be used rather than a literal string — noted here for the next task that needs it, not implemented now since nothing currently needs it.
- No claim is made here that the domain is purchased, DNS-configured, or live — this section only records the naming decision for documentation traceability.

## 1. Headline finding

**Zero literal user-visible `도란` or `Doran` text exists in the current frontend.** The only match for the Korean string `도란` in the entire `frontend/src` tree is inside a CSS developer comment (`DoranLanding.module.css:157`, not rendered to any user). Every match for the English string `Doran` is a component name, file name, TypeScript type/prop name, or code comment — all internal identifiers, explicitly protected under the PM's "변경 금지" list (§B below).

This means the PM's stated premise ("현재 사용자 노출 서비스명은 '도란'이다") does not match the current `dev-newmarkp` code state — a prior, uncommitted-to-`origin` local pass (the `b0aea1d` "Wave 6.0B chat surface + shell rebrand checkpoint" commit) already replaced the app-level user-visible name with **몽글**, before this task began. This is reported precisely rather than silently assumed away, per this session's own no-hallucination discipline.

## 2. Full occurrence table

| File | Occurrence | Context | User-visible | Change | Reason |
|---|---|---|---|---|---|
| `DoranLanding.module.css:157` | `도란` | CSS comment: "1024px+: 도란을 몽글 Shell의 실제 workspace로 통합한다" | No (developer comment) | **No change** | Internal dev commentary, not rendered |
| `App.tsx:9,63` | `DoranLanding` | import + JSX element name | No | **No change** | Component name — internal identifier |
| `NaranAppShell.tsx:77,81,102` | `Doran`, `isDoranConversationMobile`, `doranConversationMode` | code comment + variable/CSS-class name | No | **No change** | Internal identifier/comment |
| `NaranAppShell.module.css:88,90` | `Doran`, `isDoranConversationMode` | CSS comment | No | **No change** | Developer comment |
| `platform/doran/**` (10 files: `preview/*.ts`, `ChatComposer.module.css`, `ChatHeader.module.css`, `DoranLanding.module.css`, `DoranLanding.tsx`) | `Doran*` type/const/file names (`DoranPreviewRoom`, `doranPreviewRooms`, etc.) | type defs, imports, comments | No | **No change** | Internal module/type identifiers — directory `platform/doran/` itself is an internal path, per PM directive #10 |
| `AccessBoundary.tsx:11` | `몽글을 준비하고 있어요` | loading-state heading | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `NaranAppShell.tsx:13,14,16,18` | `몽글 가족 기능`, `몽글 기능`, `몽글 가족 정보`, `몽글에 연결할 수 없어요` | family-context status copy | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `NaranAppShell.tsx:106` | `aria-label="몽글 홈"`, link text `몽글` | header brand link | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `NaranAppShell.tsx:115` | `aria-label="몽글 서비스 탐색"` | desktop nav landmark | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `NaranAppShell.tsx:131` | `aria-label="몽글 모바일 탐색"` | mobile nav landmark | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `FamilyLanding.tsx:9` | `몽글 가족` | eyebrow text | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `DoranLanding.tsx:231` | `몽글 · 가족 대화` | eyebrow text | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `index.html:21,29` | `og:title`/`<title>` = `몽글` (+ `몽글 — 가족 플랫폼`) | document metadata | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `manifest.json:2,3` | `name`/`short_name` = `몽글`/`몽글 — 가족 플랫폼` | PWA metadata | **Yes** | Already `몽글` — no change needed | Confirmed correct |
| `NaranAppShell.tsx:88,147` | `와글와글` | Dock/nav label for the chat feature specifically | **Yes** | **Flagged, not changed — see §3** | Distinct from the `도란`→`몽글` scope the PM defined |
| `NaranAppShell.tsx:136,155` / `NaranAppShell.module.css:45` | `와글와글` | code comment + `sr-only` unavailable-service notice | **Yes (sr-only text)** / No (comment) | **Flagged, not changed — see §3** | Same reasoning |
| `DoranLanding.tsx:192,193,219,232,259` | `와글와글` (empty/error titles, `h1`, `Avatar alt`) | chat feature page copy | **Yes** | **Flagged, not changed — see §3** | Same reasoning |
| `index.html:27` / `manifest.json:4` | `와글와글` | meta description / PWA description | **Yes** | **Flagged, not changed — see §3** | Same reasoning |

## 3. The one open naming question found (not resolved by silent guess)

**"와글와글" is used consistently (9 user-visible occurrences across 4 files) as the specific display name for the chat/messaging feature**, coexisting with "몽글" as the overall app/shell brand name. The PM's task text names only `도란`→`몽글` as in scope; it never mentions `와글와글`. Two readings are both plausible from the evidence alone:

- **(a)** `와글와글` is a deliberate, already-decided sub-brand name for the chat feature specifically (like "채팅"/"오픈채팅" naming inside a larger app) — in which case it should be left exactly as-is, and this task's `도란`→`몽글` scope is already fully satisfied (0 changes needed).
- **(b)** `와글와글` was an interim placeholder from the same uncommitted rebrand pass that never got PM sign-off, and the PM's intent is a single unified name (`몽글` everywhere, including the chat feature's own heading/dock label) — in which case 9 occurrences across 4 files would need updating, plus the one E2E assertion that currently requires `heading name: '와글와글'` (`tests/e2e/specs-naran/01-shell.spec.ts`).

**This task does not guess between (a) and (b).** Per the PM's own explicit scope (only `도란`→`몽글` was named) and the principle of minimal, evidence-traceable change, **this wave leaves `와글와글` untouched** and reports this as the single most important open item from Wave 3, carried into the final report's non-blocking risk list.

### 3.1 RESOLVED (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, PM naming hierarchy)

Reading **(a) is confirmed correct** by the PM's explicit naming hierarchy in that later task's §1:

```
공식 한국어명: 몽글        — platform/product brand
공식 영문 제품명: Mongle Home
짧은 브랜드명: Mongle
사용자 노출 메시징 기능명: 와글와글   — the chat feature's own display name, distinct from the platform brand
메시징 내부 기술 도메인: doran        — internal identifier, unrelated to either display name
```

`와글와글` was never a leftover Naran-era placeholder — it is the deliberately separate, PM-confirmed display name for the messaging feature specifically, coexisting with `몽글` as the platform/shell brand. **No code or copy changes result from this resolution** — the 9 occurrences listed in the table above were already correct and remain unchanged. This closes the open question; §3's original text is preserved above for traceability of how the question was framed and resolved.

## 4. Wave 3 Gate

- 사용자 노출 `도란` 0건: **confirmed true, already 0 before this wave — no change required.**
- 사용자 노출 `Doran` 0건: **confirmed true.**
- 사용자 노출 `몽글` 적용: **confirmed true, already applied in 8 locations before this wave.**
- 내부 식별자 rename: **0 performed** (none needed, none attempted).
- 기능 동작 변경: **0** (no code was touched).
- 관련 lint/typecheck/test: run and reported in the final report (§9) — since no source was changed, this establishes the pre-existing baseline, not a regression check.
- `MONGLE_NAMING_INVENTORY.md`: this file, complete.

**Verdict: PASS** — with one explicitly flagged, non-blocking open question (§3) carried forward rather than silently resolved.
