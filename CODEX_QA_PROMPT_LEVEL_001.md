# [Codex QA 프롬프트] P-HOTFIX-LEVEL-001: 레벨 시스템 정규화 + 누적 포인트 물리화 검증

> **지시자:** Claude Web (Main Architect)
> **실행자:** Codex (QA Engineer)
> **Task ID:** P-HOTFIX-LEVEL-001-QA
> **상태:** TODO → 진행중
> **목표:** LEVEL-001 구현의 BE API 런타임 정합성 + DB 스키마 무결성 + FE 연동 검증

---

## 🚨 QA 원칙

1. **프로덕션 코드 수정 금지** — 테스트 스크립트만 작성/실행. 소스코드 변경 시 즉시 FAIL.
2. **DB 상태 복원** — 테스트 후 생성된 데이터는 반드시 정리 (또는 트랜잭션 롤백).
3. **런타임 검증 우선** — 정적 분석만으로는 부족. 실제 API 호출 + DB 상태 확인 필수.
4. **FAIL 시 즉시 중단** — BLOCKER 발견 시 후속 테스트 스킵, 리포트 제출.

---

## Part 1: 정적 분석 (코드 구조 검증)

### S-1. 파일 존재 확인

```bash
# level_tier 도메인 5개 파일 존재 확인
for f in __init__.py models.py schema.py service.py router.py; do
  test -f backend/app/domains/level_tier/$f && echo "✅ level_tier/$f" || echo "❌ MISSING level_tier/$f"
done
```

**기대:** 5개 전부 ✅

### S-2. 모델 등록 확인

```bash
# all_models.py에 LevelTier import 존재
grep -c "LevelTier" backend/app/models/all_models.py
```

**기대:** 1 이상

### S-3. 라우터 등록 확인

```bash
# main.py에 level_tier_router include 존재
grep -c "level_tier" backend/app/main.py
```

**기대:** 1 이상

### S-4. Player 모델에 total_earned 존재

```bash
grep -c "total_earned" backend/app/domains/player/models.py
```

**기대:** 1 이상

### S-5. Player 스키마에 total_earned 존재

```bash
grep -c "total_earned" backend/app/domains/player/schema.py
```

**기대:** 1 이상

### S-6. mission/service.py에 _sync_total_earned 존재

```bash
grep -c "_sync_total_earned" backend/app/domains/mission/service.py
```

**기대:** 2 이상 (함수 정의 1 + 호출 1 이상)

### S-7. Thin Controller 준수

```bash
# level_tier/router.py에 비즈니스 로직(if/for/raise HTTPException) 없음
grep -cE "(if |for |raise HTTPException)" backend/app/domains/level_tier/router.py
```

**기대:** 0 (Depends, return만 존재)

### S-8. SQL Annotation 존재

```bash
# service.py 핵심 함수에 SQL 주석 존재
grep -c "\-\- \[SQL\]" backend/app/domains/level_tier/service.py
```

**기대:** 3 이상 (get_tiers_by_job, create_tier, get_player_level 등)

### S-9. 컴파일 검증

```bash
find backend -name "*.py" -exec python -m py_compile {} +
echo "py_compile exit code: $?"
```

**기대:** exit code 0

### S-10. FE 빌드 검증

```bash
cd frontend && npm run build 2>&1 | tail -5
```

**기대:** 0 errors

---

## Part 2: DB 스키마 검증

### D-1. level_tiers 테이블 존재 + 구조

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
  WHERE table_name = 'level_tiers'
  ORDER BY ordinal_position;
"
```

**기대 컬럼:** id, job_code, level, title, required_points, icon_path, milestone_type, milestone_data, created_at, updated_at

### D-2. 복합 유니크 제약 조건 확인

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT constraint_name, column_name
  FROM information_schema.constraint_column_usage
  WHERE table_name = 'level_tiers' AND constraint_name = 'uq_job_level';
"
```

**기대:** job_code, level 두 컬럼이 uq_job_level에 포함

### D-3. Seed 데이터 확인

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT job_code, level, title, required_points
  FROM level_tiers
  WHERE job_code = 'COMMON'
  ORDER BY level;
