# MONGLE_TECHNICAL_NAMESPACE_ALIGNMENT_REPORT

## 1. Task ID
MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001

## 2. Task Name
Naran → Mongle 활성 기술 Namespace 정합화

## 3. 수행자
Developer Agent (Claude Code)

## 4. 최종 Verdict

**PASS**

모든 DoD 항목 충족: 활성 기술 namespace(컴포넌트/파일/CSS 변수/`data-testid`/테스트 디렉터리·설정/env var) 4개 파일군을 `git mv` + 정밀 symbol rename으로 정합화, 전수 검색(189→157 occurrence)으로 재확인 결과 미분류 잔여 0건, 콜드 스타트 2회 연속 30/30 PASS 동일, 시각 delta 0(서브픽셀 안티에일리어싱 노이즈 1건 제외 — 육안 식별 불가), Doran/URL/영속키/인프라 변경 0건, commit/push 없음, HEAD 유지.

## 5. Start Gate

| 항목 | 값 |
|---|---|
| worktree | `/Users/mac/mac_Project/minecraft_points_festivals_doran_ui` (재확인, 후보값과 일치) |
| branch | `dev-newmarkp` (재확인, 일치) |
| HEAD (시작/종료 동일) | `b0aea1d208f94ba928342d423c0f15048ca8b34d` |
| 시작 dirty | 3개 선행 작업(MONGLE-FE-ROUTE-ALIGNMENT-001, MONGLE-FE-E2E-HARNESS-RESTORE-001, MONGLE-E2E-DORAN-SUBSCRIPTION-SEED-ALIGNMENT-001)의 미커밋 변경 + 테스트 산출물 노이즈. `/tmp/mongle-namespace-start-*` (status/diff/untracked/sha256)에 기록 |
| 분류 | 전부 "선행 작업 변경" 또는 "테스트 산출물" — 충돌(C)/출처불명(D) **0건** |
| Node/npm | v26.2.0 / 11.13.0 |
| baseline lint | PASS (exit 0) |
| baseline build | PASS (exit 0, 315 modules) |
| baseline E2E (`playwright.naran.config.ts`, 변경 전) | 콜드 스타트 1회: **30 passed / 0 failed** |

**Start Gate verdict: PASS**

## 6. 기준선 lint/build/E2E

Rename 시작 전, 변경되지 않은 기존 `playwright.naran.config.ts`로 1회 콜드 스타트 실행 — 30/30 PASS 확인 후 착수. (2회까지는 이 시점에 반복하지 않음 — 선행 작업들에서 이미 이 정확한 하네스의 결정성이 반복 검증됐고, 이번 작업 고유의 검증은 rename 이후의 콜드 스타트 2회에 집중했기 때문.)

## 7. Inventory 검색 명령

```
grep -rniIE "naran|나란" . \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=test-results --exclude-dir=.pytest_cache
find . -iname "*naran*" -not -path "./.git/*" -not -path "*/node_modules/*" -not -path "*/test-results/*"
```

## 8. 전체 Naran occurrence 수

- Pass 1 (구현 전): 콘텐츠 189줄 (27개 파일) + 파일/디렉터리명 16건
- Pass 3 (구현 후, 잔여): 콘텐츠 157줄 (20개 파일) — 전부 분류됨, 미분류 0건

## 9. 분류별 occurrence 수

