# Current Screen / Route Map

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Sections 16-17). Full data: `current_screen_route_map.csv` (8 rows). Source: direct read of `frontend/src/App.tsx` (114 lines, full file) plus the page/platform components it references.

## Confirmed current route set (re-verified in code, not assumed from the brief)

```
/                → pages/Auth/index.tsx                              (public, redirects if logged in)
/dashboard       → ProtectedRoute > MongleAppShell > UserDashboard     (legacy, real API)
/admin/*         → AdminProtectedRoute > MongleAppShell > AdminDashboard (legacy, real API)
/wagle           → ProtectedRoute > MongleAppShell > DoranLanding      (canonical, FIXTURE ONLY)
/family          → ProtectedRoute > MongleAppShell > AccessBoundary > FamilyLanding (canonical, stub)
/naran/doran     → LegacyRouteRedirect → /wagle (replace, query+hash preserved)
/naran/family    → LegacyRouteRedirect → /family (replace, query+hash preserved)
*                → NotFoundPage (404 catch-all, registered last so it never shadows the legacy aliases)
```

This is an exact match to the route set already stated in this task's baseline context — re-derived
independently from `App.tsx` line-by-line, not copied from the brief.

## Headline findings (see CSV for full per-route detail)

1. **`/wagle` (와글와글) is entirely fixture-backed.** `DoranLanding.tsx` imports all room/message/service-event
   data from `platform/doran/preview/*.ts` — static TypeScript constants, not API calls. A `import.meta.env.DEV`-gated
   notice literally says "UX Gate 미리보기 · 실제 API 연결 전 화면입니다." The Doran API contract
   (`/api/families/{family_id}/doran`) is never called anywhere in `frontend/src` outside this preview data
   (confirmed by grep). This is the single most important functional-boundary finding for Phase B.
2. **`/family` is a 15-line stub.** `FamilyLanding.tsx` shows only the family's name and relationship string,
   with an explicit comment that member-management features are deferred. None of approved screen A2's
   zones (GreetingHeader, PromoCard, RecentActivityCard, ServiceGrid, Dock content) are implemented here.
3. **`/dashboard` and `/admin/*` are real, API-backed, and pre-date the Mongle platform layer** ("legacy" per
   the code's own naming — `isLegacyDashboard` in `MongleAppShell.tsx`). They correspond functionally to
   approved A3 and A5 respectively, and are far more functionally complete than `/wagle`/`/family`, but
   their current visual presentation was not compared pixel-for-pixel against the approved PNGs in this
   session (no screenshot capture of the *current* app was performed — out of scope/no running dev server
   in this read-only session; recorded as `NOT_VERIFIED`, not assumed to match or mismatch).
4. Legacy alias routes (`/naran/doran`, `/naran/family`) are registered as explicit, individual `<Route>`
   entries (not left to the catch-all), confirmed by reading `App.tsx` lines 100-101 directly, and are
   extensively covered by `specs-mongle/01-shell.spec.ts` (redirect-once, query/hash preservation,
   no-Back-loop, no-404-fallthrough — 4 dedicated tests).
