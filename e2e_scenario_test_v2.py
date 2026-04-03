#!/usr/bin/env python3
from __future__ import annotations
"""
E2E 시나리오 테스트 v2 — mc-point-festival
Gemini 감사 Critical 3건 + 제언 3건 반영

실행: python3 e2e_scenario_test.py
"""

import requests
import json
import sys
import threading
from datetime import date, timedelta

# ===== 설정 =====

BASE = "http://localhost:8000"

# [제언-A 반영] 고정 테스트 날짜 — 자정 경계 이슈 방지
# 환경변수 TEST_DATE가 있으면 사용, 없으면 오늘
import os
TEST_DATE = os.environ.get("TEST_DATE", date.today().isoformat())
TEST_TOMORROW = (date.fromisoformat(TEST_DATE) + timedelta(days=1)).isoformat()
TEST_PREFIX = "e2e_test"  # 테스트 데이터 식별자

# [제언-B 반영] 플레이어 캐시
PLAYER_MAP: dict[str, dict] = {}    # { "유빈": {"id": 1, "name": "유빈", "role": "player"}, ... }
ADMIN_TOKEN: str = ""


# ===== 테스트 유틸리티 =====

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, name):
        self.passed += 1
        print(f"  ✅ {name}")

    def fail(self, name, detail=""):
        self.failed += 1
        self.errors.append(f"{name}: {detail}")
        print(f"  ❌ {name} — {detail}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"📊 결과: {self.passed}/{total} PASS, {self.failed}/{total} FAIL")
        if self.errors:
            print(f"\n❌ 실패 항목:")
            for e in self.errors:
                print(f"  - {e}")
        print(f"{'='*60}")
        return self.failed == 0


result = TestResult()


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login_player(name: str, pin: str = "1234") -> str:
    """플레이어 로그인 → JWT 토큰. PLAYER_MAP 캐시 사용."""
    player = PLAYER_MAP.get(name)
    if not player:
        raise Exception(f"플레이어 '{name}' 캐시에 없음")
    resp = requests.post(f"{BASE}/api/auth/login", json={
        "player_id": player["id"], "pin": pin
    })
    if resp.status_code != 200:
        raise Exception(f"로그인 실패({name}): {resp.text}")
    return resp.json()["access_token"]


def pid(name: str) -> int:
    """캐시에서 플레이어 ID 조회"""
    return PLAYER_MAP[name]["id"]


def find_mission(missions: list, mission_id: int) -> dict | None:
    """[Critical-3 반영] ID 기반 정확한 미션 타겟팅"""
    return next((m for m in missions if m["id"] == mission_id), None)


def find_deduction(deductions: list, deduction_id: int) -> dict | None:
    """[Critical-3 반영] ID 기반 정확한 차감 타겟팅"""
    return next((d for d in deductions if d["id"] == deduction_id), None)


def get_daily_point_for(token: str, player_id: int, target_date: str) -> dict | None:
    """[Critical-3 반영] daily_point 안전 조회"""
    resp = requests.get(f"{BASE}/api/daily-points",
        params={"player_id": player_id, "date": target_date},
        headers=auth(token))
    if resp.status_code != 200:
        return None
    try:
        dp = resp.json()
    except:
        return None
        
    if dp is None:
        return None
        
    if isinstance(dp, list):
        # player_id로 필터
        match = [d for d in dp if d.get("player_id") == player_id]
        return match[0] if match else (dp[0] if dp else None)
    return dp if isinstance(dp, dict) else None


# ===== [Critical-1 반영] Cleanup =====

def init_cache_and_cleanup():
    """테스트 시작 시: 플레이어 캐시 구축 + 이전 테스트 데이터 정리"""
    global PLAYER_MAP, ADMIN_TOKEN

    # 플레이어 목록 캐싱 (관리자 제외됨)
    players = requests.get(f"{BASE}/api/players").json()
    PLAYER_MAP = {p["name"]: p for p in players}
    
    # [FIX] 관리자 수동 추가 (id=3, name='관리자', role='admin')
    PLAYER_MAP["관리자"] = {"id": 3, "name": "관리자", "role": "admin"}
    print(f"  캐시: {list(PLAYER_MAP.keys())}")

    # 관리자 토큰
    admin = PLAYER_MAP["관리자"]
    resp = requests.post(f"{BASE}/api/auth/login", json={
        "player_id": admin["id"], "pin": "0000"
    })
    ADMIN_TOKEN = resp.json()["access_token"]

    # 이전 테스트 데이터 정리
    cleanup_all_test_data()


def cleanup_all_test_data():
    """모든 e2e_test 프리픽스 데이터 삭제"""
    cleaned = 0

    # 미션 정리
    for name, player in PLAYER_MAP.items():
        for d in [TEST_DATE, TEST_TOMORROW]:
            resp = requests.get(f"{BASE}/api/missions",
                params={"player_id": player["id"], "date": d},
                headers=auth(ADMIN_TOKEN))
            if resp.status_code == 200:
                for m in resp.json():
                    if TEST_PREFIX in m.get("text", ""):
                        requests.delete(f"{BASE}/api/missions/{m['id']}",
                            headers=auth(ADMIN_TOKEN))
                        cleaned += 1

    # 차감 정리
    for name, player in PLAYER_MAP.items():
        resp = requests.get(f"{BASE}/api/deductions",
            params={"player_id": player["id"], "date": TEST_DATE},
            headers=auth(ADMIN_TOKEN))
        if resp.status_code == 200:
            for d in resp.json():
                if TEST_PREFIX in d.get("reason", ""):
                    requests.delete(f"{BASE}/api/deductions/{d['id']}",
                        headers=auth(ADMIN_TOKEN))
                    cleaned += 1

    if cleaned > 0:
        print(f"  🧹 이전 테스트 데이터 {cleaned}건 정리 완료")


def cleanup_scenario(label: str):
    """개별 시나리오 전 해당 라벨 데이터만 정리"""
    for name, player in PLAYER_MAP.items():
        resp = requests.get(f"{BASE}/api/missions",
            params={"player_id": player["id"], "date": TEST_DATE},
            headers=auth(ADMIN_TOKEN))
        if resp.status_code == 200:
            for m in resp.json():
                if f"{TEST_PREFIX}_{label}" in m.get("text", ""):
                    requests.delete(f"{BASE}/api/missions/{m['id']}",
                        headers=auth(ADMIN_TOKEN))


# ===== 시나리오 그룹 A: 미션 할당 → 승인 사이클 =====

def scenario_a_mission_cycle(admin_name: str, child_name: str, label: str):
    """관리자 → 아이 미션 할당 → 승인 전체 사이클"""
    print(f"\n📋 시나리오 {label}: {admin_name} → {child_name}")

    cleanup_scenario(label)

    child_id = pid(child_name)
    mission_text = f"{TEST_PREFIX}_{label}_방청소"
    mission_point = 5

    # 1. 관리자 미션 할당
    resp = requests.post(f"{BASE}/api/missions", json={
        "player_id": child_id, "date": TEST_DATE,
        "text": mission_text, "point": mission_point,
    }, headers=auth(ADMIN_TOKEN))

    if resp.status_code not in (200, 201):
        result.fail(f"{label}-1: 미션 할당", resp.text)
        return
    mission_id = resp.json()["id"]
    result.ok(f"{label}-1: 미션 할당 (id={mission_id})")

    # 2. 아이 접속 → 미션 노출
    child_token = login_player(child_name)
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": child_id, "date": TEST_DATE},
        headers=auth(child_token))
    m = find_mission(resp.json(), mission_id)
    if m and m["status"] == "active":
        result.ok(f"{label}-2: 미션 노출 확인")
    else:
        result.fail(f"{label}-2: 미션 미노출", f"found={m}")
        return

    # 3. 승인 요청
    resp = requests.patch(f"{BASE}/api/missions/{mission_id}",
        json={"status": "pending_approval"}, headers=auth(child_token))
    if resp.status_code == 200 and resp.json()["status"] == "pending_approval":
        result.ok(f"{label}-3: 승인 요청")
    else:
        result.fail(f"{label}-3: 승인 요청 실패", resp.text)
        return

    # 4. 관리자 확인
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": child_id, "date": TEST_DATE},
        headers=auth(ADMIN_TOKEN))
    m = find_mission(resp.json(), mission_id)
    if m and m["status"] == "pending_approval":
        result.ok(f"{label}-4: 관리자 승인 대기 확인")
    else:
        result.fail(f"{label}-4: 관리자 확인 실패")
        return

    # 5. 관리자 승인
    resp = requests.patch(f"{BASE}/api/missions/{mission_id}",
        json={"status": "completed"}, headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200 and resp.json()["status"] == "completed":
        result.ok(f"{label}-5: 관리자 승인")
    else:
        result.fail(f"{label}-5: 승인 실패", resp.text)
        return

    # 6. 아이 승인 확인
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": child_id, "date": TEST_DATE},
        headers=auth(child_token))
    m = find_mission(resp.json(), mission_id)
    if m and m["status"] == "completed":
        result.ok(f"{label}-6: 아이 승인 확인")
    else:
        result.fail(f"{label}-6: 아이 확인 실패")
        return

    # 7. 포인트 반영
    dp = get_daily_point_for(ADMIN_TOKEN, child_id, TEST_DATE)
    if dp and dp.get("earned", 0) >= mission_point:
        result.ok(f"{label}-7: 포인트 반영 (earned={dp['earned']})")
    else:
        result.fail(f"{label}-7: 포인트 미반영", f"dp={dp}")


