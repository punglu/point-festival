# SOURCE_SCREEN_INVENTORY

All screens found in `가족 플랫폼 화면 재현.dc.html`, the sole approved source. No external mockup images were provided as separate files at extraction time — the HTML file itself is the visual authority for every screen listed below.

| ID | Screen name | Visual authority | Notes |
|---|---|---|---|
| 1a | 로그인 / 프로필 선택 | HTML | |
| 1a-1 | 순수 로그인 (아이디/비밀번호) | HTML | |
| 1b | 가족 홈 | HTML | |
| 1c | 포인트 잔치 | HTML | |
| 1d | 가족 대화 | HTML | |
| 1e | 관리자 · 포인트 관리 | HTML | |
| 1f | 나 · 프로필 | HTML | |
| 1g | 가족 일정 | HTML | |
| 1h | 앨범 | HTML | |
| 1i | 할 일 | HTML | |
| 1j | PIN 입력 / 잠금 해제 | HTML | |
| 1j-1 | 계정 잠금 안내 | HTML | |
| 1k | 미션 상세 · 인증 제출 | HTML | |
| 1l | 포인트 사용 · 보상 교환 | HTML | |
| 1m | 관리자 · 미션 승인 대기함 | HTML | |
| 1n | 알림 목록 | HTML | |
| 1o | 일정 추가 | HTML | |
| 1p | 사진 상세 뷰어 | HTML | |
| 1q | 가족 구성원 관리 | HTML | |
| 1r | 온보딩 · 가족 만들기 | HTML | |
| 1s | 미션 반려 사유 확인 | HTML | |
| 1t | 가족 채팅방 설정 | HTML | |
| 1u | 설정 · PIN 변경 | HTML | |
| 1v | 관리자 · 가족 규칙/포인트 정책 | HTML | |
| 1w | 앨범 · 검색 결과 | HTML | |
| 1x | 보호자 · 자녀 주간 리포트 | HTML | |
| 1y | 에러 · 빈 상태 (3 variants: 네트워크 오류, 알림 없음, 검색 결과 없음) | HTML | |
| 1z0 | 기본 모달 폼 (초기 버전, 할 일 삭제 바텀시트) | HTML (hidden, `display:none`) | Superseded duplicate. Still valid visual evidence of a bottom-sheet delete-confirm pattern. |
| 1z1 | 미션 만들기/관리 (초기 버전) | HTML (hidden) | Superseded by 2e. |
| 1z2 | 사용자 관리 상세 (초기 버전) | HTML (hidden) | Superseded by 2a. |
| 1z3 | 사진/파일 전체보기 (초기 버전) | HTML (hidden) | Superseded by 2b. |
| 1z4 | 레벨업/뱃지 축하 모달 (초기 버전) | HTML (hidden) | Superseded by 2c. |
| 1z5 | 비밀번호 찾기 플로우 (초기 버전, 2-screen) | HTML (hidden) | Superseded by 2d. |
| 1z | 기본 모달 폼 (관리자 · 미션 만들기, final) | HTML | |
| 2a | 관리자 · 사용자 관리 상세 | HTML | |
| 2b | 대화 · 사진/파일 전체보기 | HTML | |
| 2c | 레벨업 축하 모달 (final) | HTML | |
| 2d | 비밀번호 찾기 · 이메일 인증 (final, 2-screen) | HTML | |
| 2e | 관리자 · 미션 목록 관리 | HTML | |
| 2f | 가족 규칙 · 자녀 초대 승인 | HTML | |
| 2g | 대화 · 답장 / 메시지 옵션 | HTML | |
| 2h | 보상 교환 확인 다이얼로그 | HTML | |
| 2i | 관리자 · 부모 대시보드 | HTML | |
| 2j | 아이 · 리워드샵 | HTML | |
| 2k | 설정 전체 목록 | HTML | |

## Omission check
No screen referenced in chat history (turns requesting additions) is missing from the HTML at extraction time; all requested screens through "부모 대시보드, 아이 리워드샵, 설정 전체 목록" are present. **No SOURCE_SCREEN_OMISSION_FOUND.**

## Assets outside token scope
`uploads/family_platform_pin_logo_transparent_1024.png` (brand pin logo/mascot) — used as imagery, not sampled for UI color tokens per task rule excluding brand-illustration colors.
