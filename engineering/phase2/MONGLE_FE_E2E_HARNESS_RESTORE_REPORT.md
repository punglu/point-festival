# MONGLE_FE_E2E_HARNESS_RESTORE_REPORT

## 1. Task ID
MONGLE-FE-E2E-HARNESS-RESTORE-001

> **Namespace rename note (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, added after this document was written):** the scripts this report created (`start-naran-phase1.sh`, `stop-naran-phase1.sh`, `naran-phase1-teardown.ts`) and `playwright.naran.config.ts`/`specs-naran/` were subsequently renamed to their `mongle`-prefixed equivalents. Citations below reflect the state at write time.

## 2. 최종 Verdict

**CONDITIONAL**

DoD의 인프라/결정성/시각 증거 항목은 전부 충족했습니다(재현 가능한 실행, 2회 연속 동일 결과, lint/build PASS, 3개 viewport 스크린샷, console error 0(신규 코드 기준), commit/push 없음). 다만 `PASS`로 닫지 않는 이유는: 복구된 하네스가 **실제로 1건의 진짜 회귀**를 드러냈고(`presents Doran as an honest unavailable service entry point`, 5개 프로젝트 모두 실패, 결정론적으로 재현됨), 이 회귀는 이번 작업 범위(하네스 복구) 밖의 제품/픽스처 문제라 이번 작업에서 고치지 않았기 때문입니다. "PASS"라고 하면 이 실패를 감추는 것이 되므로 정직하게 CONDITIONAL로 보고합니다.

## 3. Start Gate

| 항목 | 값 |
|---|---|
| worktree | `/Users/mac/mac_Project/minecraft_points_festivals_doran_ui` (일치 확인) |
| branch | `dev-newmarkp` (일치 확인) |
| HEAD (시작/종료 동일) | `b0aea1d208f94ba928342d423c0f15048ca8b34d` |
| git status (시작) | `frontend/src/App.tsx`, `package.json`, `package-lock.json`, `tests/e2e/specs-naran/01-shell.spec.ts` 수정(선행 작업 MONGLE-FE-ROUTE-ALIGNMENT-001의 변경), `tests/e2e/test-results/**` 노이즈 |
| 분류 | **B (선행 작업 변경)** — 충돌 없음, 이번 작업과 겹치지 않는 파일들 |
| node/npm | v26.2.0 / 11.13.0 |
| Playwright | `@playwright/test` 1.58.2 (설치됨, `node_modules/.bin/playwright` 확인) |
| 기존 E2E 구조 | `tests/e2e/playwright.config.ts`(root suite, `docker-compose.phase0.yml` 의존 — 부재), `tests/e2e/playwright.naran.config.ts`(Naran suite, 원래 `docker-compose.phase1.yml`/`13001` 포트 의존 — **파일 자체가 git 히스토리에서 삭제된 상태였음**) |
| 폐기된 Docker 의존성 | 확인됨 — `docker-compose.phase1.yml`, `.env.phase0.example`이 커밋 `92bd75c`(이 브랜치의 "mongle/wagle rename + Wave4 static UX" 체크포인트)에서 삭제됨. 이 삭제와 DoranLanding 전면 재작성이 **같은 커밋**에 함께 들어감 — 즉 재작성 이후 이 E2E가 실제로 재검증된 적이 없었을 가능성이 있음(§4에서 상술) |

**Start Gate verdict: PASS** — C/D(충돌·출처불명) 없음, B(선행 작업 변경)만 존재해 계속 진행.

## 4. 기존 E2E 실패 원인 (정확히 재현)

1. `tests/e2e/playwright.naran.config.ts`의 `use.baseURL`이 `http://localhost:13001`을 가리키지만, 이 포트를 서빙하는 `docker-compose.phase1.yml`이 저장소에 존재하지 않았음(삭제됨).
2. 실행 시도 시 정확한 오류: `Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:13001/` — 30개 테스트 케이스(5 project × 6 test) 전부 이 오류로 실패.
3. `.env.phase0.example`도 함께 삭제되어 있어, Compose 파일을 되살려도 자격증명/DB명 환경변수를 넣을 파일이 없었음.
4. 인증 fixture 자체(`backend/scripts/phase1_seed_synthetic.py`, `Synthetic Family Alpha/Beta` 등)는 **삭제되지 않고 그대로 존재** — 즉 "재현 가능한 fixture가 아예 없다"는 BLOCKER는 아니었고, "그 fixture를 담을 격리 실행 환경이 없다"는 순수 인프라 문제였음.