"
```

**기대:** 10행 (Lv.1 새싹 모험가 0P ~ Lv.10 월드 챔피언 1300P)

### D-4. players.total_earned 컬럼 존재

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT column_name, data_type, column_default
  FROM information_schema.columns
  WHERE table_name = 'players' AND column_name = 'total_earned';
"
```

**기대:** integer, default 0

### D-5. total_earned 초기값 정합성

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT p.id, p.name, p.total_earned,
         COALESCE(SUM(dp.earned), 0) AS daily_sum,
         p.total_earned - COALESCE(SUM(dp.earned), 0) AS drift
  FROM players p
  LEFT JOIN daily_points dp ON dp.player_id = p.id AND dp.deleted_at IS NULL
  WHERE p.deleted_at IS NULL
  GROUP BY p.id, p.name, p.total_earned
  ORDER BY p.id;
"
```

**기대:** drift 컬럼이 모든 행에서 0 (불일치 없음)

### D-6. level.thresholds JSON 폐기 확인

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT * FROM app_configs WHERE key = 'level.thresholds';
"
```

**기대:** 0 rows (삭제 완료) 또는 존재해도 FE에서 미참조 확인

### D-7. missions.template_id 컬럼 존재 (선행 핫픽스 검증)

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  SELECT column_name, data_type
  FROM information_schema.columns
  WHERE table_name = 'missions' AND column_name = 'template_id';
"
```

**기대:** integer (이전 핫픽스에서 추가됨)

---

## Part 3: BE API 런타임 검증 (핵심)

> **사전 조건:** Docker 컨테이너가 실행 중이어야 함.
> `docker-compose up -d` 확인 후 진행.

### 인증 토큰 획득

```bash
# 플레이어 로그인 (유빈, PIN=1234)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "pin": "1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token','FAIL'))")

echo "TOKEN: ${TOKEN:0:20}..."