| 분류 | 대략 건수 | 처리 |
|---|---|---|
| `ACTIVE_INTERNAL_RENAME` | 32건 (컴포넌트명 2, CSS 변수 13, `data-testid` 2, env var 4, 파일명 7, import/경로 참조 4) | 전부 rename 완료 |
| `ROUTE_CONTRACT_KEEP` | 약 15건 (`/naran/doran`, `/naran/family` 문자열) | 미변경 |
| `EXTERNAL_OR_PERSISTED_CONTRACT` | 1건 (`localStorage` 키) | 미변경, PM Gate 대상으로 기록 |
| `HISTORICAL_RECORD_KEEP` | 약 20건 (archived handoff 2개 파일 전체, graduated 로그 1행, capture manifest 1개 파일 전체, gap-analysis 인용 1건, design-source 문서 8건, Journey ID/prose 1행) | 미변경 |
| `CURRENT_DOC_UPDATE` | 4건 (Doran messaging/perf 계약 문서명 각 1건, RBAC 계약 문서명 1건, COVERAGE_MAP 경로 셀 2개) | 변경 완료 (플랫폼명/경로만, 그 외 내용 불변) |
| `APPROVED_DOCUMENTED_EXCEPTION` | 6개 파일(이전 세션 자체 조사 보고서) | 인용 원문 유지 + supplement note 추가 |
| `NOT_A_NARAN_OCCURRENCE` (false positive, "나란히") | 3건 | 미변경 (애초에 무관) |

전체 100% 분류, `UNKNOWN_REQUIRES_GATE` **0건**. 상세 파일별 분류는 `MONGLE_NARAN_REMAINING_ALLOWLIST.md` 참고.

## 10. Rename Plan (구현 전 확정, BLOCKER 0건 확인 후 착수)

| 기존 | 신규 | 근거 |
|---|---|---|
| `frontend/src/platform/shell/NaranAppShell.tsx` | `MongleAppShell.tsx` | 컴포넌트 파일, 외부 참조 없음(App.tsx 1곳에서만 import) |
| `frontend/src/platform/shell/NaranAppShell.module.css` | `MongleAppShell.module.css` | 위와 동일 CSS 모듈 짝 |
| `NaranAppShell` (컴포넌트/interface `NaranAppShellProps`) | `MongleAppShell`/`MongleAppShellProps` | 내부 식별자, 사용자 비노출 |
| `--naran-ink/-surface/-wash/-primary/-border` (5개 CSS 변수, `.shell` 스코프 전용) | `--mongle-*` | 이 파일에만 스코프된 private 변수, 외부 참조 0건 확인 후 변경 |
| `data-testid="naran-shell"` | `"mongle-shell"` | 컴포넌트 + E2E locator 동시 변경 |
| `tests/e2e/specs-naran/` | `specs-mongle/` | 활성 테스트 디렉터리 |
| `tests/e2e/playwright.naran.config.ts` | `playwright.mongle.config.ts` | 활성 설정 파일 |
| `tests/e2e/scripts/start-naran-phase1.sh` 등 3개 스크립트 | `start-mongle-phase1.sh` 등 | 이번 세션 직전 작업에서 만든 활성 스크립트(미커밋) |
| `NARAN_PLAYWRIGHT_BASE_URL`/`NARAN_SKIP_TEARDOWN` env var | `MONGLE_PLAYWRIGHT_BASE_URL`/`MONGLE_SKIP_TEARDOWN` | 로컬 셸 env var, 영속/외부 계약 아님 |
| `test.describe('Naran platform shell', ...)` 및 테스트 제목/주석 | `'Mongle platform shell'` 등 | 테스트 리포트에만 노출, 사용자 비노출 |

**예상 영향 파일 수**: 4개 파일 rename(tsx/css/config/spec) + 3개 파일 plain rename(스크립트, 미추적) + 6개 파일 내용 수정(App.tsx, ChatHeader.module.css, DoranLanding.module.css 등 cross-reference) + 4개 현재 SSOT 문서 1줄씩 + 6개 자체 보고서 supplement note.

**Rollback 방법**(실행하지 않음, 이론상 경로만 기록): `git mv <new> <old>` 4회 역순 + `git diff`로 나온 content 변경분 되돌리기. Plain-mv된 3개 스크립트는 다시 `mv`.

**변경하지 않을 동일 문자열 occurrence**: `/naran/doran`, `/naran/family` 전체, `naran.activeFamily.*` localStorage 키, 모든 historical Task ID/파일명, `나란히` false positive 3건.

