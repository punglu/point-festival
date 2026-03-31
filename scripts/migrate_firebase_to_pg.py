#!/usr/bin/env python3
"""
Firebase RTDB → PostgreSQL 데이터 마이그레이션

실행:
  python scripts/migrate_firebase_to_pg.py

필수:
  mark-point-festivals-default-rtdb-export.json (프로젝트 루트)

환경변수 (DB 접속 — 기본값: .env 기준):
  DB_HOST  (기본: localhost)
  DB_PORT  (기본: 5432)
  DB_NAME  (기본: mc_festival)
  DB_USER  (기본: mc_admin)
  DB_PASS  (기본: mc_secret_2026)

  예시:
    DB_HOST=localhost DB_PORT=5432 DB_NAME=mc_festival \\
    DB_USER=mc_admin DB_PASS=mc_secret_2026 \\
    python scripts/migrate_firebase_to_pg.py

기타 환경변수:
  FB_JSON_PATH  (기본: <프로젝트 루트>/mark-point-festivals-default-rtdb-export.json)

옵션:
  --dry-run         실제 INSERT 없이 로그만
  --json-file PATH  Firebase export JSON 경로 직접 지정
"""

import os
import sys
import json
import re
import time
import argparse
from datetime import datetime, timezone

import bcrypt
import psycopg2


# ─── 설정 ─────────────────────────────────────────────
_DB_HOST = os.getenv("DB_HOST", "localhost")
_DB_PORT = os.getenv("DB_PORT", "5432")
_DB_NAME = os.getenv("DB_NAME", "mc_festival")
_DB_USER = os.getenv("DB_USER", "mc_admin")
_DB_PASS = os.getenv("DB_PASS", "mc_secret_2026")
DEFAULT_DB_URL = f"postgresql://{_DB_USER}:{_DB_PASS}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}"
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
DEFAULT_FB_JSON = os.path.join(
    _PROJECT_ROOT, "mark-point-festivals-default-rtdb-export.json"
)


# ─── 유틸리티 ─────────────────────────────────────────
def ms_to_timestamptz(ms):
    """Unix ms → PostgreSQL TIMESTAMPTZ 문자열"""
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def log_step(step_num, name, count, extra=""):
    """Step 진행 로그"""
    mark = "✅" if count >= 0 else "⚠️"
    print(f"  Step {step_num:2d}: {name:<25s} {count:>5d} rows  {mark} {extra}")


# ─── Firebase JSON 로드 ───────────────────────────────
def load_firebase_json(json_path):
    if not os.path.exists(json_path):
        print(f"❌ Firebase JSON 파일을 찾을 수 없습니다: {json_path}")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  Firebase JSON 로드 완료: {json_path}")
    return data


# ─── PostgreSQL 연결 ──────────────────────────────────
def connect_pg(db_url):
    conn = psycopg2.connect(db_url)
    conn.autocommit = False  # 수동 트랜잭션
    return conn


# ─── Step 0: TRUNCATE ─────────────────────────────────
def truncate_all(cur):
    """모든 테이블 데이터 초기화"""
    cur.execute("""
        TRUNCATE login_logs, notifications, daily_points, deductions,
                 feedback_replies, feedbacks, cheer_messages, missions,
                 player_auth, admin_auth, app_configs, players
        CASCADE;
    """)
    # SERIAL 시퀀스 리셋
    for tbl in ['players', 'player_auth', 'admin_auth', 'missions',
                'cheer_messages', 'feedbacks', 'feedback_replies',
                'deductions', 'daily_points', 'notifications',
                'app_configs', 'login_logs']:
        cur.execute(f"ALTER SEQUENCE {tbl}_id_seq RESTART WITH 1;")
    print("  Step  0: TRUNCATE ALL              ✅")


# ─── Step 1: mc_config → app_configs ──────────────────
def migrate_config(cur, fb_data, dry_run):
    data = fb_data.get("mc_config") or {}
    count = 0
    photos = data.get("photos", {})
    for key in ["dad", "mom"]:
        val = photos.get(key, "")
        if not dry_run:
            cur.execute("""
                INSERT INTO app_configs (key, value) VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
            """, (f"photos.{key}", val))
        count += 1
    log_step(1, "app_configs", count)
    return count