## 5. 선택한 최소 복구 설계

우선순위 1(기존 webServer 설정 복구)을 그대로 채택. 새 인프라를 설계하지 않고, git 히스토리에서 **동일 커밋이 삭제하기 직전의 원본 파일**을 그대로 복원:

- `git show 92bd75c^:docker-compose.phase1.yml` → 그대로 복원 (내용 수정 없음)
- `git show 92bd75c^:.env.phase0.example` → 그대로 복원 (내용 수정 없음)
- `playwright.naran.config.ts`에 `webServer`(복원한 compose 기동 스크립트 실행) + `globalTeardown`(종료 시 정리) 추가 — 이것이 이번 작업에서 유일하게 "새로 작성"한 설정
- 기존 인증/fixture(`loginAsFirstPlayer`, `loginAsLegacyPlayer`, `phase1_seed_synthetic.py`)는 **그대로 재사용** — 임의 계정을 만들지 않음

기동 스크립트(`tests/e2e/scripts/start-naran-phase1.sh`)를 작성하는 과정에서 **레이스 컨디션 버그를 발견하고 자체 수정**했습니다: 최초 버전은 `db+backend+frontend`를 동시에 `--wait`로 올린 뒤 시딩 스크립트를 실행했는데, frontend의 nginx 헬스체크는 DB 데이터와 무관하게 즉시 통과하므로 Playwright가 시딩이 끝나기도 전에 URL 응답만 보고 테스트를 시작해버리는 경우가 있었습니다(실제로 2차 전체 실행에서 다른 테스트가 비결정적으로 실패하는 것으로 관측). **db+backend를 먼저 올려 시딩을 완료한 뒤, frontend를 마지막에 올리는 순서로 수정**하여, Playwright가 폴링하는 frontend URL 자체가 "시딩 완료 후에만 응답 가능"하도록 만들었습니다. 이후 콜드 스타트 2회 반복 실행에서 완전히 동일한 결과(25 passed / 5 failed, 같은 테스트)를 확인했습니다.

## 6. 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `docker-compose.phase1.yml` (신규, 실제로는 복원) | git 히스토리 원본 그대로, 내용 미수정 |
| `.env.phase0.example` (신규, 실제로는 복원) | git 히스토리 원본 그대로, 내용 미수정 |
| `tests/e2e/playwright.naran.config.ts` | `webServer`(시작 스크립트 실행, URL 폴링, `reuseExistingServer: true`)와 `globalTeardown` 추가. 기존 `testDir`/`use`/`projects` 설정은 전혀 변경 안 함 |
| `tests/e2e/scripts/start-naran-phase1.sh` (신규) | 격리 스택 기동 + 시딩, 순서 보장(§5) |
| `tests/e2e/scripts/stop-naran-phase1.sh` (신규) | 컨테이너+볼륨 정리 |
| `tests/e2e/scripts/naran-phase1-teardown.ts` (신규) | Playwright `globalTeardown`에서 stop 스크립트 호출 |

## 7. 변경 이유

- 저장소에 실제로 정의됐던 명령/구조(과거 커밋의 `docker-compose.phase1.yml` + `playwright.naran.config.ts`의 `baseURL:13001`)를 그대로 되살리는 것이 "명령을 추정하지 않는다"는 원칙에 가장 부합.
- `webServer`/`globalTeardown` 추가는 Playwright 표준 메커니즘으로, 반복 실행 가능성·자동 정리라는 DoD 요구사항을 코드 최소 변경으로 충족.
- `@types/node` 추가(선행 작업에서 이미 발생)는 이번 작업과 무관하지만, `npm run build`가 이걸 요구하는 상태였고 이미 선행 커밋 diff에 포함되어 있어 손대지 않음.

## 8. 테스트 명령과 결과

| 명령 | 결과 |
|---|---|
| `cd tests/e2e && npx playwright test --config playwright.naran.config.ts --reporter=list` | 실행됨(자동 webServer 기동 → 테스트 → 자동 teardown) |
| exit code | 1 (5개 실패 존재하므로 — 아래 §9/§10 참고) |
| 테스트 수 | 30 (6 spec × 5 project) |
| pass/fail/skip | **25 pass / 5 fail / 0 skip** |
| 실행 시간 | 약 45~47초(콜드 스타트, Docker 빌드+기동+시딩+테스트 전체 포함) |

