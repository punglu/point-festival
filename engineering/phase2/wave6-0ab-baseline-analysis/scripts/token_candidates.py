#!/usr/bin/env python3
import csv

OUT = "/tmp/mongle-wave6-0ab/6.0A/approved_token_candidates.csv"

# current implementation tokens (read directly from
# frontend/src/styles/global.css during Phase A/B code reading; recorded here
# for cross-reference only, not as authority over the design source)
CURRENT_TOKENS = {
    "#5835DF": "--color-brand-600", "#4726C7": "--color-brand-700", "#6B46F2": "--color-brand-500",
    "#8B6DF5": "--color-brand-400", "#D9CCFF": "--color-brand-200", "#EEE8FF": "--color-brand-100",
    "#F8F5FF": "--color-brand-50", "#12172F": "--color-ink-950", "#171D3A": "--color-ink-900",
    "#434A68": "--color-ink-700", "#757C98": "--color-ink-500", "#E8E6F2": "--color-line",
    "#F7F6FC": "--color-canvas", "#FFFFFF": "--color-surface", "#FBFAFF": "--color-surface-soft",
    "#2FBE78": "--color-success", "#F3A72B": "--color-warning", "#EF4665": "--color-danger",
    "#F1B83A": "--color-reward", "#6944EF": "--color-chat-own", "#F3F0FF": "--color-chat-other",
}

rows = []
def add(cat, raw, occ, screens, role, conflict, proposed, confidence, pm_gate, note=""):
    rows.append(dict(category=cat, raw_value=raw, occurrence_count=occ, source_files="standalone-src.html",
        screen_ids=screens, intended_semantic_role=role, classification=conflict, proposed_candidate_name=proposed,
        confidence=confidence, pm_gate_required=pm_gate, note=note))

# Colors (from _raw_colors.csv, top by frequency)
color_data = [
    ("#17103A", 188, "A1,A1-S1,A2,A3,A4,A5,EXTRA", "최고강조 잉크(제목/핵심수치)"),
    ("#5A35DF", 117, "A1,A1-S1,A2,A3,A4,A5,EXTRA", "브랜드 accent(버튼/링크/활성상태)"),
    ("#FFF", 107, "ALL", "표면 흰색"),
    ("#8A83A8", 82, "ALL", "muted 보조텍스트(3차 정보)"),
    ("#4A3F72", 70, "A1,A1-S1,A3,A5", "보조 본문(2차 정보, 인디고 톤)"),
    ("#A8A5B6", 50, "ALL", "placeholder/시간/비활성 아이콘"),
    ("#6B6880", 21, "A4,A5,EXTRA-01", "라벨/등록자 텍스트"),
    ("#EEE8FF", 19, "A1,A2,A3,EXTRA-01", "브랜드 100 배경(배지/pill 배경)"),
    ("#EF4665", 19, "A1-S1,A3,A5", "danger/차감/에러 강조"),
    ("#EAE7F5", 15, "A5", "admin 보더 라인(연한 회보라)"),
    ("#FDFDFF", 14, "A2,A3,A4,EXTRA", "BottomDock 배경(거의 흰색)"),
    ("#C7C3D6", 13, "EXTRA-01", "chevron 비활성 컬러"),
    ("#F7F6FC", 12, "ALL", "캔버스 배경(카드 바깥 배경)"),
    ("#FBFAFE", 12, "A1,A1-S1,A3,A4", "카드 서브표면(살짝 톤 다운된 흰색)"),
    ("#F0EEF7", 11, "A2,A3,A4,A5", "구분선/보더 라인"),
    ("#2F8C5C", 8, "A4,A5", "'민준' 아바타 텍스트 그린톤"),
    ("#22C55E", 6, "A1,A2,A4", "온라인 상태 dot"),
    ("#DCF4E8", 7, "A3,A5", "완료/성공 배지 배경(연초록)"),
    ("#DCEBFB", 7, "A4,A5", "'아빠' 아바타 배경(연파랑)"),
    ("#3C7BC4", 7, "A4,A5", "'아빠' 아바타 텍스트(파랑)"),
    ("#D9D2F3", 7, "A1-S1,A3,A5", "outline 보더(연보라)"),
    ("#EFECF8", 7, "A2,A3,A4", "구분선/배경(연보라 회색)"),
    ("#6944EF", 5, "A4", "발신(own) 말풍선 배경 — 현재 --color-chat-own과 EXACT MATCH"),
    ("#F3F0FF", 4, "A4", "수신(other) 말풍선 배경 — 현재 --color-chat-other와 EXACT MATCH(참고: raw 카운트는 background 단축 표기 누락으로 실측치보다 낮게 집계되었을 수 있음, NOT_VERIFIED 전수 카운트)"),
]