# ─── Step 2: mc_players → players ─────────────────────
def migrate_players(cur, fb_data, dry_run):
    data = fb_data.get("mc_players") or {}
    player_id_map = {}        # Firebase Push ID → PostgreSQL id
    total_points_map = {}     # Firebase Push ID → totalPoints (검증용)
    count = 0

    for fb_id, p in data.items():
        total_points_map[fb_id] = p.get("totalPoints", 0)
        if not dry_run:
            cur.execute("""
                INSERT INTO players (name, role, photo, status_msg, last_login)
                VALUES (%s, 'player', %s, %s, %s) RETURNING id;
            """, (
                p.get("name", "Unknown"),
                p.get("photo"),
                p.get("statusMsg"),
                p.get("lastLogin"),
            ))
            pg_id = cur.fetchone()[0]
            player_id_map[fb_id] = pg_id
        else:
            player_id_map[fb_id] = count + 1  # dry-run용 가짜 ID
        count += 1

    log_step(2, "players", count)
    return player_id_map, total_points_map, count


# ─── Step 3: mc_player_auth → player_auth (bcrypt) ────
def migrate_player_auth(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_player_auth") or {}
    count = 0

    for fb_id, auth in data.items():
        pg_pid = player_id_map.get(fb_id)
        if pg_pid is None:
            print(f"    ⚠️ player_auth: 알 수 없는 player ID '{fb_id}' — 스킵")
            continue

        pin_raw = str(auth.get("pin", ""))
        if not pin_raw:
            pin_raw = "0000"
            print(f"    ⚠️ player_auth: 빈 PIN → 기본 '0000' 적용 (player_id={pg_pid})")

        # bcrypt 해시 (Gemini 권고: 소요 시간 로깅)
        t0 = time.time()
        pin_hash = bcrypt.hashpw(pin_raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        elapsed = time.time() - t0
        print(f"    🔐 PIN 해시 완료: player_id={pg_pid}, {elapsed:.2f}s")

        if not dry_run:
            cur.execute("""
                INSERT INTO player_auth (player_id, pin_hash, login_attempts, lock_until)
                VALUES (%s, %s, 0, NULL);
            """, (pg_pid, pin_hash))
        count += 1

    log_step(3, "player_auth", count, "(bcrypt)")
    return count


# ─── Step 4: mc_mission_data → missions ───────────────
def migrate_missions(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_mission_data") or {}
    count = 0

    for fb_pid, dates in data.items():
        pg_pid = player_id_map.get(fb_pid)
        if pg_pid is None:
            print(f"    ⚠️ missions: 알 수 없는 player ID '{fb_pid}' — 스킵")
            continue
        if not isinstance(dates, dict):
            continue

        for date_str, date_data in dates.items():
            if not isinstance(date_data, dict):
                continue
            missions = date_data.get("missions", {})
            if not isinstance(missions, dict):
                continue

            for mid, m in missions.items():
                if not isinstance(m, dict):
                    continue
                created_at = ms_to_timestamptz(m.get("createdAt"))
                if not dry_run:
                    cur.execute("""
                        INSERT INTO missions
                          (player_id, date, text, point, status, sender, msg,
                           proposed_by, proposal_reason, rejection_reason, sort_order, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                COALESCE(%s, NOW()));
                    """, (
                        pg_pid,
                        date_str,
                        m.get("text", ""),
                        m.get("point", 0),
                        m.get("status", "active"),
                        m.get("sender"),
                        m.get("msg"),
                        m.get("proposedBy"),
                        m.get("proposalReason"),
                        m.get("rejectionReason"),
                        m.get("order", 0),
                        created_at,
                    ))
                count += 1

    log_step(4, "missions", count)
    return count


# ─── Step 5: mc_cheer_msgs → cheer_messages ───────────
def migrate_cheers(cur, fb_data, dry_run):
    data = fb_data.get("mc_cheer_msgs") or {}
    count = 0

    for date_str, senders in data.items():
        if not isinstance(senders, dict):
            continue
        for sender in ["dad", "mom"]:
            msg = senders.get(sender, "")
            if not msg:
                continue
            if not dry_run:
                cur.execute("""
                    INSERT INTO cheer_messages (date, sender, message)
                    VALUES (%s, %s, %s);
                """, (date_str, sender, msg))
            count += 1

    log_step(5, "cheer_messages", count)
    return count


# ─── Step 6: mc_feedbacks → feedbacks + feedback_replies
def migrate_feedbacks(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_feedbacks") or {}
    fb_count = 0
    reply_count = 0

    for fb_pid, dates in data.items():
        pg_pid = player_id_map.get(fb_pid)
        if pg_pid is None:
            continue
        if not isinstance(dates, dict):
            continue

        for date_str, entries in dates.items():
            if not isinstance(entries, dict):
                continue

            for fid, fb in entries.items():
                if not isinstance(fb, dict):
                    continue
                created_at = ms_to_timestamptz(fb.get("createdAt"))

                if not dry_run:
                    cur.execute("""
                        INSERT INTO feedbacks (player_id, date, msg, created_at)
                        VALUES (%s, %s, %s, COALESCE(%s, NOW()))
                        RETURNING id;
                    """, (pg_pid, date_str, fb.get("msg", ""), created_at))
                    pg_fb_id = cur.fetchone()[0]
                else:
                    pg_fb_id = fb_count + 1
                fb_count += 1

                # replies
                replies = fb.get("replies", {})
                if isinstance(replies, dict):
                    for rid, r in replies.items():
                        if not isinstance(r, dict):
                            continue
                        r_created = ms_to_timestamptz(r.get("createdAt"))
                        if not dry_run:
                            cur.execute("""
                                INSERT INTO feedback_replies
                                  (feedback_id, sender, text, created_at)
                                VALUES (%s, %s, %s, COALESCE(%s, NOW()));
                            """, (pg_fb_id, r.get("sender", ""), r.get("text", ""), r_created))
                        reply_count += 1

    log_step(6, "feedbacks", fb_count)
    log_step(6, "  feedback_replies", reply_count)
    return fb_count, reply_count


# ─── Step 7: mc_deductions → deductions (⚠️ 2중 flat) ─
def migrate_deductions(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_deductions") or {}
    count = 0
    skipped = 0

    for fb_pid, entries in data.items():
        pg_pid = player_id_map.get(fb_pid)
        if pg_pid is None:
            continue
        if not isinstance(entries, dict):
            continue

        for did, d in entries.items():
            # ⚠️ 오염 데이터 방어: dict가 아닌 항목(list, str) 스킵
            if not isinstance(d, dict):
                skipped += 1
                print(f"    ⚠️ deductions: 오염 데이터 스킵 (key='{did}', type={type(d).__name__})")
                continue

            created_at = ms_to_timestamptz(d.get("timestamp"))
            if not dry_run:
                cur.execute("""
                    INSERT INTO deductions (player_id, date, reason, amount, created_at)
                    VALUES (%s, %s, %s, %s, COALESCE(%s, NOW()));
                """, (
                    pg_pid,
                    d.get("date", "1970-01-01"),
                    d.get("reason", ""),
                    d.get("amount", 0),
                    created_at,
                ))
            count += 1

    extra = f"({skipped} skipped)" if skipped else ""
    log_step(7, "deductions", count, extra)
    return count


# ─── Step 8: mc_daily_points → daily_points ───────────
def migrate_daily_points(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_daily_points") or {}
    count = 0

    for fb_pid, dates in data.items():
        pg_pid = player_id_map.get(fb_pid)
        if pg_pid is None:
            continue
        if not isinstance(dates, dict):
            continue

        for date_str, dp in dates.items():
            if not isinstance(dp, dict):
                continue
            if not dry_run:
                cur.execute("""
                    INSERT INTO daily_points
                      (player_id, date, earned, spent, balance)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    pg_pid,
                    date_str,
                    dp.get("earned", 0),
                    dp.get("deducted", 0),    # ⚠️ Firebase "deducted" → PG "spent"
                    dp.get("balance", 0),
                ))
            count += 1

    log_step(8, "daily_points", count)
    return count


# ─── Step 9: mc_notifications → notifications ─────────
def migrate_notifications(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_notifications") or {}
    count = 0

    for nid, n in data.items():
        if not isinstance(n, dict):
            continue
        fb_pid = n.get("playerId", "")
        pg_pid = player_id_map.get(fb_pid)
        if pg_pid is None:
            print(f"    ⚠️ notifications: 알 수 없는 playerId '{fb_pid}' — 스킵")
            continue

        created_at = ms_to_timestamptz(n.get("createdAt"))
        if not dry_run:
            cur.execute("""
                INSERT INTO notifications
                  (type, player_id, title, body, is_read, created_at)
                VALUES (%s, %s, %s, NULL, %s, COALESCE(%s, NOW()));
            """, (
                n.get("type", ""),
                pg_pid,
                n.get("message", "(알림)"),  # ⚠️ Firebase "message" → PG "title" (NOT NULL)
                n.get("read", False),
                created_at,
            ))
        count += 1

    log_step(9, "notifications", count)
    return count


# ─── Step 10: mc_login_logs → login_logs ──────────────
def migrate_login_logs(cur, fb_data, player_id_map, dry_run):
    data = fb_data.get("mc_login_logs") or {}
    count = 0

    for fb_pid, entries in data.items():
        pg_pid = player_id_map.get(fb_pid)
        if pg_pid is None:
            continue
        if not isinstance(entries, dict):
            continue

        for lid, l in entries.items():
            if not isinstance(l, dict):
                continue
            created_at = ms_to_timestamptz(l.get("timestamp"))
            if not dry_run:
                cur.execute("""
                    INSERT INTO login_logs
                      (player_id, success, ip_address, date, created_at)
                    VALUES (%s, %s, NULL, %s, COALESCE(%s, NOW()));
                """, (
                    pg_pid,
                    l.get("success", False),
                    l.get("date", "1970-01-01"),
                    created_at,
                ))
            count += 1

    log_step(10, "login_logs", count)
    return count


# ─── Step 11: admin_auth Seed 재삽입 ──────────────────
def insert_admin_auth_seed(cur, dry_run):
    """Phase 5 admin 인증용 Seed (init.sql과 동일)"""
    if dry_run:
        log_step(11, "admin_auth Seed", 0, "(dry-run)")
        return 0

    init_sql_path = os.path.join(_PROJECT_ROOT, "database", "init.sql")
    if os.path.exists(init_sql_path):
        with open(init_sql_path, "r") as f:
            content = f.read()
        matches = re.findall(
            r"INSERT INTO admin_auth.*?;", content, re.DOTALL | re.IGNORECASE
        )
        count = 0
        for stmt in matches:
            cur.execute(stmt)
            count += cur.rowcount
        log_step(11, "admin_auth Seed", count)
        return count
    else:
        print("    ⚠️ init.sql 미발견 — admin_auth Seed 스킵")
        log_step(11, "admin_auth Seed", 0, "(init.sql 미발견)")
        return 0


# ─── Step 12: ★ totalPoints 잔액 보정 ─────────────────
def reconcile_total_points(cur, player_id_map, total_points_map, dry_run):
    """
    PM 핵심 요구사항:
    daily_points SUM(balance) != Firebase totalPoints 이면
    date='1970-01-01' 보정 레코드 삽입
    """
    if dry_run:
        log_step(12, "잔액 보정", 0, "(dry-run)")
        return

    print("  Step 12: 잔액 보정")
    for fb_id, pg_pid in player_id_map.items():
        fb_total = total_points_map.get(fb_id, 0)

        cur.execute("""
            SELECT COALESCE(SUM(balance), 0) FROM daily_points
            WHERE player_id = %s;
        """, (pg_pid,))
        db_total = cur.fetchone()[0]

        diff = fb_total - db_total
        name = fb_id[:20]  # 로그용

        if diff == 0:
            print(f"    {name}: FB={fb_total}, DB={db_total}  ✅ (차이 0)")
        else:
            print(f"    {name}: FB={fb_total}, DB={db_total}  → 보정 {diff:+d}")
            if diff > 0:
                earned = diff
                spent = 0
            else:
                earned = 0
                spent = abs(diff)
            balance = earned - spent  # balance = earned - spent 등식 보장
            cur.execute("""
                INSERT INTO daily_points (player_id, date, earned, spent, balance)
                VALUES (%s, '1970-01-01', %s, %s, %s)
                ON CONFLICT (player_id, date) DO UPDATE
                SET earned = EXCLUDED.earned,
                    spent = EXCLUDED.spent,
                    balance = EXCLUDED.balance;
            """, (pg_pid, earned, spent, balance))


# ─── Step 13: app_configs Seed 재삽입 ─────────────────
def insert_app_configs_seed(cur, dry_run):
    """Phase 3 level.thresholds 등 Seed 복원"""
    if dry_run:
        log_step(13, "app_configs Seed", 0, "(dry-run)")
        return 0

    seeds = [
        ("level.thresholds", '{"1":0,"2":50,"3":150,"4":300,"5":500}'),
    ]
    count = 0
    for key, value in seeds:
        cur.execute("""
            INSERT INTO app_configs (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
        """, (key, value))
        count += 1

    log_step(13, "app_configs Seed", count)
    return count


# ─── 메인 ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Firebase → PostgreSQL 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="INSERT 없이 로그만")
    parser.add_argument(
        "--json-file",
        default=os.environ.get("FB_JSON_PATH", DEFAULT_FB_JSON),
        help="Firebase RTDB export JSON 파일 경로",
    )
    args = parser.parse_args()

    db_url = DEFAULT_DB_URL  # DB_HOST/PORT/NAME/USER/PASS 환경변수로 제어

    print("╔══════════════════════════════════════════════════════╗")
    print("║  Firebase → PostgreSQL 마이그레이션                  ║")
    print(f"║  Mode: {'DRY-RUN' if args.dry_run else 'LIVE    '}                                   ║")
    print("╠══════════════════════════════════════════════════════╣")

    fb_data = load_firebase_json(args.json_file)
    conn = connect_pg(db_url)
    cur = conn.cursor()

    try:
        truncate_all(cur)

        migrate_config(cur, fb_data, args.dry_run)
        player_id_map, total_points_map, _ = migrate_players(cur, fb_data, args.dry_run)
        migrate_player_auth(cur, fb_data, player_id_map, args.dry_run)
        migrate_missions(cur, fb_data, player_id_map, args.dry_run)
        migrate_cheers(cur, fb_data, args.dry_run)
        migrate_feedbacks(cur, fb_data, player_id_map, args.dry_run)
        migrate_deductions(cur, fb_data, player_id_map, args.dry_run)
        migrate_daily_points(cur, fb_data, player_id_map, args.dry_run)
        migrate_notifications(cur, fb_data, player_id_map, args.dry_run)
        migrate_login_logs(cur, fb_data, player_id_map, args.dry_run)
        insert_admin_auth_seed(cur, args.dry_run)
        reconcile_total_points(cur, player_id_map, total_points_map, args.dry_run)
        insert_app_configs_seed(cur, args.dry_run)

        if not args.dry_run:
            conn.commit()
            print("╠══════════════════════════════════════════════════════╣")
            print("║  ✅ 커밋 완료                                        ║")
        else:
            conn.rollback()
            print("╠══════════════════════════════════════════════════════╣")
            print("║  🔍 DRY-RUN 완료 (롤백됨)                            ║")

        print("╚══════════════════════════════════════════════════════╝")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 마이그레이션 실패: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