## 9. 1차 실행 결과 (콜드 스타트, 완전히 정리된 상태에서)

- `docker ps`로 `mc_phase1` 컨테이너 없음을 사전 확인.
- `npx playwright test --config playwright.naran.config.ts` 단독 실행 → webServer가 자동으로 `start-naran-phase1.sh` 실행(빌드+기동+시딩) → 30개 테스트 실행 → globalTeardown이 자동으로 `stop-naran-phase1.sh` 실행.
- 결과: **25 passed, 5 failed** (전부 `presents Doran as an honest unavailable service entry point`, 5개 project 각각 1회씩).
- 실행 후 `docker ps`/`docker volume ls`로 `mc_phase1` 흔적 0건 확인 — teardown 정상 동작.

## 10. 2차 반복 실행 결과 (동일 환경에서 재실행)

- 1차 종료 후 컨테이너/볼륨이 자동 정리된 것을 재확인한 뒤, 동일 명령을 다시 콜드 스타트로 실행.
- 결과: **25 passed, 5 failed** — 실패한 테스트 이름과 개수가 1차와 **정확히 동일**.
- §5에서 서술한 레이스 컨디션 수정 이후에는 두 번의 콜드 실행이 완전히 결정론적으로 일치함을 확인. (수정 전에는 2차 실행에서 별도의 테스트가 추가로 비결정적 실패하는 것을 발견 → 원인 규명 후 수정 → 재검증 완료.)

## 11. 시각 증거 경로

```
tests/e2e/artifacts/mongle-route-alignment/
  mobile/   (390×844)
  tablet/   (1024×1366)
  desktop/  (1440×900)
```

각 viewport 폴더에 5개 PNG:
- `01-login-select.png` — 로그인/프로필 선택 화면(기존 route `/`)
- `02-dashboard-shell.png` — 로그인 후 Shell + 대시보드(기존 route `/dashboard`)
- `03-naran-doran.png` — 기존 route `/naran/doran` (가족 미선택 상태 렌더)
- `04-naran-family.png` — 기존 route `/naran/family` (가족 미선택 상태 렌더)
- `05-not-found.png` — 신규 404 fallback (`/this-path-does-not-exist`)

인증 토큰/개인정보 노출 없음(합성 시드 계정만 사용, 화면에 이름 외 민감정보 없음). 임의 CSS 조작 없음, Playwright가 실제 페이지를 열고 `networkidle` 이후 캡처.

## 12. viewport별 확인 결과

| Viewport | Shell 정상 | 기존 route 정상 | 404 정상 | 가로 overflow | 주요 컨트롤 잘림 |
|---|---|---|---|---|---|
| 390×844 (Mobile) | 예 | 예 | 예 (제목/설명/링크 모두 표시) | 없음 | 없음 |
| 1024×1366 (Tablet) | 예 | 예 | 예 | 없음 | 없음 |
| 1440×900 (Desktop) | 예 | 예 | 예 | 없음 | 없음 |

이 판정은 **라우팅/정상 출력 확인**이며, 승인 디자인과의 픽셀 단위 일치를 주장하지 않습니다(Wave 6.9 몫).

## 13. Console error 결과

시각 증거 캡처 세션(5개 route × 3 viewport)에서 수집된 콘솔/네트워크 오류:

| 오류 | 발생 시점 | 판정 |
|---|---|---|
| `HTTP 401 /api/configs/level.thresholds` | 로그인 전(`01-login-select`) | 예상된 동작(미인증 상태에서의 401) — 문제 아님 |
| `HTTP 404 /api/configs/level.thresholds` | 로그인 후(`02-dashboard-shell`) | **이번 작업과 무관한 기존 픽스처 간극** — 격리 DB 시드 스크립트(`phase1_seed_synthetic.py`)가 RBAC 픽스처만 만들고 레거시 `app_configs` 테이블의 `level.thresholds` 키를 시딩하지 않음. `CLAUDE.md`에 문서화된 "BE 설정 연동 실패 시 FE 폴백" 패턴대로 화면은 정상 렌더링됨(스크린샷에서 확인) — 앱 크래시나 blank 없음, 논블로킹으로 기록 |
| `path="*"` 404 route 자체에서 발생한 오류 | — | **0건** |

