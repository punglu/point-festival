#!/bin/bash
set -e
BASE="${PHASE0_API_BASE_URL:-http://localhost:18000}"
PASS=0
FAIL=0

# 관리자 토큰 획득
ADMIN_TOKEN=$(curl -s -X POST "$BASE/api/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"dad","password":"admin1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 플레이어 토큰 획득 (PIN 1234)
PLAYER_TOKEN=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"player_id":1,"pin":"1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "=== P-HOTFIX-WEEKLY-001 API 테스트 ==="

# T1: 주간 미션 조회
echo -n "T1 주간 미션 조회... "
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/missions/weekly?player_id=1&week_start=2026-03-30" \
  -H "Authorization: Bearer $PLAYER_TOKEN")
if [ "$R" = "200" ]; then echo "PASS"; ((PASS++)); else echo "FAIL ($R)"; ((FAIL++)); fi

# T2: Admin 주간 요약
echo -n "T2 Admin 주간 요약... "
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/weekly-summary?week_start=2026-03-30" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
if [ "$R" = "200" ]; then echo "PASS"; ((PASS++)); else echo "FAIL ($R)"; ((FAIL++)); fi

# T3: Admin 일괄 승인 (빈 대상도 200이어야 함)
echo -n "T3 Admin 일괄 승인... "
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/admin/missions/bulk-approve?player_id=1&date=2026-04-04" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
if [ "$R" = "200" ]; then echo "PASS"; ((PASS++)); else echo "FAIL ($R)"; ((FAIL++)); fi

# T4: 주간 미션 조회 — 비인증 시 401
echo -n "T4 비인증 주간 조회 거부... "
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/missions/weekly?player_id=1&week_start=2026-03-30")
if [ "$R" = "401" ] || [ "$R" = "403" ]; then echo "PASS"; ((PASS++)); else echo "FAIL ($R)"; ((FAIL++)); fi

# T5: Admin API — 플레이어 토큰으로 접근 거부
echo -n "T5 Player로 Admin API 거부... "
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/admin/weekly-summary?week_start=2026-03-30" \
  -H "Authorization: Bearer $PLAYER_TOKEN")
if [ "$R" = "401" ] || [ "$R" = "403" ]; then echo "PASS"; ((PASS++)); else echo "FAIL ($R)"; ((FAIL++)); fi

# T6: 주간 요약 응답 구조 확인
echo -n "T6 주간 요약 응답 구조... "
BODY=$(curl -s "$BASE/api/admin/weekly-summary?week_start=2026-03-30" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
HAS_PLAYERS=$(echo "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if 'players' in d and 'week_start' in d else 'fail')")
if [ "$HAS_PLAYERS" = "ok" ]; then echo "PASS"; ((PASS++)); else echo "FAIL"; ((FAIL++)); fi

echo ""
echo "=== 결과: $PASS PASS / $FAIL FAIL ==="