**BLOCKER 체크 결과**: API path/DB schema/PWA manifest id·scope·start_url/Docker volume·network/CI 설정에서 naran 발견 **0건** — 진행 확정.

## 11. 실제 rename manifest

```
git mv frontend/src/platform/shell/NaranAppShell.tsx frontend/src/platform/shell/MongleAppShell.tsx
git mv frontend/src/platform/shell/NaranAppShell.module.css frontend/src/platform/shell/MongleAppShell.module.css
git mv tests/e2e/playwright.naran.config.ts tests/e2e/playwright.mongle.config.ts
git mv tests/e2e/specs-naran/01-shell.spec.ts tests/e2e/specs-mongle/01-shell.spec.ts   (디렉터리 자동 이관)
mv tests/e2e/scripts/start-naran-phase1.sh tests/e2e/scripts/start-mongle-phase1.sh       (미추적 파일, plain mv)
mv tests/e2e/scripts/stop-naran-phase1.sh tests/e2e/scripts/stop-mongle-phase1.sh
mv tests/e2e/scripts/naran-phase1-teardown.ts tests/e2e/scripts/mongle-phase1-teardown.ts
```

`git status --short`에서 4개 파일이 `RM`(rename+modify)으로 정확히 인식됨 — `git diff --find-renames` 확인 완료.

## 12. 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `frontend/src/App.tsx` | `NaranAppShell`→`MongleAppShell` import + 4곳 JSX 사용 |
| `frontend/src/platform/shell/MongleAppShell.tsx` | import 경로, interface명, 함수명, `data-testid` (4곳) |
| `frontend/src/platform/shell/MongleAppShell.module.css` | 5개 CSS 커스텀 프로퍼티명 (13곳 참조 포함), **값은 전부 불변** |
| `frontend/src/platform/doran/components/ChatHeader/ChatHeader.module.css` | 주석 1줄, 파일명 cross-reference 갱신 |
| `frontend/src/platform/pages/DoranLanding.module.css` | 주석 1줄, 동일 |
| `tests/e2e/specs-mongle/01-shell.spec.ts` | `test.describe` 라벨, 1개 테스트 제목, `data-testid` locator, 주석 1줄 |
| `tests/e2e/playwright.mongle.config.ts` | `testDir`, env var명 2개, 스크립트 경로 참조 2곳, 주석 1줄 |
| `tests/e2e/scripts/start-mongle-phase1.sh` | 주석 1줄(spec 경로 참조) |
| `tests/e2e/scripts/stop-mongle-phase1.sh` | 주석 1줄 |
| `tests/e2e/scripts/mongle-phase1-teardown.ts` | 주석 1줄 + 스크립트 참조 |
| `engineering/phase2/DORAN_MESSAGING_CONTRACT.md` | "Naran is the Platform"→"Mongle is the Platform" (1단어) |
| `engineering/phase2/DORAN_PERFORMANCE_AND_SYNC.md` | "Naran Shell DOM audit"→"Mongle Shell DOM audit" (1단어) |
| `engineering/phase1/ACCOUNT_FAMILY_RBAC_CONTRACT.md` | "Naran platform"→"Mongle platform" (1단어) |
| `agent-system/qa/COVERAGE_MAP.md` | 1개 행의 파일 경로 셀 2개만 갱신 + 설명 note, Journey ID/prose 불변 |
| `engineering/phase2/MONGLE_NAMING_INVENTORY.md` | §3에 §3.1 RESOLVED 섹션 추가(원문 보존) + 상단 supplement note |
| `MONGLE_ROUTE_AUDIT.md`/`MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`/`MONGLE_FE_ROUTE_ALIGNMENT_REPORT.md`/`MONGLE_E2E_DORAN_SUBSCRIPTION_SEED_ALIGNMENT_REPORT.md`/`MONGLE_FE_E2E_HARNESS_RESTORE_REPORT.md` | 각각 상단에 namespace-rename supplement note 1개 문단 추가, 본문 인용은 원문 그대로 |
| `backend/scripts/phase1_seed_synthetic.py` | **미수정 이번 작업에서** — 이전 작업의 diff 그대로(`doran` 서비스 구독 시드) |
| `frontend/package.json`/`package-lock.json` | **미수정 이번 작업에서** — 이전 작업의 `@types/node` diff 그대로 |