**신규로 추가한 코드(App.tsx 404 route)로 인한 콘솔 오류는 0건.**

## 14. 기존 route 회귀 결과

MONGLE_ROUTE_AUDIT.md를 정본으로 사용해 5개 최상위 route(`/`, `/dashboard`, `/admin/*`, `/naran/doran`, `/naran/family`) 전체 진입을 확인:

- 30개 E2E 테스트 중 **29개는 라우팅/Shell 자체와 무관하게 통과**(로그인, Family 스위치, 권한 차단, 반응형 네비게이션, mapping-required 상태, 신규 404 등).
- **1개(`presents Doran as an honest unavailable service entry point`)만 실패** — 이는 라우팅 자체의 회귀가 아니라, `/naran/doran`이 도달 가능하고 정상 렌더링되지만(스크린샷으로 확인, blank 아님) 그 안에서 기대되는 컴포넌트 상태(활성 서비스의 Room List 헤딩)가 현재 합성 시드 데이터로는 나타나지 않는다는 **콘텐츠/픽스처 수준의 불일치**입니다. 정확한 원인:
  - `NaranAppShell.tsx`의 `serviceStatus('doran')`은 family의 `ServiceSubscription` 목록에서 `service_code === 'doran'`인 행을 찾음.
  - `backend/scripts/phase1_seed_synthetic.py`는 `ServiceSubscription(family_group_id=alpha.id, service_code="markpoint", ...)`만 생성 — **`doran` 서비스 구독 행이 아예 없음**.
  - 따라서 `/naran/doran`은 항상 `pageState === 'disabled'`로 떨어져 "와글와글을 사용할 수 없어요" 안내만 보이고, 테스트가 기대하는 `<h1>와글와글</h1>` Room List 헤딩은 나타나지 않음.
  - 이 테스트 자체와 `DoranLanding.tsx`의 현재 동작(serviceStatus 게이팅)은 커밋 `92bd75c`에서 **같은 커밋에 함께** 도입됐지만(도란→몽글/와글와글 명칭 변경 + DoranLanding 전면 재작성 + E2E 인프라 삭제), 그 시점 이후 실제로 이 E2E가 재검증된 적이 없었던 것으로 보입니다(그 커밋 자체가 인프라를 지웠으므로).
- **이번 작업 범위(하네스 복구)에서는 이 픽스처 간극을 고치지 않았습니다** — `backend/scripts/phase1_seed_synthetic.py` 수정은 금지된 "Backend 수정"에 해당할 수 있고, 이 작업의 목적은 "하네스를 복구해 회귀를 드러내는 것"이지 "발견된 모든 회귀를 고치는 것"이 아니기 때문입니다. 정확한 원인과 위치를 여기 기록해 다음 작업이 바로 고칠 수 있게 했습니다.

## 15. 404 fallback 결과

- `/this-path-does-not-exist` 직접 진입 시 30개 테스트 중 5개(project별 1개씩) 모두 **PASS** — "페이지를 찾을 수 없어요" 헤딩과 "몽글로 돌아가기" 링크 노출 확인.
- 기존 route(`/`, `/dashboard`, `/admin/*`, `/naran/doran`, `/naran/family`)를 가로채지 않음 — React Router가 더 구체적인 경로를 우선 매칭하므로 구조적으로 보장되며, 실제로 다른 25개 테스트가 여전히 정상 통과하는 것으로 실증.
- 콘솔 오류 0건(§13).

## 16. 영향 범위

- 수정/추가된 모든 파일은 `tests/e2e/**` 또는 저장소 루트의 격리 테스트 전용 Compose/env 파일 — **제품 소스(`frontend/src/**`, `backend/app/**`) 추가 수정 없음**(선행 작업에서 이미 변경된 `App.tsx`만 그대로 유지, 이번 작업에서 재수정 안 함).
- API/DB/백엔드 애플리케이션 코드 변경 **0건**. `backend/scripts/phase1_seed_synthetic.py`도 읽기만 했고 수정하지 않음.
- 격리된 `mc_phase1` Docker 스택은 실행 후 매번 완전히 정리됨(컨테이너+볼륨) — 다른 실행 중인 스택(`mc-backend`, `outlook-hub-*`, `mongle-wave5-qa-*`)과 포트/이름 충돌 없음(사전 확인: `docker ps`).