# Admin 토큰 (관리자 계정으로 — 현재 admin_auth 구조에 맞춰 조정 필요)
# admin_auth가 별도라면 해당 방식으로 로그인
ADMIN_TOKEN=$TOKEN  # 임시: 동일 토큰 사용 (admin_auth 구조에 따라 조정)
```

### R-1. GET /api/level-tiers — 레벨 구간 목록 조회

```bash
RESULT=$(curl -s http://localhost:8000/api/level-tiers?job_code=COMMON)
echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert isinstance(data, list), 'FAIL: 배열이 아님'
assert len(data) == 10, f'FAIL: {len(data)}개 (기대: 10)'
assert data[0]['level'] == 1, 'FAIL: 첫 번째 레벨이 1이 아님'
assert data[0]['required_points'] == 0, 'FAIL: Lv.1 포인트가 0이 아님'
assert data[0]['job_code'] == 'COMMON', 'FAIL: job_code가 COMMON이 아님'
assert data[-1]['level'] == 10, 'FAIL: 마지막 레벨이 10이 아님'
assert data[-1]['required_points'] == 1300, 'FAIL: Lv.10 포인트가 1300이 아님'
# 오름차순 정렬 확인
for i in range(1, len(data)):
    assert data[i]['required_points'] > data[i-1]['required_points'], f'FAIL: 정렬 오류 Lv.{data[i][\"level\"]}'
print('✅ R-1 PASS: 10개 COMMON 레벨, 오름차순 정렬 정상')
"
```

### R-2. GET /api/level-tiers?job_code=NONEXIST — 존재하지 않는 직업 코드

```bash
RESULT=$(curl -s http://localhost:8000/api/level-tiers?job_code=NONEXIST)
echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert isinstance(data, list), 'FAIL: 배열이 아님'
assert len(data) == 0, f'FAIL: {len(data)}개 반환 (기대: 0)'
print('✅ R-2 PASS: 존재하지 않는 직업 코드 → 빈 배열')
"
```

### R-3. GET /api/level-tiers/player/{id} — 플레이어 레벨 조회

```bash
RESULT=$(curl -s http://localhost:8000/api/level-tiers/player/1?job_code=COMMON)
echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
required = ['player_id','total_earned','level','title','current_threshold','next_threshold','progress_percent']
for key in required:
    assert key in data, f'FAIL: {key} 필드 누락'
assert data['player_id'] == 1, 'FAIL: player_id 불일치'
assert isinstance(data['total_earned'], int), 'FAIL: total_earned가 정수가 아님'
assert isinstance(data['level'], int) and data['level'] >= 1, 'FAIL: level이 1 미만'
assert 0 <= data['progress_percent'] <= 100, f'FAIL: progress_percent 범위 초과 ({data[\"progress_percent\"]})'
assert data['next_threshold'] > data['current_threshold'], 'FAIL: next_threshold <= current_threshold'
print(f'✅ R-3 PASS: 플레이어 1 — Lv.{data[\"level\"]} {data[\"title\"]} ({data[\"total_earned\"]}P, {data[\"progress_percent\"]}%)')
"
```

### R-4. GET /api/level-tiers/player/9999 — 존재하지 않는 플레이어

```bash
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/level-tiers/player/9999)
echo "$HTTP_CODE" | python3 -c "
import sys
code = sys.stdin.read().strip()
assert code == '404', f'FAIL: HTTP {code} (기대: 404)'
print('✅ R-4 PASS: 존재하지 않는 플레이어 → 404')
"
```

### R-5. POST /api/level-tiers — 레벨 구간 추가 (중복 테스트 포함)

```bash
# 새 레벨 추가 (Lv.11)
RESULT=$(curl -s -X POST http://localhost:8000/api/level-tiers \
  -H "Content-Type: application/json" \
  -d '{"job_code":"COMMON","level":11,"title":"QA 테스트 레벨","required_points":1600}')
TIER_ID=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert data['level'] == 11, 'FAIL: level 불일치'
assert data['title'] == 'QA 테스트 레벨', 'FAIL: title 불일치'
assert data['required_points'] == 1600, 'FAIL: required_points 불일치'
print(data['id'])
")
echo "✅ R-5a PASS: Lv.11 추가 성공 (id=$TIER_ID)"

# 동일 (job_code, level) 중복 추가 시 에러
DUP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/level-tiers \
  -H "Content-Type: application/json" \
  -d '{"job_code":"COMMON","level":11,"title":"중복 테스트","required_points":1700}')
echo "$DUP_CODE" | python3 -c "
import sys
code = sys.stdin.read().strip()
assert code in ('400','409','500'), f'FAIL: HTTP {code} (기대: 400/409/500 — 유니크 제약 위반)'
print(f'✅ R-5b PASS: 중복 (COMMON, Lv.11) → HTTP {code}')
"

# 정리: 추가한 Lv.11 삭제
curl -s -X DELETE "http://localhost:8000/api/level-tiers/$TIER_ID" -o /dev/null
echo "✅ R-5c: 테스트 데이터 정리 완료"
```

### R-6. PUT /api/level-tiers/bulk — 벌크 저장 + 검증

```bash
# 벌크 저장 (5레벨로 축소)
RESULT=$(curl -s -X PUT http://localhost:8000/api/level-tiers/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "job_code": "QA_TEST",
    "tiers": [
      {"job_code":"QA_TEST","level":1,"title":"테스트1","required_points":0},
      {"job_code":"QA_TEST","level":2,"title":"테스트2","required_points":50},
      {"job_code":"QA_TEST","level":3,"title":"테스트3","required_points":150}
    ]
  }')
echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert len(data) == 3, f'FAIL: {len(data)}개 반환 (기대: 3)'
assert all(t['job_code'] == 'QA_TEST' for t in data), 'FAIL: job_code 불일치'
print('✅ R-6a PASS: QA_TEST 벌크 저장 3개')
"

# Lv.1이 0P가 아닌 경우 → 400 에러
ERR_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT http://localhost:8000/api/level-tiers/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "job_code": "QA_TEST2",
    "tiers": [
      {"job_code":"QA_TEST2","level":1,"title":"오류","required_points":10}
    ]
  }')