def scenario_a_all(admin_name: str, label: str):
    """관리자 → 모두에게 미션 할당"""
    print(f"\n📋 시나리오 {label}: {admin_name} → 모두")

    cleanup_scenario(label)
    children = [p for p in PLAYER_MAP.values() if p["role"] == "player"]
    mission_text = f"{TEST_PREFIX}_{label}_공통미션"

    # 각 아이에게 미션 생성
    mission_ids = {}
    for child in children:
        resp = requests.post(f"{BASE}/api/missions", json={
            "player_id": child["id"], "date": TEST_DATE,
            "text": mission_text, "point": 5,
        }, headers=auth(ADMIN_TOKEN))
        if resp.status_code in (200, 201):
            mission_ids[child["name"]] = resp.json()["id"]
        else:
            result.fail(f"{label}-create-{child['name']}", resp.text)
            return
    result.ok(f"{label}-1: 모두({len(children)}명)에게 할당")

    for child in children:
        cn = child["name"]
        mid = mission_ids[cn]
        ct = login_player(cn)

        # 노출 확인
        resp = requests.get(f"{BASE}/api/missions",
            params={"player_id": child["id"], "date": TEST_DATE}, headers=auth(ct))
        if not find_mission(resp.json(), mid):
            result.fail(f"{label}-2-{cn}: 미노출")
            continue
        result.ok(f"{label}-2-{cn}: 노출 확인")

        # 승인 요청 → 관리자 승인
        requests.patch(f"{BASE}/api/missions/{mid}",
            json={"status": "pending_approval"}, headers=auth(ct))
        requests.patch(f"{BASE}/api/missions/{mid}",
            json={"status": "completed"}, headers=auth(ADMIN_TOKEN))

        # 확인
        resp = requests.get(f"{BASE}/api/missions",
            params={"player_id": child["id"], "date": TEST_DATE}, headers=auth(ct))
        m = find_mission(resp.json(), mid)
        if m and m["status"] == "completed":
            result.ok(f"{label}-3-{cn}: 완료 확인")
        else:
            result.fail(f"{label}-3-{cn}: 미확인")

    # 포인트
    for child in children:
        dp = get_daily_point_for(ADMIN_TOKEN, child["id"], TEST_DATE)
        if dp:
            result.ok(f"{label}-4-{child['name']}: 포인트 확인")
        else:
            result.fail(f"{label}-4-{child['name']}: 포인트 조회 실패")