## 13. 이동 파일

`git mv` 4건(§11), plain `mv` 3건(§11) — 전부 §12에 목록화.

## 14. 생성 파일

- `engineering/phase2/MONGLE_TECHNICAL_NAMESPACE_ALIGNMENT_REPORT.md` (이 파일)
- `engineering/phase2/MONGLE_NARAN_REMAINING_ALLOWLIST.md`

## 15. 미변경 영역

- `frontend/nginx.conf`, `frontend/vite.config.ts`, `docker-compose.yml`, `docker-compose.prod.yml` — 전수 검색, `naran` 0건 확인.
- `frontend/public/manifest.json`의 `id`/`start_url`/`scope`/`name`/`short_name` — `naran` 관련 값 없음(확인됨, "나란히"는 무관한 부사).
- 모든 `backend/app/**.py` 애플리케이션 코드 — `naran` 0건.
- DB 스키마/마이그레이션 — `naran` 0건.
- `doran.*`/`doran_*`/`service_code="doran"`/`SERVICE_CODE = "doran"` — 문자 그대로 완전 보존.
- `/naran/doran`, `/naran/family` route path 문자열 — 모든 위치에서 완전 보존.
- `naran.activeFamily.${accountId}` localStorage 키 — 완전 보존(§18에서 상술).
- Git worktree/repo 디렉터리명, branch명 — 미변경.
- 모든 historical Task ID/archived 파일명 — 미변경.

## 16. Doran 정본 보존 결과

`grep -rn "'doran'\|\"doran\"" backend/app/domains/`로 재확인: `SERVICE_CODE = "doran"` (`backend/app/domains/doran/service.py:16`) 등 모든 Doran 관련 문자열/파일/디렉터리/권한 네임스페이스 **완전 미변경**. `DORAN_MESSAGING_CONTRACT.md`의 `doran.*`/`doran_*`/`room_admin` 텍스트도 플랫폼명 1단어를 제외하고 전부 원문 그대로.

## 17. route 보존 결과

`git diff`로 `/naran/doran`, `/naran/family` 문자열이 등장하는 모든 파일(App.tsx, MongleAppShell.tsx, specs-mongle/01-shell.spec.ts, backend 시드 스크립트 주석)을 확인 — 전부 **byte-identical**로 보존됨(rename 대상에서 완전히 제외).

## 18. persisted/infra 보존 결과

유일하게 발견된 영속 계약(`naran.activeFamily.${accountId}` localStorage 키, `frontend/src/shared/stores/useFamilyContextStore.ts:20`)은 **명시적으로 변경하지 않음**. 근거: 이 키를 rename하면 기존 사용자의 브라우저에 저장된 "마지막 선택 가족" 상태가 다음 방문 시 조용히 초기화되는 실제 런타임 동작 변화가 발생하며, 이는 이번 작업의 "사용자 화면과 런타임 동작 변화 0" 원칙 및 §3.C의 명시적 금지 항목과 정확히 일치. Docker volume/network/CI 설정에서도 `naran` 0건 확인.

## 19. historical 보존 결과

