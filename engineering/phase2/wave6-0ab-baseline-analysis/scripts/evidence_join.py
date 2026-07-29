#!/usr/bin/env python3
import csv
OUT = "/tmp/mongle-wave6-0ab/cross-reference/w6_0ab_evidence_join.csv"

rows = [
 dict(screen_id="A1", approved_source="standalone-src.html#1a + screen_login_approved.png", approved_zones="ProfileSelectorCard, AdminEntryRow (html_zone_inventory.csv)",
   approved_measurement="MEASUREMENT_TABLE_V2 rows tagged A1", current_route="/", current_component="pages/Auth/index.tsx + PlayerSelectView/PlayerCard",
   functional_contract="select→PIN→session MUST_PRESERVE; A1-S1 ID/PW form KNOWN_GAP", token_delta="brand accent/ink near-miss(D2/D3)",
   component_gap="PARTIAL(admin-entry UX differs)", asset_gap="none material for A1 itself", e2e_coverage="specs/01-login(2, CURRENT_TEMPORARY) + specs-mongle loginAsFirstPlayer helper(indirect, every test)",
   expected_change_files="see PER_SCREEN_FILE_CHANGE_PLAN A1", pm_decision="D1(aspect ratio), D2/D3(color near-miss), D4(font), D9(A1-S1)",
   readiness="READY_WITH_PM_DECISION"),
 dict(screen_id="A2", approved_source="standalone-src.html#1b + screen_family_home_approved.png", approved_zones="GreetingHeader, ChatPromoHeroCard, RecentActivityCard, ServiceGrid, BottomDock",
   approved_measurement="MEASUREMENT_TABLE_V2 rows tagged A2", current_route="/family (stub) + MongleAppShell Dock(global)",
   functional_contract="Account/Family Context, Header, Dock filtering MUST_PRESERVE; home CONTENT itself MISSING",
   token_delta="chat colors exact match; brand/ink near-miss same as A1", component_gap="MISSING(FamilyLanding 15-line stub); Dock PARTIAL(label-only, icon asset gap self-documented in code)",
   asset_gap="Hero illustration + 3 service-tile icons SOURCE_MISSING(independently re-verified this session)",
   e2e_coverage="specs-mongle: Family-switch, permission-forbidden, mapping-required, canonical route render/refresh(4+ tests) — none assert visual content",
   expected_change_files="see PER_SCREEN_FILE_CHANGE_PLAN A2", pm_decision="D5(assets), D10(Dock routes, pre-existing open code comment)",
   readiness="BLOCKED_BY_SOURCE(assets missing) + BLOCKED_BY_FUNCTION(screen not built)"),
 dict(screen_id="A3", approved_source="standalone-src.html#1c + screen_point_festival_approved.png", approved_zones="ProfileSummaryCard, WeekDateStrip, FamilyCheerCard, TodayMissionListCard",
   approved_measurement="MEASUREMENT_TABLE_V2 rows tagged A3", current_route="/dashboard", current_component="pages/UserDashboard/index.tsx + 11 components",
   functional_contract="mission/points/deduction/level/cheer/approval MUST_PRESERVE(real API, operational history)",
   token_delta="mission-icon emoji-vs-flat-icon gap(same pattern as A2)", component_gap="PARTIAL(component set exists, visual 1:1 NOT_VERIFIED this session)",
   asset_gap="mission icons SOURCE_MISSING(broom/book/people/card)", e2e_coverage="specs/02-mission.spec.ts(2, CURRENT_TEMPORARY)",
   expected_change_files="see PER_SCREEN_FILE_CHANGE_PLAN A3", pm_decision="D5(assets, shared with A2)",
   readiness="READY_WITH_PM_DECISION"),
 dict(screen_id="A4", approved_source="standalone-src.html#1d + screen_family_chat_approved.png", approved_zones="ChatHeader, MessageTimeline, Composer(single GROUP room only)",
   approved_measurement="MEASUREMENT_TABLE_V2 category F", current_route="/wagle", current_component="platform/pages/DoranLanding.tsx + 10 platform/doran/components",
   functional_contract="ALL FIXTURE_ONLY/CURRENT_TEMPORARY — no live backend behind any of it",
   token_delta="chat bubble colors EXACT MATCH(best token alignment of the whole audit)", component_gap="MINOR_RENDERING_NOISE structurally(TIER1), but Room List/DIRECT/SERVICE = EXTRA_CURRENT_UI(no approved counterpart)",
   asset_gap="none material for the GROUP conversation view itself", e2e_coverage="specs-mongle: 8+ tests, but 0 assert real message send/receive(fixture-safe only)",
   expected_change_files="see PER_SCREEN_FILE_CHANGE_PLAN A4(doranApi.ts PROPOSED_PATH — the actual blocker)", pm_decision="D6(Room List scope), D7(desktop auto-select provenance)",
   readiness="BLOCKED_BY_FUNCTION(no backend) / BLOCKED_BY_BACKEND"),
 dict(screen_id="A5", approved_source="standalone-src.html#1e + screen_admin_point_approved.png", approved_zones="AdminSidebar, MainHeaderRow, StatCardRow, DeductionDataTable",
   approved_measurement="MEASUREMENT_TABLE_V2 category G", current_route="/admin/points(views/PointView)", current_component="AdminDashboard/views/PointView/PointView.tsx + hooks/usePointView",
   functional_contract="auth/RBAC/point-data/filter/dialogs MUST_PRESERVE(current implementation AHEAD of approved source — dialogs exist, approved PNG has none)",
   token_delta="admin sidebar dark(#1e1b4b) vs approved light(#FBFAFE) TOKEN_CONFLICT", component_gap="PARTIAL(functionally ahead, visual tone conflict)",
   asset_gap="none material", e2e_coverage="specs/03-admin.spec.ts(3, CURRENT_TEMPORARY)",
   expected_change_files="see PER_SCREEN_FILE_CHANGE_PLAN A5", pm_decision="D8(sidebar tone)",
   readiness="READY_WITH_PM_DECISION"),
]

fieldnames = ["screen_id","approved_source","approved_zones","approved_measurement","current_route","current_component",
  "functional_contract","token_delta","component_gap","asset_gap","e2e_coverage","expected_change_files",
  "pm_decision","readiness"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {len(rows)} rows")