for raw, occ, screens, role in color_data:
    key = raw.upper()
    if key == "#FFF":
        key = "#FFFFFF"
    match = CURRENT_TOKENS.get(key)
    if match:
        cls, name, conf = "MIGRATION_ALIAS_CANDIDATE", match, "HIGH(EXACT_HEX_MATCH)"
    else:
        # check near-miss (delta <= 3 in any channel) against brand/ink tokens
        near = None
        try:
            rr, gg, bb = int(raw[1:3],16), int(raw[3:5],16), int(raw[5:7],16)
            for tok_hex, tok_name in CURRENT_TOKENS.items():
                if len(tok_hex) == 7:
                    tr, tg, tb = int(tok_hex[1:3],16), int(tok_hex[3:5],16), int(tok_hex[5:7],16)
                    if abs(rr-tr) <= 4 and abs(gg-tg) <= 4 and abs(bb-tb) <= 4:
                        near = tok_name
                        break
        except Exception:
            pass
        if near:
            cls, name, conf = "SOURCE_CONFLICT", f"near-miss of {near}", "MEDIUM(채널당 delta<=4, 반올림 오차 가능성 vs 의도적 변경 가능성 모두 존재 — PM 확인 필요)"
        else:
            cls, name, conf = ("SEMANTIC_CANDIDATE" if occ >= 6 else "ONE_OFF_LITERAL"), f"color.approved.NEW_{raw.lstrip('#')}", ("MEDIUM" if occ>=6 else "LOW")
    pm_gate = "YES" if cls in ("SOURCE_CONFLICT", "SEMANTIC_CANDIDATE") else ("YES" if cls=="MIGRATION_ALIAS_CANDIDATE" else "NO")
    add("color", raw, occ, screens, role, cls, name, conf, pm_gate)

# Font sizes
fs_data = [("11px",73),("13px",69),("12px",60),("10px",58),("14px",54),("15px",33),("16px",24),
    ("9px",20),("12.5px",19),("13.5px",17),("20px",16),("19px",12),("17px",11),("26px",5),
    ("18px",5),("11.5px",5),("30px",3),("24px",2),("37px",1),("31px",1)]
for raw, occ in fs_data:
    cls = "REPEATED_LITERAL" if occ >= 10 else "ONE_OFF_LITERAL"
    add("font-size", raw, occ, "ALL(분산)", "본문/라벨/제목 scale 원소", cls,
        f"typography.approved.{raw.replace('.', '_').replace('px','')}", "MEDIUM",
        "YES" if cls == "REPEATED_LITERAL" else "NO",
        "현재 global.css는 Display/Page/Section/Card/Body 명명 scale(주석)만 있고 실제 px 목록과의 1:1 매핑은 NOT_VERIFIED")

# Spacing (padding/gap combined, top values)
sp_data = [("padding","13px 14px",17),("padding","10px 30px 0",9),("padding","8px 14px",8),
    ("padding","0 2px",8),("padding","8px 18px",8),("padding","4px 10px",7),
    ("padding","7px 20px 5px",7),("padding","16px 24px",6),("padding","15px 16px",6),
    ("gap","3px",97),("gap","7px",33),("gap","2px",32),("gap","4px",30),("gap","10px",30),
    ("gap","12px",26),("gap","6px",24),("gap","8px",19),("gap","5px",19)]
for kind, raw, occ in sp_data:
    cls = "REPEATED_LITERAL" if occ >= 15 else "ONE_OFF_LITERAL"
    add(f"spacing-{kind}", raw, occ, "ALL(분산)", f"{kind} 원소값", cls,
        f"space.approved.{kind}.{raw.replace(' ','_').replace('px','')}", "MEDIUM",
        "YES" if cls == "REPEATED_LITERAL" else "NO",
        "현재 --space-1..12(4/8/12/16/20/24/32/40/48px) 스케일과 비교 시 3px/7px/5px 등 홀수값이 다수 존재 — TOKEN_CONFLICT(현재 스케일이 4의 배수 기반인 반면 원본은 3/5/7/9/11px 등 홀수 다수 사용)")

# Radius
rad_data = [("50%",108),("999px",50),("1px",45),("12px",22),("18px",19),("14px",18),
    ("20px",14),("3px",11),("16px",10),("10px",10),("44px",9),("2px",9),("4px",9),
    ("6px",7),("8px",7),("24px",6),("6px 18px 18px 18px",6),("5px",5),("7px",5),("22px",4)]