- `agent-system/handoffs/archive/2026-07/PHASE1-NARAN-PLATFORM-SHELL-001.md`, `agent-system/qa/PHASE1-NARAN-PLATFORM-SHELL-001.md` — 전체 미수정(Task ID/파일명/본문).
- `agent-system/graduated/2026-07.md:17` — 미수정.
- `agent-system/qa/COVERAGE_MAP.md`의 Journey ID(`E2E-NARAN-SHELL-001`)와 설명 텍스트 — 미수정(파일 경로 셀 2개만 예외적으로 갱신, §9 참고).
- `tests/e2e/naran-shell-capture-manifest.md` — 전체 미수정.
- `engineering/phase2/DORAN_FOUNDATION_GAP_ANALYSIS.md:29`의 자체 테스트 결과 인용 — 미수정.
- `engineering/phase2/FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md` — 전체 미수정(경계 사례로 판단, §16 참고 — PM 확인 시 선택적으로만 조정 권장).
- 이전 세션 자체 조사 보고서 6개 — 인용 원문 미수정, supplement note만 추가.

## 20. current 문서 현행화 결과

| 문서 | 상태 | 변경 |
|---|---|---|
| `engineering/phase2/DORAN_MESSAGING_CONTRACT.md` | `APPROVED CONTRACT / canonical R2` | 완료 (1단어) |
| `engineering/phase2/DORAN_PERFORMANCE_AND_SYNC.md` | `APPROVED CONTRACT / canonical R2` | 완료 (1단어) |
| `engineering/phase1/ACCOUNT_FAMILY_RBAC_CONTRACT.md` | `APPROVED DECISIONS / v0.1` | 완료 (1단어) |
| `agent-system/active.md`, `agent-system/relay/current.md` | — | 검색 결과 `naran` 0건, 변경 불필요 |
| `CLAUDE.md` | — | 유일한 매치가 "나란히"(무관한 부사) — 변경 불필요 |

## 21. lint 결과

`npm run lint` — **PASS, exit 0**, 0 신규 warning/error (rename 전/후 동일).

## 22. build 결과

`npm run build`(`tsc -b && vite build`) — **PASS, exit 0**, 315 modules transformed (rename 전/후 동일), unresolved import 0건, casing mismatch 0건(macOS 케이스에 의존하지 않고 실제 파일시스템 rename 확인).

## 23. E2E 1차 cold-start 결과

사전: `docker ps`/`docker volume ls`로 `mc_phase1` 완전 부재 확인. `npx playwright test --config playwright.mongle.config.ts` 단독 실행(자동 webServer 기동 → 30개 테스트 → globalTeardown 자동 정리).

**결과: 30 passed / 0 failed / 0 skipped** (37.2초).

> 이 실행 직전, 곧바로 이전에 시도한 확인용 수동 실행에서 Docker 이미지 레이어 캐시가 stale하여(`--build`가 실제 소스 변경을 반영하지 않고 이전 이미지를 재사용) `getByTestId('mongle-shell')` 탐색이 일시적으로 실패하는 것을 발견했습니다. 소스 코드 자체는 처음부터 정확했음을 직접 확인(`grep`으로 디스크상 파일 내용 재확인) — 순수 Docker 빌드 캐시 문제였습니다. `docker rmi`로 이미지를 제거하고 캐시 없이 1회 재빌드한 뒤, 이후의 모든 `--build` 호출(1차/2차 cold-start 포함)이 정상적으로 최신 소스를 반영함을 확인했습니다. 이 이슈는 코드 결함이 아니라 로컬 Docker 캐시 상태의 일시적 문제였으며, 최종 검증에 영향이 없습니다.

## 24. E2E 2차 cold-start 결과

1차 종료 후 `mc_phase1` 컨테이너/볼륨 완전 부재 재확인 → 동일 명령 재실행.

**결과: 30 passed / 0 failed / 0 skipped** (37.1초).

## 25. 두 실행 비교

| | 1차 | 2차 |
|---|---|---|
| passed | 30 | 30 |
| failed | 0 | 0 |
| skipped | 0 | 0 |
| 실행 시간 | 37.2s | 37.1s |
| 실패 테스트 | 없음 | 없음 |

