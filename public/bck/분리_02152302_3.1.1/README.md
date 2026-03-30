# 마인크래프트 포인트 잔치 v3.0

## 📋 프로젝트 구조

```
minecraft-point-festival/
├── index.html             # 메인 선택 페이지 (사용자/관리자 선택)
├── user.html              # 사용자 조회 전용 페이지
├── admin.html             # 관리자 전체 관리 페이지
├── styles.css             # 공통 스타일시트
├── firebase.json          # Firebase Hosting 설정
├── .firebaserc            # Firebase 프로젝트 설정
├── database.rules.json    # Firebase Security Rules
└── README.md              # 이 파일
```

## 🚀 배포 방법

### 1. Firebase CLI 설치 (최초 1회)

```bash
npm install -g firebase-tools
```

### 2. Firebase 로그인

```bash
firebase login
```

### 3. 프로젝트 배포

```bash
# 프로젝트 폴더에서 실행
firebase deploy
```

### 4. 배포 완료!

```
✅ https://mark-point-festivals.web.app               (메인 선택 페이지)
✅ https://mark-point-festivals.web.app/user.html     (사용자 페이지)
✅ https://mark-point-festivals.web.app/admin.html    (관리자 페이지)
```

## 🔐 보안 설정

### Security Rules 적용

배포 시 `database.rules.json` 파일이 자동으로 적용됩니다.

**권한:**
- 📖 **읽기**: 모두 허용
- ✍️ **쓰기**: 
  - 사용자: `statusMsg`, `feedbacks`만 가능
  - 관리자: 모든 권한 (비밀번호 인증 필요)

### 관리자 비밀번호 변경

`admin.html` 파일에서 다음 라인을 찾아 수정:

```javascript
if(document.getElementById('adminPwd').value === 'admin1234') {
```

→ `'admin1234'`를 원하는 비밀번호로 변경

## 📱 사용 방법

### 🏠 메인 페이지

1. https://mark-point-festivals.web.app 접속
2. "아이들 보기" 또는 "관리자 페이지" 선택

### 👦 사용자 (아이들)

1. 메인 페이지에서 "아이들 보기" 클릭
2. 이름 선택
3. 오늘의 미션 확인
4. 포인트 현황 조회
5. 피드백 작성

### 🛠️ 관리자 (부모님)

1. 메인 페이지에서 "관리자 페이지" 클릭
2. 비밀번호 입력
3. 미션 생성/관리
4. 포인트 승인/차감
5. 응원 메시지 작성

## 🎨 주요 기능

### 사용자 페이지
- ✅ **PIN 로그인** (4자리 숫자)
- ✅ 자동 로그인 (기본 활성화)
- ✅ 5회 실패 시 5분 잠금
- ✅ 플레이어 선택
- ✅ 미션 목록 조회
- ✅ 포인트 현황 확인
- ✅ 부모님 응원 메시지 보기
- ✅ 상태 메시지 작성
- ✅ 피드백 전송
- ✅ 전체 기록 조회

### 관리자 페이지
- ✅ **사용자 관리**
  - 사용자 등록 (이름 + PIN)
  - 사용자 삭제
  - PIN 설정/변경
  - 잠금 해제
  - 로그인 기록 조회
  - 마지막 접속 시간 확인
- ✅ 미션 생성/수정/삭제
- ✅ 미션 승인/실패 처리
- ✅ 포인트 차감 관리
- ✅ 포인트 동기화
- ✅ 부모님 메시지 관리
- ✅ 사진 업로드
- ✅ 미션 복제/일괄삭제
- ✅ 전체 데이터 관리

## 💰 비용

**100% 무료** (Firebase 무료 티어 사용)

- Realtime Database: 1GB 저장, 10GB/월 다운로드
- Hosting: 10GB 저장, 360MB/일 전송
- 가족 사용 기준 충분

## 🔧 커스터마이징

### 색상 변경

`styles.css` 파일에서 CSS Variables 수정:

```css
:root {
  --accent: #10b981;  /* 메인 색상 */
  --blue: #3b82f6;    /* 파란색 */
  --danger: #ef4444;  /* 빨간색 */
  /* ... */
}
```

### 텍스트 변경

각 HTML 파일에서 직접 수정 가능합니다.

## 📊 데이터 구조

### Players (아이들)
```javascript
mc_players/{playerId}/
  name: "아이 이름"
  pin: "1234"              // NEW - 4자리 PIN
  totalPoints: 280
  photo: "base64..."
  statusMsg: "오늘의 다짐"
  loginAttempts: 0         // NEW - 로그인 실패 횟수
  lockUntil: null          // NEW - 잠금 해제 시간
  lastLogin: timestamp     // NEW - 마지막 접속 시간
```

### Missions (미션)
```javascript
mc_mission_data/{playerId}/{date}/missions/{missionId}/
  text: "미션 내용"
  point: 10
  status: "active" | "completed" | "failed"
  sender: "아빠" | "엄마"
  msg: "응원 메시지"
  order: 0
```

### Deductions (차감)
```javascript
mc_deductions/{playerId}/{deductId}/
  amount: 50
  reason: "간식"
  date: "2026-02-15"
  timestamp: 1739577600000
```

### Login Logs (로그인 기록) - NEW
```javascript
mc_login_logs/{playerId}/{logId}/
  timestamp: 1739577600000
  success: true/false
  date: "2026-02-15"
```

## 🐛 문제 해결

### 배포 안 됨
```bash
# Firebase 재로그인
firebase logout
firebase login

# 프로젝트 재초기화
firebase init hosting
```

### 데이터 안 보임
- Firebase Console에서 Database Rules 확인
- 브라우저 콘솔에서 에러 확인

### 이미지 업로드 안 됨
- 파일 크기 확인 (50KB 미만 권장)
- 이미지 압축 기능 자동 동작

## 📞 지원

문제가 있으시면 Firebase Console에서:
1. Database 탭에서 데이터 확인
2. Hosting 탭에서 배포 상태 확인
3. Rules 탭에서 보안 규칙 확인

## 📝 버전 히스토리

### v3.0 (2026-02-15)
- ✅ 페이지 분리 (user/admin)
- ✅ CSS 분리
- ✅ **PIN 로그인 시스템**
  - 4자리 PIN 인증
  - 자동 로그인 (기본 ON)
  - 5회 실패 시 5분 잠금
  - 로그인 기록 저장
  - 마지막 접속 시간 표시
- ✅ **사용자 관리 기능**
  - 사용자 등록/삭제
  - PIN 설정/변경
  - 잠금 해제
  - 로그인 기록 조회
- ✅ 이미지 압축 기능
- ✅ Security Rules 적용
- ✅ Firebase Hosting 배포

### v2.5 (이전)
- MVP 단일 HTML 파일

## 📄 라이선스

가족 사용 목적으로 자유롭게 사용 가능합니다.