for raw, occ in rad_data:
    if raw == "999px":
        cls, name, conf = "MIGRATION_ALIAS_CANDIDATE", "--radius-pill(EXACT MATCH)", "HIGH"
    elif raw == "16px":
        cls, name, conf = "MIGRATION_ALIAS_CANDIDATE", "--radius-control(EXACT MATCH)", "HIGH"
    elif raw == "44px":
        cls, name, conf = "SOURCE_CONFLICT", "phone-mockup-frame-only, not a component radius(PRESENTATION_ARTIFACT)", "HIGH(제외 권장)"
    elif raw == "50%":
        cls, name, conf = "REPEATED_LITERAL", "radius.circle(원형 아바타/아이콘 전용, 이미 관용적)", "HIGH"
    elif occ >= 10:
        cls, name, conf = "SEMANTIC_CANDIDATE", f"radius.approved.{raw.replace('px','').replace(' ','_')}", "MEDIUM"
    else:
        cls, name, conf = "ONE_OFF_LITERAL", f"radius.approved.{raw.replace('px','').replace(' ','_')}", "LOW"
    add("border-radius", raw, occ, "ALL(분산)", "카드/버튼/뱃지 모서리", cls, name, conf,
        "YES" if cls in ("SOURCE_CONFLICT","SEMANTIC_CANDIDATE","MIGRATION_ALIAS_CANDIDATE") else "NO")

# Shadows
sh_data = [("0 5px 16px rgba(60,30,120,.05)",15,"A3 카드"),
    ("0 30px 70px rgba(40,20,90,.22)",9,"폰 프레임 자체(PRESENTATION_ARTIFACT)"),
    ("0 6px 18px rgba(60,30,120,.07)",3,"A1 카드"),
    ("0 7px 16px rgba(70,35,180,.26)",3,"버튼류 강조 그림자")]
for raw, occ, ctx in sh_data:
    cls = "SOURCE_CONFLICT" if "30px 70px" in raw else ("SEMANTIC_CANDIDATE" if occ >= 10 else "ONE_OFF_LITERAL")
    note = "현재 --shadow-sm/--shadow-md 값(rgb(70 47 158/6%),(10%)) 과 색상축(70,47,158 vs 60,30,120 / 70,35,180)이 달라 direct alias 불가 — 새 shadow 스케일 후보"
    add("box-shadow", raw, occ, ctx, "카드/프레임 elevation", cls, f"shadow.approved.{occ}", "MEDIUM",
        "YES" if cls != "ONE_OFF_LITERAL" else "NO", note)

# Layout widths
w_data = [("480px",9,"phone mockup frame(PRESENTATION_ARTIFACT, not a content token)"),
    ("132px",9,"home indicator bar(PRESENTATION_ARTIFACT)"),
    ("78px",6,"A1 avatar(large)"),("42px",12,"소형 아이콘/아바타"),
    ("38px",13,"chat avatar / 원형버튼")]
for raw, occ, note in w_data:
    cls = "SOURCE_CONFLICT" if "PRESENTATION_ARTIFACT" in note else ("SEMANTIC_CANDIDATE" if occ>=10 else "ONE_OFF_LITERAL")
    add("layout-width", raw, occ, "ALL(분산)", "고정 폭 요소", cls, f"size.approved.{raw.replace('px','')}", "MEDIUM",
        "YES" if cls != "ONE_OFF_LITERAL" else "NO", note)

# Control height (44px touch target — cross-reference with --size-touch-min)
add("control-height", "44px", 1, "A4(전송버튼)", "primary touch target", "MIGRATION_ALIAS_CANDIDATE",
    "--size-touch-min(EXACT MATCH)", "HIGH", "YES", "유일하게 명시적으로 44px인 컨트롤 — 나머지(38px chevron 등)는 44px 미달")

# Font family (explicit REQUIRES_PM_DECISION — hard conflict, not a simple alias)
add("font-family", "'Noto Sans KR' (Google Fonts CDN)", 1, "ALL", "본문/제목 서체 전체", "REQUIRES_PM_DECISION",
    "N/A — 현재 구현은 'Pretendard'+'Black Han Sans'+'Inter' 사용 중, 직접 대체 불가", "HIGH(불일치 확실)",
    "YES", "폰트 패밀리 자체가 승인자료(Noto Sans KR)와 현재 구현(Pretendard 등)에서 다름 — token alias가 아니라 PM 정책 결정 필요 항목")

with open(OUT, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["category","raw_value","occurrence_count","source_files","screen_ids",
        "intended_semantic_role","classification","proposed_candidate_name","confidence","pm_gate_required","note"]
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {len(rows)} rows")