**완전히 동일 — 비결정성 없음.**

## 26. console error 결과

시각 증거 캡처(§27) 세션에서 수집: `HTTP 401 /api/configs/level.thresholds`(로그인 전, 예상됨), `HTTP 404 /api/configs/level.thresholds`(로그인 후, 이전 작업들에서 이미 기록된 기존 픽스처 간극 — 화면은 정상 렌더링). **rename으로 인한 신규 콘솔 오류 0건.**

## 27. viewport별 시각 증거 경로

`tests/e2e/artifacts/mongle-route-alignment/{mobile,tablet,desktop}/` — 5개 화면(로그인, 대시보드, Doran, Family, 404) × 3 viewport(390×844/1024×1366/1440×900), rename 이후 재캡처본으로 갱신.

## 28. Visual Delta 판정

**PASS — 실질적 Visual Delta 0.**

- `01-login-select.png`, `05-not-found.png` (전 viewport): **byte-identical (0 diff)**.
- `04-naran-family.png` (전 viewport): 최초 비교 시 가족-선택 상태 차이로 큰 diff가 나타났으나, 이는 이번 세션의 캡처 스크립트가 이전 baseline과 다른 사용자 조작 순서를 거쳤기 때문(테스트-스크립트 차이, 코드 변경과 무관) — baseline과 동일 조건(가족 미선택)으로 재캡처한 결과 **byte-identical (0 diff)**로 확인.
- `03-naran-doran.png`: desktop/tablet **0 diff**; mobile은 6% 픽셀에서 차이가 났으나 `max_channel_delta=2/255`로 육안 식별 불가한 서브픽셀 안티에일리어싱 노이즈임을 크롭 비교로 직접 확인.
- `02-dashboard-shell.png`: 0.01~0.07% 픽셀, `max_channel_delta=107` — 미션 타임스탬프 텍스트("오후 11:17" 등)가 캡처 시점에 따라 달라진 것으로, 레이아웃/색상/구조 변화 없음.

## 29. 잔여 Naran allowlist

`engineering/phase2/MONGLE_NARAN_REMAINING_ALLOWLIST.md` 참고. 157개 잔여 occurrence 전부 4가지 허용 분류(`ROUTE_CONTRACT_KEEP`/`EXTERNAL_OR_PERSISTED_CONTRACT`/`HISTORICAL_RECORD_KEEP`/`APPROVED_DOCUMENTED_EXCEPTION`) + false-positive 3건으로 완결. 미분류 0건.

## 30. 알려진 기존 비차단 gap

- `/api/configs/level.thresholds` 404 (격리 DB 시드 완전성 간극, 이전 작업들에서 이미 기록, 이번 작업과 무관, 그대로 유지됨).
- Root `tests/e2e/specs/*.spec.ts` 4개 파일은 `docker-compose.phase0.yml` 부재로 여전히 실행 불가 — 이번 작업 범위 밖, 상태 악화 없음(파일 미변경 확인).
- `와글와글` vs `몽글` 명명 질문 — 이번 작업 이전에 이미 RESOLVED 처리됨(§8.F 반영), 재론의 없음.

## 31. 3회 재귀 검토 결과

**Review 1 — Scope and Naming**: 활성 플랫폼 기술명(`NaranAppShell`/`specs-naran`/`playwright.naran.config.ts`/env var/CSS 변수/`data-testid`)만 변경했음을 `git diff --stat` 라인 수로 재확인 — Doran 관련 파일(`backend/app/domains/doran/**`) 변경 0건, `와글와글` 텍스트 변경 0건, `/naran/...` route 문자열 변경 0건(grep으로 재확인), historical 파일 8개(archived handoffs, capture manifest, graduated log, gap-analysis quote, design-source doc) 전부 diff 없음 확인. **PASS.**