# ===== 시나리오 그룹 B: 미션 제안 =====

def scenario_b1_propose_approve(child_name: str):
    """미션 제안 → 승인"""
    print(f"\n📋 시나리오 B1: {child_name} 제안 → 승인")

    ct = login_player(child_name)
    cid = pid(child_name)

    resp = requests.post(f"{BASE}/api/missions/propose", json={
        "player_id": cid, "date": TEST_DATE,
        "text": f"{TEST_PREFIX}_B1_독서", "point": 5,
        "proposed_by": child_name, "proposal_reason": "책 읽고 싶어요",
    }, headers=auth(ct))
    if resp.status_code not in (200, 201):
        result.fail("B1-1: 제안 실패", resp.text)
        return
    prop_id = resp.json()["id"]
    result.ok("B1-1: 제안 완료")

    # 관리자 확인
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ADMIN_TOKEN))
    m = find_mission(resp.json(), prop_id)
    if m and m["status"] == "proposed":
        result.ok("B1-2: 관리자 확인")
    else:
        result.fail("B1-2: 미확인")
        return

    # 승인
    resp = requests.patch(f"{BASE}/api/missions/{prop_id}",
        json={"status": "active"}, headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200 and resp.json()["status"] == "active":
        result.ok("B1-3: 승인 (proposed → active)")
    else:
        result.fail("B1-3: 승인 실패", resp.text)
        return

    # 아이 확인
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ct))
    m = find_mission(resp.json(), prop_id)
    if m and m["status"] == "active":
        result.ok("B1-4: 아이 할당 확인")
    else:
        result.fail("B1-4: 미확인")