echo "$ERR_CODE" | python3 -c "
import sys
code = sys.stdin.read().strip()
assert code == '400', f'FAIL: HTTP {code} (기대: 400 — Lv.1은 0P 필수)'
print(f'✅ R-6b PASS: Lv.1 != 0P → HTTP {code}')
"

# 정리: QA_TEST 데이터 삭제
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "DELETE FROM level_tiers WHERE job_code IN ('QA_TEST','QA_TEST2');"
echo "✅ R-6c: 테스트 데이터 정리 완료"
```

### R-7. 미션 완료 → total_earned 동기화 검증 (핵심 ACID 테스트)

```bash
# 현재 total_earned 기록
BEFORE=$(docker exec -i mc-db psql -U mc_admin -d mc_festival -t -A -c "
  SELECT total_earned FROM players WHERE id = 1;
")
echo "변경 전 total_earned: $BEFORE"

# active 미션 1건 찾기 (player_id=1)
MISSION_ID=$(docker exec -i mc-db psql -U mc_admin -d mc_festival -t -A -c "
  SELECT id FROM missions
  WHERE player_id = 1 AND status = 'active' AND deleted_at IS NULL
  ORDER BY id DESC LIMIT 1;
")

if [ -z "$MISSION_ID" ]; then
  echo "⚠️ R-7 SKIP: active 미션 없음 — 수동 테스트 필요"
else
  MISSION_POINT=$(docker exec -i mc-db psql -U mc_admin -d mc_festival -t -A -c "
    SELECT point FROM missions WHERE id = $MISSION_ID;
  ")
  echo "테스트 미션: id=$MISSION_ID, point=$MISSION_POINT"

  # pending_approval로 변경
  curl -s -X PATCH "http://localhost:8000/api/missions/$MISSION_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"status":"pending_approval"}' -o /dev/null

  # completed로 변경 (승인)
  curl -s -X PATCH "http://localhost:8000/api/missions/$MISSION_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"status":"completed"}' -o /dev/null

  # total_earned 확인
  AFTER=$(docker exec -i mc-db psql -U mc_admin -d mc_festival -t -A -c "
    SELECT total_earned FROM players WHERE id = 1;
  ")
  EXPECTED=$((BEFORE + MISSION_POINT))

  python3 -c "
before = int('$BEFORE')
after = int('$AFTER')
point = int('$MISSION_POINT')
expected = before + point
assert after == expected, f'FAIL: total_earned {after} != {expected} (before={before}, point={point})'
print(f'✅ R-7a PASS: 미션 완료 → total_earned {before} → {after} (+{point})')
"

  # 되돌리기 (admin revert) — 엔드포인트가 있는 경우
  REVERT_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "http://localhost:8000/api/admin/missions/$MISSION_ID/revert" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

  if [ "$REVERT_CODE" = "200" ]; then
    REVERTED=$(docker exec -i mc-db psql -U mc_admin -d mc_festival -t -A -c "
      SELECT total_earned FROM players WHERE id = 1;
    ")
    python3 -c "
before = int('$BEFORE')
reverted = int('$REVERTED')
assert reverted == before, f'FAIL: revert 후 total_earned {reverted} != {before}'
print(f'✅ R-7b PASS: 미션 되돌리기 → total_earned {before}으로 복원')
"
  else
    echo "⚠️ R-7b SKIP: admin revert 엔드포인트 HTTP $REVERT_CODE"
  fi
fi
```

### R-8. 하이브리드 자동 확장 검증

```bash
# total_earned를 1500으로 수동 설정 (Lv.10 = 1300P 초과)
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  UPDATE players SET total_earned = 1500 WHERE id = 2;
"

RESULT=$(curl -s http://localhost:8000/api/level-tiers/player/2?job_code=COMMON)
echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert data['level'] >= 11, f'FAIL: level={data[\"level\"]} (기대: 11+ — 1500P는 Lv.10(1300P) 초과)'
assert '자동' in data['title'] or data['level'] > 10, 'FAIL: 하이브리드 확장 미동작'
print(f'✅ R-8 PASS: 1500P → Lv.{data[\"level\"]} \"{data[\"title\"]}\" (하이브리드 자동 확장 정상)')
"

# 복원
docker exec -i mc-db psql -U mc_admin -d mc_festival -c "
  UPDATE players SET total_earned = 0 WHERE id = 2;
"
echo "✅ R-8 복원: player 2 total_earned → 0"
```

### R-9. 템플릿 포인트 변경 → completed 미션 차액 + total_earned 정합성

```bash
echo "⚠️ R-9: 템플릿 변경 전파 + total_earned 동기화는 수동 검증 권장"
echo "  시나리오: 반복 미션(10P) 배정 → 완료 승인 → 템플릿 포인트 5P로 변경"
echo "  확인 사항:"
echo "    1) 완료된 미션의 point가 10 → 5로 변경"
echo "    2) daily_points.earned가 -5 보정"
echo "    3) players.total_earned가 -5 보정"
echo "  → _propagate_template_change + _sync_total_earned 연동 확인"
```

---

## Part 4: FE 연동 검증

### F-1. ExpBar API 호출 확인

```bash
# FE 빌드 산출물에서 기존 level.thresholds 참조 제거 확인
grep -r "level.thresholds" frontend/src/ 2>/dev/null | grep -v node_modules | grep -v ".git"
```

**기대:** 0건 (완전 제거) 또는 주석만 남아있음

### F-2. 새 API 엔드포인트 참조 확인

```bash
grep -r "level-tiers" frontend/src/ 2>/dev/null | grep -v node_modules
```

**기대:** 1건 이상 (dashboardApi.ts 또는 유사 파일)

### F-3. levelInfo 상태 사용 확인

```bash
grep -r "levelInfo" frontend/src/ 2>/dev/null | grep -v node_modules
```

**기대:** 2건 이상 (useDashboard.ts + ExpBar.tsx)

---

## Part 5: 종합 리포트 템플릿

```
═══════════════════════════════════════════
P-HOTFIX-LEVEL-001-QA 종합 리포트
═══════════════════════════════════════════
실행일시: [YYYY-MM-DD HH:MM]
실행자: Codex (QA Engineer)

[Part 1: 정적 분석]
S-1  파일 존재:        ✅/❌
S-2  all_models 등록:  ✅/❌
S-3  main.py 등록:     ✅/❌
S-4  Player model:     ✅/❌
S-5  Player schema:    ✅/❌
S-6  _sync_total_earned: ✅/❌
S-7  Thin Controller:  ✅/❌
S-8  SQL Annotation:   ✅/❌
S-9  py_compile:       ✅/❌
S-10 npm build:        ✅/❌

[Part 2: DB 스키마]
D-1  level_tiers 구조:      ✅/❌
D-2  복합 유니크:            ✅/❌
D-3  Seed 데이터:            ✅/❌
D-4  total_earned 컬럼:      ✅/❌
D-5  total_earned 정합성:    ✅/❌
D-6  JSON 폐기:              ✅/❌
D-7  template_id 컬럼:       ✅/❌

[Part 3: API 런타임] ★ 핵심
R-1  레벨 구간 조회:         ✅/❌
R-2  미존재 직업 코드:       ✅/❌
R-3  플레이어 레벨 조회:     ✅/❌
R-4  미존재 플레이어:        ✅/❌
R-5  추가 + 중복 검증:       ✅/❌
R-6  벌크 저장 + 검증:       ✅/❌
R-7  미션 완료→total_earned: ✅/❌ ← BLOCKER
R-8  하이브리드 자동 확장:   ✅/❌
R-9  템플릿 전파 정합성:     수동/✅/❌

[Part 4: FE 연동]
F-1  기존 JSON 참조 제거:    ✅/❌
F-2  새 API 참조:            ✅/❌
F-3  levelInfo 상태:         ✅/❌

═══════════════════════════════════════════
총 결과: PASS / FAIL (BLOCKER: _건)
═══════════════════════════════════════════
BLOCKER 목록:
- (없음 또는 상세 기술)

비고:
- (특이사항)
```