**Review 2 — Code and Runtime**: import/export 정상(`npm run build` 315 modules, 0 error), lint 0 error, cold-start 2회 전건 30/30 PASS, 신규 console error 0(§26), UI visual delta 0(§28), 기존 404 gap 동일(재확인), 제품 기능 동작 변경 0(routes/permissions/Doran service-status 로직 무변경, `git diff` 라인 단위 재확인). **PASS.**

**Review 3 — Residual and Traceability**: `Naran/naran/NARAN/나란` 전수 재검색 결과 157건, 전부 allowlist 등록(§9, §29), 활성 내부 잔여 0, 미분류 잔여 0. 문서 신선도: 6개 조사 보고서에 supplement note 추가, 3개 현재 SSOT 문서 갱신, historical 문서는 원문 보존. 보고서(이 파일)와 `git diff`가 정확히 일치함을 `git status --short`/`git diff --stat` 재확인으로 검증. Start/End manifest(`/tmp/mongle-namespace-start-*`) 정합 확인. **PASS.**

## 32. 6종 최종 검증 Gate

| Gate | 판정 | 근거 |
|---|---|---|
| 1. 환각 방지 | **PASS** | `NaranAppShell.tsx` 실제 경로/내용을 직접 `Read`로 확인 후 rename; `SERVICE_CODE = "doran"` 등 모든 근거는 실제 코드 인용; 화면 ID를 route로 추정한 사례 없음(§17 재확인); 실행되지 않은 테스트를 PASS로 표기한 사례 없음(모든 테스트 실행 로그 직접 확인) |
| 2. 누락 방지 | **PASS** | source/test/config/package-script/docs/route/persistence/infra/historical/artifact 9개 축 전부 §7 grep으로 전수 확인, 결과는 §9 표로 정리; modal/state 화면을 억지 route로 만든 사례 없음(이번 작업은 라우팅 자체를 다루지 않음) |
| 3. 오작업 방지 | **PASS** | global replace(`sed -i` 전체 치환 등) 사용 안 함 — 파일별 정밀 `Edit`/Python 스크립트로 특정 패턴만 치환; Doran 변경 0건; 기존 dirty(3개 선행 작업 변경) 훼손 0건(`git diff --stat`으로 그 파일들이 그대로임을 재확인); 테스트 완화 0건(assertion 삭제/skip/timeout 증가 없음, 테스트 이름만 변경) |
| 4. 중심축 유지 | **PASS** | 기술 namespace 정합화(파일명/심볼명/CSS변수명/testid/env var/문서 플랫폼명 1단어)만 수행; 기능/디자인/API/DB로 범위 확장 없음(CSS 값 불변, JSX 구조 불변, 라우트 불변 — §9, §17, §28로 실증) |
| 5. 신선도 | **PASS** | current(Status: APPROVED CONTRACT/DECISIONS) vs historical(Task ID·commit-anchored) 문서를 매번 `Status` 헤더 직접 확인으로 구분; superseded 문서를 정본으로 사용한 사례 없음; 현재 명칭 결정을 현재 SSOT 3개 문서에 정확히 반영 |
| 6. 근거 정합 | **PASS** | 모든 변경이 code(`git diff`)/test(30/30 로그)/build(exit 0)/screenshot(§28)/PM decision(§0 명칭 계층)/canonical document(Status 헤더) 중 하나 이상으로 추적 가능 |

6개 전부 PASS — Task Verdict `PASS` 성립.

## 33. 잔여 Risk

