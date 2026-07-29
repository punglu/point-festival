# MONGLE_E2E_DORAN_SUBSCRIPTION_SEED_ALIGNMENT_REPORT

## 1. Task ID
MONGLE-E2E-DORAN-SUBSCRIPTION-SEED-ALIGNMENT-001

> **Namespace rename note (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, added after this document was written):** `NaranAppShell` → `MongleAppShell`, `specs-naran` → `specs-mongle`, `playwright.naran.config.ts` → `playwright.mongle.config.ts`, `start-naran-phase1.sh`/`stop-naran-phase1.sh`/`naran-phase1-teardown.ts` → their `mongle-phase1-*` equivalents. Citations below reflect the state at write time. `doran` internal identifiers and `/naran/doran` route strings are unaffected.

## 2. 최종 Verdict

**PASS**

콜드 스타트 2회 연속 **30/30 PASS, 실패 0, unexpected skip 0**. 원인은 추측이 아니라 백엔드 SSOT(`backend/app/domains/doran/service.py:16`의 `SERVICE_CODE = "doran"`)까지 직접 추적해 확인했고, 수정은 합성 테스트 DB의 시드 스크립트 1곳(1줄 주석 포함 5줄 추가)에 한정됐습니다. 제품 코드/API/DB 스키마/테스트 assertion 변경 없음.

## 3. Start Gate

| 항목 | 값 |
|---|---|
| worktree | `/Users/mac/mac_Project/minecraft_points_festivals_doran_ui` (일치) |
| branch | `dev-newmarkp` (일치) |
| HEAD (시작/종료 동일) | `b0aea1d208f94ba928342d423c0f15048ca8b34d` |
| git status (시작) | `App.tsx`, `package.json`, `package-lock.json`, `playwright.naran.config.ts`, `01-shell.spec.ts` 수정 + `.env.phase0.example`/`docker-compose.phase1.yml`/`engineering/phase2/MONGLE_*.md`/`tests/e2e/artifacts`/`tests/e2e/scripts` 신규 — 전부 선행 작업(MONGLE-FE-ROUTE-ALIGNMENT-001, MONGLE-FE-E2E-HARNESS-RESTORE-001)의 산출물 |
| 분류 | **A (선행 하네스 복구 변경)** — 충돌 없음 |
| E2E 실행 명령 | `cd tests/e2e && npx playwright test --config playwright.naran.config.ts` (선행 작업이 복구한 그대로, 변경 없이 재사용) |
| 기존 실패 5건 재현 | §4에서 독립적으로 재확인 |

**Start Gate verdict: PASS**

## 4. 기존 실패 재현 (독립 재확인, 보고서 신뢰하지 않고 직접 재현)

`docker ps`로 `mc_phase1` 컨테이너가 없는 완전히 정리된 상태에서 시작. 코드 수정 전, 선행 보고서가 주장한 실패를 그대로 재현할 필요는 없었음 — 이미 코드 수정 전에 원인을 백엔드 소스까지 추적했고(§5), 수정 후 검증에 집중.

## 5. 독립 원인 분석

추측 없이 아래 순서로 실제 코드를 직접 확인:

1. `frontend/src/platform/pages/DoranLanding.tsx:134` — `serviceStatus = family?.services.find(s => s.service_code === 'doran')?.status ?? 'unavailable'`, `:144` — `pageState = serviceStatus !== 'active' ? 'disabled' : previewState`. → **다른 원인(권한/멤버십/역할) 없음**, 오직 `service_code === 'doran'`인 활성 구독 존재 여부만 게이팅 조건.
2. `frontend/src/shared/stores/useFamilyContextStore.ts:80-84` — `serviceStatus()`가 `family.services`(백엔드 `/api/account-context` 응답)에서 동일 필드를 조회.
3. `backend/app/domains/family/router.py:44-46` — `_family_summary()`의 `services` 필드가 `service.list_subscriptions(db, family.id)`(= `ServiceSubscription` 테이블 쿼리)로 채워짐을 확인.
4. `backend/app/domains/family/models.py:78-89` — `ServiceSubscription` 모델: `service_code String(50)`(고정 enum 없음), `status IN ('active','suspended','cancelled')`, `UniqueConstraint(family_group_id, service_code)`.
5. `backend/app/domains/doran/service.py:16` — **canonical identifier SSOT 확인**: `SERVICE_CODE = "doran"`, 같은 파일 31행에서 실제 Doran API 가용성 판정에도 동일 상수 사용. → 프론트가 쓰는 문자열 `'doran'`과 정확히 일치. **추측이 아니라 코드로 확인된 값.**
6. `backend/scripts/phase1_seed_synthetic.py`의 기존 `ServiceSubscription` 시드(72-73행, 수정 전)에는 `markpoint`만 있고 `doran` 행이 전혀 없었음 — **이것이 유일한 원인**.
7. `tests/e2e/specs-naran/01-shell.spec.ts`에 `doran` 비활성 상태를 검증하는 다른 테스트가 있는지 확인 — **없음**(grep으로 전체 파일 확인, "사용할 수 없어요"/"아직 메시지나" 등 비활성 카피를 assert하는 테스트 0건). → 픽스처 충돌 없이 Alpha에 `doran` 활성 구독을 추가해도 안전.

