# Legacy Files (Firebase 기반 원본)

이 폴더는 마이그레이션 이전의 원본 파일을 보관합니다.
**절대 수정하지 마세요.** Phase 3~5에서 CSS/HTML 참조 원본으로 사용됩니다.

| 파일 | 용도 |
|---|---|
| index.html | 홈/랭킹 페이지 (다크 테마) — Phase 5 참조 |
| user.html | 아이용 대시보드 — Phase 3 참조 |
| admin.html | 관리자 대시보드 — Phase 4 참조 |
| styles.css | 전역 CSS 1,589줄 — CSS Modules 이관 원본 |
| firebase.json | Firebase Hosting 설정 |
| database_rules.json | Firebase RTDB 보안 규칙 |
| migrate-player-auth.js | PIN 분리 마이그레이션 스크립트 |

**삭제 예정:** Phase 7 (프로덕션 배포 완료) 후 이 폴더를 삭제합니다.