def scenario_b2_propose_reject(child_name: str):
    """미션 제안 → 반려 + 사유"""
    print(f"\n📋 시나리오 B2: {child_name} 제안 → 반려")

    ct = login_player(child_name)
    cid = pid(child_name)

    resp = requests.post(f"{BASE}/api/missions/propose", json={
        "player_id": cid, "date": TEST_DATE,
        "text": f"{TEST_PREFIX}_B2_게임", "point": 5,
        "proposed_by": child_name, "proposal_reason": "게임도 미션?",
    }, headers=auth(ct))
    if resp.status_code not in (200, 201):
        result.fail("B2-1: 제안 실패", resp.text)
        return
    prop_id = resp.json()["id"]
    result.ok("B2-1: 제안 완료")

    # 관리자 확인
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ADMIN_TOKEN))
    if find_mission(resp.json(), prop_id):
        result.ok("B2-2: 관리자 확인")
    else:
        result.fail("B2-2: 미확인")
        return

    # 반려 + 사유
    reason = "게임은 미션으로 적절하지 않아요"
    resp = requests.patch(f"{BASE}/api/missions/{prop_id}",
        json={"status": "rejected", "rejection_reason": reason},
        headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200 and resp.json()["status"] == "rejected":
        result.ok("B2-3: 반려 완료")
    else:
        result.fail("B2-3: 반려 실패", resp.text)
        return

    # 아이 반려 조회
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ct))
    m = find_mission(resp.json(), prop_id)
    if m and m["status"] == "rejected":
        result.ok("B2-4: 반려 내역 조회")
    else:
        result.fail("B2-4: 미확인")
        return

    # 반려 사유
    if m.get("rejection_reason") == reason:
        result.ok(f"B2-5: 반려 사유 확인")
    else:
        result.fail("B2-5: 사유 불일치", f"got={m.get('rejection_reason')}")


# ===== 시나리오 그룹 C: 포인트 차감 =====

