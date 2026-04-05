#!/bin/bash
# reset-history.sh — 이력 데이터 초기화 (계정/설정 유지)
# 사용법: ./reset-history.sh [--include-templates]
#   --include-templates: 미션 템플릿도 함께 초기화
set -e

echo "⚠️  이력 데이터 초기화 (미션/포인트/채팅/알림/피드백/차감/로그인로그)"
echo "   계정, PIN, 앱 설정, 미션 템플릿은 유지됩니다."
echo ""

# 템플릿 포함 여부
INCLUDE_TEMPLATES=false
if [ "$1" = "--include-templates" ]; then
    INCLUDE_TEMPLATES=true
    echo "   ⚠️  미션 템플릿도 함께 초기화됩니다."
    echo ""
fi

read -p "정말 초기화하시겠습니까? (yes 입력): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "취소되었습니다."
    exit 0
fi

echo ""
echo "=== 이력 데이터 초기화 중... ==="

TEMPLATE_SQL=""
if [ "$INCLUDE_TEMPLATES" = true ]; then
    TEMPLATE_SQL="TRUNCATE mission_templates RESTART IDENTITY CASCADE;"
fi

DB_USER="${POSTGRES_USER:-mc_admin}"
DB_NAME="${POSTGRES_DB:-mc_festival}"

docker exec -i mc-db psql -U "$DB_USER" -d "$DB_NAME" << SQL
BEGIN;

-- 이력 데이터 삭제 (FK 의존성 순서)
TRUNCATE chat_messages RESTART IDENTITY CASCADE;
TRUNCATE notifications RESTART IDENTITY CASCADE;
TRUNCATE login_logs RESTART IDENTITY CASCADE;
TRUNCATE feedback_replies RESTART IDENTITY CASCADE;
TRUNCATE feedbacks RESTART IDENTITY CASCADE;
TRUNCATE deductions RESTART IDENTITY CASCADE;
TRUNCATE daily_points RESTART IDENTITY CASCADE;
TRUNCATE missions RESTART IDENTITY CASCADE;
${TEMPLATE_SQL}

-- player_auth 잠금 상태 초기화
UPDATE player_auth SET login_attempts = 0, lock_until = NULL;

COMMIT;
SQL

echo ""
echo "✅ 초기화 완료"
echo "   유지된 항목: players, player_auth, admin_auth, app_configs$([ "$INCLUDE_TEMPLATES" = false ] && echo ", mission_templates")"
echo "   삭제된 항목: missions, daily_points, deductions, feedbacks, feedback_replies, chat_messages, notifications, login_logs$([ "$INCLUDE_TEMPLATES" = true ] && echo ", mission_templates")"