1. `FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md`의 "확정 명칭은 플랫폼 나란" 등 8개 문장 — 경계 사례로 판단해 historical로 분류·미수정. PM이 이 문서를 여전히 살아있는 정본으로 여긴다면 별도 확인/현행화가 필요할 수 있음(낮은 리스크 — 문서 자체가 "이후 PM 명시 결정이 이 표를 override한다"고 스스로 명시).
2. `naran.activeFamily.*` localStorage 키 — 영구 보존 대상으로 이번엔 유지했으나, 향후 실제로 `mongle.*`로 이관하고 싶다면 기존 사용자의 선택 상태를 잃지 않는 마이그레이션(구키 읽기 → 신키 쓰기 폴백) 설계가 별도로 필요.
3. Docker 빌드 캐시가 최초 1회 stale했던 현상(§23) — 근본 원인은 규명하지 못했고(1회성 재현), 재발 시 `docker rmi`로 이미지 강제 재생성하는 우회법만 확인됨. 향후 유사 세션에서 재발 가능성 있음(낮은 리스크, 이미 우회법 문서화됨).

## 34. 후속 Task (제안만, 실행 안 함)

`MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001` — 범위: `/naran/...` 신규 URL 정책, 구 URL redirect, deep-link, browser Back, PWA `start_url`/`scope`/`id`, Service Worker origin/cache, nginx fallback, 설치 앱 마이그레이션 정책, 전체 route E2E. 별도로, `naran.activeFamily.*` localStorage 키의 안전한 이관(영향분석 후)도 이 후속 Task 또는 그 다음 Task에서 다룰 것을 권장.

## 35. 종료 Git 상태

```
pwd: /Users/mac/mac_Project/minecraft_points_festivals_doran_ui
branch: dev-newmarkp
HEAD: b0aea1d208f94ba928342d423c0f15048ca8b34d  (시작과 동일)

git status --short:
 M agent-system/qa/COVERAGE_MAP.md
 M backend/scripts/phase1_seed_synthetic.py            (선행 작업 변경, 이번 작업 미수정)
 M engineering/phase1/ACCOUNT_FAMILY_RBAC_CONTRACT.md
 M engineering/phase2/DORAN_MESSAGING_CONTRACT.md
 M engineering/phase2/DORAN_PERFORMANCE_AND_SYNC.md
 M frontend/package-lock.json                          (선행 작업 변경)
 M frontend/package.json                                (선행 작업 변경)
 M frontend/src/App.tsx
 M frontend/src/platform/doran/components/ChatHeader/ChatHeader.module.css
 M frontend/src/platform/pages/DoranLanding.module.css
RM frontend/src/platform/shell/NaranAppShell.module.css -> .../MongleAppShell.module.css
RM frontend/src/platform/shell/NaranAppShell.tsx -> .../MongleAppShell.tsx
RM tests/e2e/playwright.naran.config.ts -> tests/e2e/playwright.mongle.config.ts
RM tests/e2e/specs-naran/01-shell.spec.ts -> tests/e2e/specs-mongle/01-shell.spec.ts
 M tests/e2e/test-results/.last-run.json                (테스트 실행 노이즈)
?? .env.phase0.example, docker-compose.phase1.yml        (선행 작업 산출물)
?? engineering/phase2/MONGLE_*.md (9개, 이번 파일 2개 포함)
?? tests/e2e/artifacts/, tests/e2e/scripts/
```

package/lockfile 변경: 이번 작업에서 신규 없음(기존 diff 그대로). backend 변경: 이번 작업에서 없음(기존 diff 그대로). route 문자열 변경: 0건. Doran 영역 변경: 0건. 의도치 않은 파일 변화: 없음(`git diff --stat` 라인 수가 예상 rename 범위와 정확히 일치).

## 36. commit/push/PR 미수행 확인

**확인됨.** 이번 작업 전체에서 `git commit`, `git push`, `git add`(스테이징 없음 — `git mv`가 자동으로 인덱스에 반영한 것 외 별도 `add` 없음), `gh pr create` 등 어떤 명령도 실행하지 않았습니다. `git reset`/`git clean`/`git stash`도 사용하지 않았습니다. HEAD는 시작과 종료 시점에 완전히 동일합니다(`b0aea1d208f94ba928342d423c0f15048ca8b34d`).