def scenario_c_deduction(child_name: str):
    """포인트 차감 → 내역 확인 → 아이 확인"""
    print(f"\n📋 시나리오 C: {child_name} 포인트 차감")

    ct = login_player(child_name)
    cid = pid(child_name)

    resp = requests.post(f"{BASE}/api/deductions", json={
        "player_id": cid, "date": TEST_DATE,
        "reason": f"{TEST_PREFIX}_C_게임초과", "amount": 5,
    }, headers=auth(ADMIN_TOKEN))
    if resp.status_code not in (200, 201):
        result.fail("C-1: 차감 실패", resp.text)
        return
    did = resp.json()["id"]
    result.ok("C-1: 차감 완료")

    # 내역 확인
    resp = requests.get(f"{BASE}/api/deductions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ADMIN_TOKEN))
    d = find_deduction(resp.json(), did)
    if d and f"{TEST_PREFIX}_C" in d.get("reason", ""):
        result.ok("C-2: 차감 내역 확인")
    else:
        result.fail("C-2: 내역 미확인")
        return

    # 아이 확인
    resp = requests.get(f"{BASE}/api/deductions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ct))
    d = find_deduction(resp.json(), did)
    if d:
        result.ok("C-3: 아이 대시보드 차감 확인")
    else:
        result.fail("C-3: 아이 미확인")

    # 잔액 확인
    dp = get_daily_point_for(ADMIN_TOKEN, cid, TEST_DATE)
    if dp and dp.get("spent", 0) >= 5:
        result.ok(f"C-4: 잔액 변동 확인 (spent={dp['spent']})")
    else:
        result.fail("C-4: 잔액 미반영", f"dp={dp}")


# ===== 시나리오 그룹 D: 추가 시나리오 =====

def scenario_d1_mission_edit():
    """미션 편집"""
    print(f"\n📋 시나리오 D1: 미션 편집")

    cid = pid("유빈")
    resp = requests.post(f"{BASE}/api/missions", json={
        "player_id": cid, "date": TEST_DATE,
        "text": f"{TEST_PREFIX}_D1_편집전", "point": 10,
    }, headers=auth(ADMIN_TOKEN))
    mid = resp.json()["id"]

    resp = requests.patch(f"{BASE}/api/missions/{mid}",
        json={"text": f"{TEST_PREFIX}_D1_편집후", "point": 20},
        headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200:
        m = resp.json()
        if f"편집후" in m["text"] and m["point"] == 20:
            result.ok("D1: 미션 편집 성공")
        else:
            result.fail("D1: 값 불일치", f"text={m['text']}, point={m['point']}")
    else:
        result.fail("D1: 편집 실패", resp.text)


def scenario_d2_complete_cancel():
    """완료 취소 (BE 패치 후 PASS 기대)"""
    print(f"\n📋 시나리오 D2: 완료 취소")

    cid = pid("유빈")
    ct = login_player("유빈")

    resp = requests.post(f"{BASE}/api/missions", json={
        "player_id": cid, "date": TEST_DATE,
        "text": f"{TEST_PREFIX}_D2_완료취소", "point": 5,
    }, headers=auth(ADMIN_TOKEN))
    mid = resp.json()["id"]

    # active → pending_approval → completed
    requests.patch(f"{BASE}/api/missions/{mid}",
        json={"status": "pending_approval"}, headers=auth(ct))
    requests.patch(f"{BASE}/api/missions/{mid}",
        json={"status": "completed"}, headers=auth(ADMIN_TOKEN))

    # completed → active (완료 취소)
    resp = requests.patch(f"{BASE}/api/missions/{mid}",
        json={"status": "active"}, headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200 and resp.json()["status"] == "active":
        result.ok("D2: 완료 취소 성공 (completed → active)")
    else:
        result.fail("D2: 완료 취소 실패 — BE VALID_TRANSITIONS 패치 확인", resp.text)


def scenario_d3_deduction_edit_delete():
    """차감 편집 + 삭제"""
    print(f"\n📋 시나리오 D3: 차감 편집/삭제")

    cid = pid("유현")
    resp = requests.post(f"{BASE}/api/deductions", json={
        "player_id": cid, "date": TEST_DATE,
        "reason": f"{TEST_PREFIX}_D3_편집전", "amount": 10,
    }, headers=auth(ADMIN_TOKEN))
    did = resp.json()["id"]

    # 편집
    resp = requests.patch(f"{BASE}/api/deductions/{did}",
        json={"reason": f"{TEST_PREFIX}_D3_편집후", "amount": 15},
        headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200:
        d = resp.json()
        if "편집후" in d["reason"] and d["amount"] == 15:
            result.ok("D3-1: 차감 편집 성공")
        else:
            result.fail("D3-1: 값 불일치")
    else:
        result.fail("D3-1: 편집 실패", resp.text)

    # 삭제
    resp = requests.delete(f"{BASE}/api/deductions/{did}", headers=auth(ADMIN_TOKEN))
    if resp.status_code == 204:
        result.ok("D3-2: 차감 삭제 성공")
    else:
        result.fail("D3-2: 삭제 실패", resp.text)


def scenario_d4_batch_copy():
    """미션 일괄 복제"""
    print(f"\n📋 시나리오 D4: 일괄 복제")

    cid = pid("유빈")
    for t in [f"{TEST_PREFIX}_D4_원본A", f"{TEST_PREFIX}_D4_원본B"]:
        requests.post(f"{BASE}/api/missions", json={
            "player_id": cid, "date": TEST_DATE, "text": t, "point": 10,
        }, headers=auth(ADMIN_TOKEN))

    resp = requests.post(f"{BASE}/api/missions/batch-copy", params={
        "player_id": cid, "from_date": TEST_DATE, "to_date": TEST_TOMORROW,
    }, headers=auth(ADMIN_TOKEN))

    if resp.status_code in (200, 201):
        copied = resp.json()
        cnt = len(copied) if isinstance(copied, list) else 0
        if cnt >= 2:
            result.ok(f"D4: 복제 성공 ({cnt}개)")
        else:
            result.fail("D4: 복제 부족", f"count={cnt}")
    else:
        result.fail("D4: 복제 실패", resp.text)


def scenario_d5_notification():
    """알림 조회 + 읽음"""
    print(f"\n📋 시나리오 D5: 알림")

    resp = requests.get(f"{BASE}/api/notifications", headers=auth(ADMIN_TOKEN))
    if resp.status_code != 200:
        result.fail("D5-1: 조회 실패", resp.text)
        return
    notifs = resp.json()
    result.ok(f"D5-1: 조회 성공 ({len(notifs)}건)")

    unread = [n for n in notifs if not n["is_read"]]
    if unread:
        resp = requests.patch(f"{BASE}/api/notifications/{unread[0]['id']}/read",
            headers=auth(ADMIN_TOKEN))
        if resp.status_code in (200, 204):
            result.ok("D5-2: 읽음 처리 성공")
        else:
            result.fail("D5-2: 읽음 실패", resp.text)
    else:
        result.ok("D5-2: 안 읽음 없음 (SKIP)")


def scenario_d6_config():
    """설정 CRUD"""
    print(f"\n📋 시나리오 D6: 설정")

    resp = requests.get(f"{BASE}/api/configs/level.thresholds", headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200:
        result.ok("D6-1: 조회 성공")
    else:
        result.fail("D6-1: 조회 실패", resp.text)
        return

    original = resp.json().get("value", '{"1":0,"2":50,"3":150,"4":300,"5":500}')

    resp = requests.put(f"{BASE}/api/configs/level.thresholds",
        json={"value": '{"1":0,"2":60,"3":180,"4":350,"5":600}'},
        headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200:
        result.ok("D6-2: 수정 성공")
    else:
        result.fail("D6-2: 수정 실패", resp.text)

    # 원복
    requests.put(f"{BASE}/api/configs/level.thresholds",
        json={"value": original}, headers=auth(ADMIN_TOKEN))


def scenario_d7_cheer():
    """응원 메시지"""
    print(f"\n📋 시나리오 D7: 응원 메시지")

    resp = requests.post(f"{BASE}/api/cheers", json={
        "date": TEST_DATE, "sender": "dad",
        "message": f"{TEST_PREFIX}_D7_화이팅",
    }, headers=auth(ADMIN_TOKEN))
    if resp.status_code in (200, 201):
        result.ok("D7-1: 등록 성공")
    else:
        result.fail("D7-1: 등록 실패", resp.text)
        return

    ct = login_player("유빈")
    resp = requests.get(f"{BASE}/api/cheers",
        params={"date": TEST_DATE}, headers=auth(ct))
    if resp.status_code == 200:
        found = any(TEST_PREFIX in c.get("message", "") for c in resp.json())
        if found:
            result.ok("D7-2: 아이 조회 성공")
        else:
            result.fail("D7-2: 미노출")
    else:
        result.fail("D7-2: 조회 실패", resp.text)


def scenario_d8_feedback():
    """피드백"""
    print(f"\n📋 시나리오 D8: 피드백")

    ct = login_player("유빈")
    cid = pid("유빈")

    resp = requests.post(f"{BASE}/api/feedbacks", json={
        "player_id": cid, "date": TEST_DATE,
        "msg": f"{TEST_PREFIX}_D8_재밌었어요",
    }, headers=auth(ct))
    if resp.status_code in (200, 201):
        result.ok("D8-1: 전송 성공")
    else:
        result.fail("D8-1: 전송 실패", resp.text)
        return

    resp = requests.get(f"{BASE}/api/feedbacks",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ADMIN_TOKEN))
    if resp.status_code == 200:
        found = any(TEST_PREFIX in f.get("msg", "") for f in resp.json())
        if found:
            result.ok("D8-2: 관리자 조회 성공")
        else:
            result.fail("D8-2: 미노출")
    else:
        result.fail("D8-2: 조회 실패", resp.text)


def scenario_d9_invalid_transitions():
    """잘못된 상태 전이 차단"""
    print(f"\n📋 시나리오 D9: 전이 차단")

    cid = pid("유빈")
    resp = requests.post(f"{BASE}/api/missions", json={
        "player_id": cid, "date": TEST_DATE,
        "text": f"{TEST_PREFIX}_D9_전이차단", "point": 5,
    }, headers=auth(ADMIN_TOKEN))
    mid = resp.json()["id"]

    # active → completed (직접 — 차단)
    resp = requests.patch(f"{BASE}/api/missions/{mid}",
        json={"status": "completed"}, headers=auth(ADMIN_TOKEN))
    if resp.status_code == 400:
        result.ok("D9-1: active → completed 차단")
    else:
        result.fail("D9-1: 허용됨", f"status={resp.status_code}")

    # active → rejected (차단)
    resp = requests.patch(f"{BASE}/api/missions/{mid}",
        json={"status": "rejected"}, headers=auth(ADMIN_TOKEN))
    if resp.status_code == 400:
        result.ok("D9-2: active → rejected 차단")
    else:
        result.fail("D9-2: 허용됨", f"status={resp.status_code}")


def scenario_d10_concurrent_approve():
    """[제언-C 반영] 동시성: 아빠+엄마 동시 미션 할당"""
    print(f"\n📋 시나리오 D10: 동시 미션 할당")

    cid = pid("유빈")
    results_map = {"dad": None, "mom": None}

    def create_mission(sender, idx):
        resp = requests.post(f"{BASE}/api/missions", json={
            "player_id": cid, "date": TEST_DATE,
            "text": f"{TEST_PREFIX}_D10_{sender}", "point": 5,
        }, headers=auth(ADMIN_TOKEN))
        results_map[sender] = resp.status_code

    t1 = threading.Thread(target=create_mission, args=("dad", 0))
    t2 = threading.Thread(target=create_mission, args=("mom", 1))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    if all(s in (200, 201) for s in results_map.values()):
        result.ok("D10-1: 동시 생성 성공")
    else:
        result.fail("D10-1: 동시 생성 실패", f"results={results_map}")

    # 두 미션 모두 존재 확인
    resp = requests.get(f"{BASE}/api/missions",
        params={"player_id": cid, "date": TEST_DATE}, headers=auth(ADMIN_TOKEN))
    missions = resp.json()
    dad_found = any(f"{TEST_PREFIX}_D10_dad" in m.get("text", "") for m in missions)
    mom_found = any(f"{TEST_PREFIX}_D10_mom" in m.get("text", "") for m in missions)
    if dad_found and mom_found:
        result.ok("D10-2: 두 미션 모두 존재")
    else:
        result.fail("D10-2: 누락", f"dad={dad_found}, mom={mom_found}")


# ===== 메인 =====

def main():
    print("=" * 60)
    print("🎮 마인크래프트 포인트 잔치 — E2E 시나리오 테스트 v2")
    print(f"📅 테스트 날짜: {TEST_DATE} (고정)")
    print("=" * 60)

    # 헬스 체크
    try:
        resp = requests.get(f"{BASE}/api/health", timeout=5)
        if resp.status_code != 200:
            print("❌ 서버 응답 없음")
            sys.exit(1)
        print("✅ 서버 정상")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        sys.exit(1)

    # 초기화 + cleanup
    print("\n🔧 초기화...")
    init_cache_and_cleanup()

    # 그룹 A: 미션 할당 사이클
    scenario_a_mission_cycle("관리자", "유빈", "A1")
    scenario_a_mission_cycle("관리자", "유현", "A2")
    scenario_a_all("관리자", "A3")
    scenario_a_mission_cycle("관리자", "유빈", "A4")
    scenario_a_mission_cycle("관리자", "유현", "A5")
    scenario_a_all("관리자", "A6")

    # 그룹 B: 미션 제안
    scenario_b1_propose_approve("유빈")
    scenario_b2_propose_reject("유빈")

    # 그룹 C: 포인트 차감
    scenario_c_deduction("유빈")

    # 그룹 D: 추가 시나리오
    scenario_d1_mission_edit()
    scenario_d2_complete_cancel()
    scenario_d3_deduction_edit_delete()
    scenario_d4_batch_copy()
    scenario_d5_notification()
    scenario_d6_config()
    scenario_d7_cheer()
    scenario_d8_feedback()
    scenario_d9_invalid_transitions()
    scenario_d10_concurrent_approve()

    # 정리
    print("\n🧹 테스트 데이터 정리...")
    cleanup_all_test_data()

    # 결과
    success = result.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