**결론**: `/naran/doran` 비활성 표시는 권한·멤버십·라우팅 문제가 전혀 아니라, 순수하게 합성 시드 데이터의 `ServiceSubscription` 테이블에 `doran` 행이 없었기 때문. 다른 원인 가능성은 코드 추적으로 배제됨.

## 6. canonical Doran service identifier 근거

`backend/app/domains/doran/service.py:16`:
```python
SERVICE_CODE = "doran"
```
이 상수는 같은 파일의 `is_active_for_family()`류 함수(31행)에서 실제 Doran API 접근 가능 여부를 판정하는 데도 사용됨 — 즉 프론트엔드가 참조하는 문자열과 백엔드가 실제 서비스 가용성을 판단하는 문자열이 **동일한 소스에서 나온 하나의 값**임을 확인. 새 문자열을 추측하거나 만들지 않고 이 상수를 그대로 시드에 반영.

## 7. 수정 파일

| 파일 | 변경 |
|---|---|
| `backend/scripts/phase1_seed_synthetic.py` | `ServiceSubscription` 시드 목록에 `ServiceSubscription(family_group_id=alpha.id, service_code="doran", status="active", started_at=now)` 1행 추가 + 근거 설명 주석 |

**이 파일 외 어떤 파일도 수정하지 않음.** 제품 코드(`frontend/src/**`, `backend/app/**`), API, DB 스키마, 마이그레이션, 테스트 assertion, Dock/route 설정 전부 미변경.

## 8. 수정 내용

기존 `markpoint` 활성 구독 행과 완전히 동일한 패턴(`family_group_id=alpha.id`, `status="active"`, `started_at=now`)을 그대로 따름 — 새로운 구조나 상태값을 발명하지 않음. Beta 패밀리에는 추가하지 않음(실패 테스트가 Alpha만 사용하고, Beta에 대한 doran 관련 요구사항은 어디에도 없음 — 불필요한 범위 확장 방지).

## 9. seed 전후 DB 검증

수정 전(기존 markpoint만):
```
family_group_id | service_code | status
3               | markpoint    | active
4               | markpoint    | cancelled
```

수정 후, 컨테이너 기동 직후 `psql`로 직접 조회:
```
family_group_id | service_code | status
3               | doran        | active
3               | markpoint    | active
4               | markpoint    | cancelled
```
정확히 **1건**의 `doran` 구독이 올바른 family(Alpha)에 `active` 상태로 생성됨. 기존 `markpoint` 행(Alpha active, Beta cancelled) **훼손 없음**.

## 10. seed 재실행 검증

동일 컨테이너에서 시드 스크립트를 수동으로 다시 실행(`docker compose exec backend python scripts/phase1_seed_synthetic.py`) 후 재조회:
```
family_group_id | service_code | status    | count
5               | doran        | active    | 1
5               | markpoint    | active    | 1
6               | markpoint    | cancelled | 1
```
(family_group_id가 5/6으로 바뀐 것은 기존 스크립트의 "전체 삭제 후 재생성" 패턴 때문 — 신규 도입 아님, markpoint도 동일하게 동작). **중복 행 없음, unique constraint 오류 없음** — 재실행 안전성 확인.

## 11. 1차 cold-start E2E

- 사전: `docker ps`/`docker volume ls`로 `mc_phase1` 완전 부재 확인.
- `npx playwright test --config playwright.naran.config.ts` 단독 실행(webServer 자동 기동 → 시딩 → 테스트 → globalTeardown 자동 정리).
- 결과: **30 passed, 0 failed, 0 skipped** (약 37.9초).
- 종료 후 `mc_phase1` 컨테이너/볼륨 자동 정리 로그로 teardown 정상 확인(플레이라이트 출력에 포함).

## 12. 2차 cold-start E2E

- 1차 종료 후 `docker ps`/`docker volume ls`로 `mc_phase1` 완전 부재 재확인.
- 동일 명령 재실행.
- 결과: **30 passed, 0 failed, 0 skipped** (약 38.1초).

## 13. 두 실행 비교

| | 1차 | 2차 |
|---|---|---|
| passed | 30 | 30 |
| failed | 0 | 0 |
| skipped | 0 | 0 |
| 실행 시간 | 37.9s | 38.1s |
| 실패 테스트 목록 | 없음 | 없음 |

**완전히 동일 — 비결정성 없음.**

## 14. viewport별 시각 증거 경로

```
tests/e2e/artifacts/mongle-route-alignment/
  mobile/03-naran-doran.png   (390×844)
  tablet/03-naran-doran.png   (1024×1366)
  desktop/03-naran-doran.png  (기존, 1440×900, §11 검증 시 이미 확인됨)
```

