# MONGLE_W6_1_EXECUTION_BLOCKERS

> Relocated from a root-level `CLAUDE_ACTIVE.md` this same session — that file was newly created (not a
> pre-existing project file) and its write path (`/`) fell outside this task's allowed scope
> (`frontend/**` + `engineering/phase2/**`). PM instructed the move; the root copy has been deleted.
> Owner: `MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001` and its required follow-up,
> `MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001`.
> Last updated: 2026-07-31 (PM correction — Verdict capped at CONDITIONAL, E2E framing corrected,
> sole-writer note added).

---

## 1. Blocking item — PM action required before Wave 6.2 can start

### PM-ACTION-001 — Mongle Wave 6.1 Playwright E2E closeout on Mac/Docker environment

- **무엇을**: `tests/e2e/playwright.mongle.config.ts` 기반 Mongle Playwright suite를
  Mac/OrbStack Docker 환경에서 **cold-start 2회 연속** 실행
  (`./scripts/start-mongle-phase1.sh` → `docker-compose.phase1.yml` 격리 스택,
  포트 15434/18001/13001), Foundation 구현(색상/타이포/spacing/Primitive/responsive) 이후 상태 기준.
- **기대값**: 두 번 모두 66 passed / 0 failed / 4 intentional skipped, 신규 console error 0,
  Foundation 변경 전후 대표 화면 시각 비교에서 UNEXPECTED_SCREEN_DELTA/MATERIAL_REGRESSION 없음.
- **왜 PM이 직접**: 이 WSL 세션에는 Docker가 없음 (`/usr/bin/docker`가
  `/mnt/wsl/docker-desktop/...`를 가리키는 broken symlink, `docker-desktop` 마운트 자체가 부재.
  `/mnt/wsl/podman-sockets/`는 존재하나 `podman` CLI 바이너리 없음 — 실측 2026-07-31).
- **E2E 상태 구분 (혼동 금지)**:
  ```
  PREVIOUSLY_REPORTED_E2E_REFERENCE: 66 passed / 0 failed / 4 skipped   (과거 참고치, 이번 변경의 baseline 아님)
  CURRENT_PRE_IMPLEMENTATION_E2E:    NOT_RUN — Docker unavailable in WSL
  CURRENT_POST_IMPLEMENTATION_E2E:   NOT_RUN — pending Mac/Docker closeout
  REGRESSION_0:                      NOT CLAIMABLE
  ```
- **후속 Task**: `MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001` (Mac/Docker에서 lint/build 재확인 +
  cold-start 2회 + 시각 회귀 확인 + 컨테이너/볼륨 정리 + PASS/FAIL 확정).
- **Gate 규칙**: 이 항목이 PASS로 닫히기 전에는 `MONGLE-W6-2-A1-MOBILE-RECONSTRUCTION-001`을
  시작하지 않는다.
- **완료 조건**: PM이 Mac에서 2회 cold-start 결과 확인 후 이 항목을 CLOSED로 표시하고,
  `MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md`의 해당 섹션을 실측치로 갱신.

---

## 2. Verdict ceiling for MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001

E2E를 실행하지 못했으므로 이 Task는 PASS가 될 수 없다.

```
최대 Verdict: CONDITIONAL
최종 상태 문구: CONDITIONALLY_IMPLEMENTED_AWAITING_DOCKER_E2E_CLOSEOUT
금지 문구: READY_FOR_MONGLE_W6_2_A1_MOBILE_RECONSTRUCTION / E2E PASS / baseline E2E PASS /
           regression 0(무조건적 주장) / Wave 6.1 complete PASS
```

## 3. Sole-writer note

Wave 6.1 구현은 background agent 1개(`agentId a2300ada5d1d4634d`)가 이 worktree의 유일한 writer로
진행 중이며, `frontend/**`와 `MONGLE_W6_1_*` 문서 세트만 건드린다. 이 문서(`MONGLE_W6_1_EXECUTION_BLOCKERS.md`)와
루트 `CLAUDE_ACTIVE.md` 삭제는 오케스트레이팅 세션이 별도로 수행한 것이며, agent의 Start/End Gate
비교에서 "설명되지 않은 동시 변경"으로 오판되지 않도록 agent에게도 통지했다.

## 4. 리스크 (from relocated CLAUDE_ACTIVE.md)

- Docker 부재로 이 WSL 세션에서는 Mongle Playwright cold-start 회귀를 직접 검증할 수 없음.
- `frontend/package-lock.json`(삭제, 미커밋) / `frontend/pnpm-lock.yaml`(신규, 미커밋) — npm→pnpm
  전환이 승인 완료된 것으로 단정하지 않음(`PRE_EXISTING_PRESERVED_DIRTY`로만 보존, Wave 6.1에서도
  lockfile 변경 없이 진행).

## 5. 최근 실측 상태

| 항목 | 값 |
|---|---|
| 실측일 | 2026-07-31 |
| worktree / branch | `/appl/point-festival` / `dev-newmarkp` |
| HEAD | `08619298ff7b7a175ba4d30537be92e0387b2eb4` |
| 환경 | Linux/WSL (company checkout) — Docker 없음, npm 11.13.0 / pnpm 10.32.1 / node v26.2.0 사용 가능 |
| 로컬 실행 중 프로세스 | `postgres`(5432, DB `mc_festival`) / `uvicorn app.main:app`(8000) / `pnpm dev`→`vite`(5173) — 이전 세션 잔존, Mongle 격리 fixture 스택(mc_phase1)과는 별개 |
| Wave 6.0C | CONDITIONAL 확정, closeout 문서·태블릿 archive 완료 |
| Wave 6.1 | 구현 진행 중 (background agent), Verdict 상한 CONDITIONAL로 고정 |