## 17. 미변경 확인

- `frontend/src/**`의 어떤 컴포넌트도 이번 작업에서 수정하지 않음(`App.tsx`는 선행 작업의 상태 그대로).
- `backend/**` 전체 미수정.
- 기존 `tests/e2e/specs-naran/01-shell.spec.ts`의 기존 5개 테스트 assertion **전혀 수정 안 함** — 선행 작업에서 추가된 404 테스트 1개만 그대로 유지.
- `tests/e2e/playwright.config.ts`(root suite) 미수정 — 여전히 `docker-compose.phase0.yml` 의존(부재), 이번 작업 범위 밖이라 손대지 않음.
- `.gitignore` 미수정.
- commit/push/PR/merge/reset/clean/stash **전혀 수행 안 함**.

## 18. 잔여 Risk

1. **`presents Doran as an honest unavailable service entry point` 회귀** (§14) — 원인과 정확한 파일/행까지 특정됨. 고치려면 `phase1_seed_synthetic.py`에 `doran` service_code 구독 행 추가(또는 테스트 기대값을 현재 제품 동작에 맞게 재검토) 필요 — **다음 작업으로 이관**, 이번엔 고치지 않음.
2. **`/api/configs/level.thresholds` 404** (§13) — 논블로킹, 화면은 정상 렌더링되나 격리 DB 시드 완전성 간극으로 기록.
3. Root `tests/e2e/specs/*.spec.ts`(4개 파일, `playwright.config.ts` 의존)는 여전히 `docker-compose.phase0.yml` 부재로 실행 불가 — 이번 작업은 Naran suite만 복구 대상이었으므로 범위 밖으로 남김.
4. 명칭(`와글와글` vs `몽글`) 문제는 이번 작업에서 다시 열지 않음 — PM 승인 R2 계약대로 미변경 유지.

## 19. 종료 Git 상태

```
git status --short (최종)
 M frontend/package-lock.json
 M frontend/package.json
 M frontend/src/App.tsx
 M tests/e2e/playwright.naran.config.ts
 M tests/e2e/specs-naran/01-shell.spec.ts
 M tests/e2e/test-results/.last-run.json
?? .env.phase0.example
?? docker-compose.phase1.yml
?? engineering/phase2/MONGLE_FE_E2E_HARNESS_RESTORE_REPORT.md
?? engineering/phase2/MONGLE_*.md (선행 작업 산출물 4건)
?? tests/e2e/artifacts/
?? tests/e2e/scripts/
?? tests/e2e/test-results/**(신규 테스트 실행 산출물, 노이즈)
```

- HEAD: 시작/종료 동일 `b0aea1d208f94ba928342d423c0f15048ca8b34d` — **커밋 없음**.
- push/merge/reset/clean/stash **없음**.
- `package-lock.json`/`package.json`은 선행 작업(`@types/node` 추가)의 변경 그대로이며, 이번 작업에서 추가 dependency를 넣지 않음(대규모 lockfile churn 없음, 18줄 추가 그대로 유지).

## 20. MONGLE-FE-ROUTE-ALIGNMENT-001의 PASS 승격 가능 여부

**아니오, 아직 승격 불가.** 그 작업의 CONDITIONAL 사유 2가지 중 "E2E 실행 불가"는 이번 작업으로 **해소**됐습니다(하네스가 복구되어 반복 가능·결정론적으로 실행됨). 그러나 그 실행 결과 **새로운 실패**(§14의 `doran` 서비스 픽스처 간극)가 발견되었으므로, 두 작업을 합쳐도 전체 그림은 여전히 CONDITIONAL입니다. 정확히는:

- MONGLE-FE-ROUTE-ALIGNMENT-001이 만든 코드 변경(404 route) 자체는 **E2E로 실증되어 PASS 수준의 증거를 확보**했습니다.
- 하지만 그 작업이 다루지 않았던 기존 `/naran/doran` 관련 테스트가 실제로는 실패 상태였다는 사실이 이번에 새로 드러났고, 이는 두 작업 모두의 범위 밖(픽스처 완전성)이므로 **별도 후속 작업**이 필요합니다.