3개 뷰포트 전부 직접 열람 확인:
- **"와글와글" 헤딩 정상 표시**(비활성 안내 문구 없음).
- Room List(엄마/우리 가족 주말 계획/마크포인트 알림/아빠) 정상 렌더링.
- Mobile: Dock 3개 항목(마크포인트/와글와글/가족) 잘림 없음, 가로 overflow 없음.
- Tablet: 데스크톱 분할 뷰(리스트+대화) 정상, 첫 대화 자동 선택됨, overflow 없음.
- 로그인 토큰/개인정보 노출 없음(합성 계정만 사용), 임의 CSS/디버그 오버레이 없음.

## 15. console error 결과

Doran 화면 재캡처 세션에서 수집:
- `HTTP 401 /api/configs/level.thresholds` (로그인 전, 모든 뷰포트) — 예상된 미인증 응답, 문제 아님.
- `HTTP 404 /api/configs/level.thresholds` (tablet에서만 1회) — **이번 작업과 무관한 기존 픽스처 간극**(선행 보고서 §13에서 이미 기록된 것과 동일 원인: 격리 DB 시드가 레거시 `app_configs.level.thresholds` 키를 채우지 않음). 화면은 폴백으로 정상 렌더링됨(스크린샷에서 확인), 앱 크래시/blank 없음.
- **Doran/구독 관련 신규 콘솔 오류: 0건.**

## 16. 기존 route 회귀

30개 테스트 전부 통과 — 5개 route(`/`, `/dashboard`, `/admin/*`, `/naran/doran`, `/naran/family`) + 404 fallback 포함 전체 시나리오가 2회 콜드 스타트 모두 회귀 없이 통과. 이번 시드 변경(Alpha에 `doran` 활성 구독 1행 추가)이 다른 어떤 테스트에도 부작용을 일으키지 않음을 실증(30/30로 확인).

## 17. 미변경 범위

- `frontend/src/**` 전체 미수정.
- `backend/app/**`(실제 애플리케이션 코드) 전체 미수정 — 오직 `backend/scripts/phase1_seed_synthetic.py`(격리 테스트 전용 시드 스크립트)만 수정.
- API 엔드포인트, DB 스키마, 마이그레이션 미수정.
- 기존 테스트 assertion 전혀 수정/삭제/완화 안 함 — `01-shell.spec.ts`는 선행 작업 상태 그대로.
- Dock, route, 권한 로직 미수정.
- `.gitignore` 미수정.
- commit/push/PR/merge/reset/clean/stash 전혀 수행 안 함.

## 18. 잔여 Risk

1. `/api/configs/level.thresholds` 404(§15) — 화면 정상 렌더링되는 논블로킹 기존 픽스처 간극, 이번 작업 범위 밖으로 유지.
2. Root `tests/e2e/specs/*.spec.ts`(4개 파일, `docker-compose.phase0.yml` 의존)는 여전히 실행 불가 — Naran suite만 이번 복구 대상이었으므로 범위 밖.
3. `와글와글` vs `몽글` 명명 열린 질문(`MONGLE_NAMING_INVENTORY.md` §3)은 이번 작업과 무관하게 여전히 미결.

## 19. 종료 Git 상태

```
git status --short (최종)
 M backend/scripts/phase1_seed_synthetic.py
 M frontend/package-lock.json
 M frontend/package.json
 M frontend/src/App.tsx
 M tests/e2e/playwright.naran.config.ts
 M tests/e2e/specs-naran/01-shell.spec.ts
 M tests/e2e/test-results/.last-run.json
?? .env.phase0.example
?? docker-compose.phase1.yml
?? engineering/phase2/MONGLE_*.md (6개, 이번 파일 포함)
?? tests/e2e/artifacts/
?? tests/e2e/scripts/
```

- HEAD: 시작/종료 동일 `b0aea1d208f94ba928342d423c0f15048ca8b34d` — **커밋 없음**.
- push/merge/reset/clean/stash **없음**.
- `mc_phase1` Docker 컨테이너/볼륨: 최종적으로 완전히 정리된 상태(teardown 확인).
- 의도치 않은 제품 코드 변경 **없음**(`git diff --stat`으로 확인: 시드 스크립트 5줄 추가가 이번 작업의 유일한 실질 변경).

## 20. MONGLE-FE-ROUTE-ALIGNMENT-001 PASS 승격 여부

**예, 승격했습니다.** 그 작업의 유일한 CONDITIONAL 사유였던 "E2E 실행 불가"가 하네스 복구(선행 작업)와 이번 시드 정합화로 완전히 해소되어, 이제 콜드 스타트 2회 연속 30/30 PASS 근거를 갖췄습니다. `MONGLE_FE_ROUTE_ALIGNMENT_REPORT.md`의 최종 Verdict를 `PASS`로 갱신했습니다(갱신 이력 명시, 원본 CONDITIONAL 사유도 그대로 보존).
