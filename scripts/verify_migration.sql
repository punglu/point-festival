-- ============================================
-- 데이터 마이그레이션 정합성 검증
-- 실행: psql -d mc_festival -f scripts/verify_migration.sql
-- ============================================

-- 1. 테이블별 레코드 수
SELECT 'players' AS tbl, COUNT(*) AS cnt, 2 AS expected FROM players
UNION ALL SELECT 'player_auth', COUNT(*), 2 FROM player_auth
UNION ALL SELECT 'admin_auth', COUNT(*), 2 FROM admin_auth
UNION ALL SELECT 'missions', COUNT(*), 140 FROM missions
UNION ALL SELECT 'cheer_messages', COUNT(*), 12 FROM cheer_messages
UNION ALL SELECT 'feedbacks', COUNT(*), 63 FROM feedbacks
UNION ALL SELECT 'feedback_replies', COUNT(*), 2 FROM feedback_replies
UNION ALL SELECT 'deductions', COUNT(*), 11 FROM deductions
UNION ALL SELECT 'daily_points', COUNT(*), 42 FROM daily_points
UNION ALL SELECT 'notifications', COUNT(*), 86 FROM notifications
UNION ALL SELECT 'app_configs', COUNT(*), 3 FROM app_configs
UNION ALL SELECT 'login_logs', COUNT(*), 149 FROM login_logs
ORDER BY tbl;

-- 2. FK orphan 검사 (모두 0이어야 함)
SELECT 'orphan_player_auth' AS chk, COUNT(*) AS cnt
FROM player_auth pa LEFT JOIN players p ON pa.player_id = p.id WHERE p.id IS NULL
UNION ALL SELECT 'orphan_missions', COUNT(*)
FROM missions m LEFT JOIN players p ON m.player_id = p.id WHERE p.id IS NULL
UNION ALL SELECT 'orphan_feedbacks', COUNT(*)
FROM feedbacks f LEFT JOIN players p ON f.player_id = p.id WHERE p.id IS NULL
UNION ALL SELECT 'orphan_deductions', COUNT(*)
FROM deductions d LEFT JOIN players p ON d.player_id = p.id WHERE p.id IS NULL
UNION ALL SELECT 'orphan_notifications', COUNT(*)
FROM notifications n LEFT JOIN players p ON n.player_id = p.id WHERE p.id IS NULL
UNION ALL SELECT 'orphan_login_logs', COUNT(*)
FROM login_logs ll LEFT JOIN players p ON ll.player_id = p.id WHERE p.id IS NULL;

-- 3. PIN 해시 검증
SELECT 'plaintext_pins' AS chk, COUNT(*) AS cnt
FROM player_auth WHERE LENGTH(pin_hash) < 50;

-- 4. 미션 상태 분포
SELECT status, COUNT(*) AS cnt FROM missions GROUP BY status ORDER BY cnt DESC;

-- 5. daily_points balance 정합성
SELECT player_id, date, balance, (earned - spent) AS expected
FROM daily_points WHERE balance != (earned - spent);

-- 6. ★ totalPoints 잔액 보정 검증
SELECT p.name, SUM(dp.balance) AS db_total
FROM players p JOIN daily_points dp ON dp.player_id = p.id
WHERE p.role = 'player'
GROUP BY p.id, p.name;

-- 7. Notification type 분포
SELECT type, COUNT(*) AS cnt FROM notifications GROUP BY type ORDER BY cnt DESC;
