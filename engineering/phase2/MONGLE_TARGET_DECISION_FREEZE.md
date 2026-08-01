# 몽글 Target Decision Freeze

**Status:** `APPROVED` / `FROZEN` — PM approved D1–D8 on 2026-08-01. This document is the **Target product contract SSOT**.

## What "APPROVED / FROZEN" does and does not mean

This document separates four axes; do not collapse them.

| Axis | Meaning here |
|---|---|
| `APPROVED TARGET CONTRACT` | The frozen product decision every implementation task must satisfy. D1–D8 below. |
| `CURRENT IMPLEMENTATION` | What the repository actually contains today. Cited as evidence only, never as proof a decision is built. |
| `DEFERRED IMPLEMENTATION POLICY` | `D6-P1`–`D6-P8` and named future-service policies. Decided at the relevant task's own Start Gate. |
| `LEGACY / HISTORICAL REFERENCE` | Pre-pivot point-festival material and superseded planning prose. Background only. |

An `APPROVED` decision is a binding design contract, **not** a claim that any
table, API, route, worker, or screen implementing it exists. Freeze authorizes
planning and, once a task's own Start Gate passes, implementation — it does not
retroactively mark anything complete. No row below may be reopened, narrowed or
widened without a new PM decision.

## Evidence boundary

- Current assets: `backend/app/domains/family/models.py`, `backend/app/domains/doran/models.py`, `backend/app/domains/service_outbox/models.py`, `backend/app/domains/mission/models.py`, `engineering/phase1/ACCOUNT_FAMILY_RBAC_CONTRACT.md`, `engineering/phase2/DORAN_MESSAGING_CONTRACT.md`.
- Legacy reference: `engineering/LEGACY_MARKPOINT_REFERENCE.md`; it is not a target contract.
- Test governance: `agent-system/qa/TEST_POLICY.md`, `agent-system/qa/COVERAGE_MAP.md`, `tests/README.md`.

| ID | Question / recommendation | Current asset and options | PM decision required |
|---|---|---|---|
| D1 | FamilyGroup is the family platform's organisation, communication and data-isolation boundary; Account supports multiple FamilyMemberships. | `family_groups`/`family_memberships` exist. Generic groups are out of current product scope. | **APPROVED** |
| D2 | `아이디 + 플랫폼 비밀번호` is the Account credential. FamilyAdmin may provision an independent Account and initial credential within its FamilyGroup. | `accounts` exists; independent Account credential/session does not yet. Legacy PIN is not primary identity. | **APPROVED** — PIN scope is defined by approved D3-PIN-SCOPE. |
| D3 | Persistent Account Session is separate from ActiveFamilyContext; optional Wagle PIN is a local conversation-screen lock, not Account authentication. | Phase 1 contract supports Account/context separation; current legacy tokens are player/global-role based. | **APPROVED** — D3-PIN-SCOPE is Account + Device personal PIN; shared PIN is unsupported. |
| D4 | FamilyAdmin and ServiceAdmin are separate, FamilyMembership-scoped roles; service operations require the explicit ServiceAdmin binding. Default deny applies. | `roles`, `permissions`, membership role assignments exist; seed is implementation baseline only. | **APPROVED** — detailed permissions, audit and safety constraints below. |
| D5 | Service ownership, registration, access and machine identity are separate. D5-A/A1/A2/A3/B/C are approved; Markpoint uses FamilyMembership identity and no separate Participant at this stage. | `ServiceSubscription`, `service_principals` and Doran binding exist; Markpoint is `player_id` owned. | **APPROVED** — implementation validates existing principal/binding reuse. |
| D6 | Wagle uses WebSocket for foreground realtime and Web Push for background notification. Durable DB + transactional Outbox are SSOT; delivery is at-least-once with deduplication and recovery. | Room/Message/Participant/read-state assets exist; outbox consumer/realtime are not complete. | **APPROVED** — v1 contract below. |
| D7 | Family-owned features/services use explicit `/families/{familyId}/...` route/API scope; personal services use `/me/...`. Server revalidates all family/resource authorization. | legacy player REST APIs and family/Doran paths exist. | **APPROVED** — Target contract below; actual endpoint inventory remains implementation work. |
| D8 | Legacy data is `RESET`: no legacy users, credentials, family, Markpoint or chat data migrates into Target. Legacy is separately retained read-only until PM-approved retirement. | legacy player-owned tables and target-shaped platform tables coexist. | **APPROVED** — reset/cutover contract below. |

D1–D8 are `APPROVED` and `FROZEN`. `D6-P1`–`D6-P8` are separately
`DEFERRED_TO_RELEVANT_TASK_START_GATE` and `NON_BLOCKING_FOR_DECOMPOSITION`;
they are recorded in `agent-system/active.md`. No D1–D8 row is
`PM_DECISION_REQUIRED` any longer, and no task may cite D1–D8 as its blocker.

## Package reconciliation — Decision SSOT

This is the Target Decision SSOT. Axis B retains current-code evidence but is partially superseded for Target ownership, implementation readiness and migration judgement.

| ID | Reconciled decision | Status |
|---|---|---|
| D5-A | Core Capability and Family Service Entitlement: Family-owned optional services use FamilyGroup-scoped `ServiceSubscription` with `INACTIVE` / `ACTIVE` / `SUSPENDED`. Wagle is core and never subscription-gated. | APPROVED |
| D5-A1 | Service Ownership Scope: a definition declares `CORE_FAMILY`, `PERSONAL`, `FAMILY`, or `PERSONAL_OR_FAMILY`; each instance has one explicit owner scope. | APPROVED |
| D5-A2 | Service Registration Authority: Registrant, Owner, User, ServiceAdmin and ServicePrincipal are distinct; a FamilyMember may register or request as policy permits. | APPROVED |
| D5-A3 | Family activation policy is per service: `MEMBER_SELF_ACTIVATE`, `MEMBER_REQUEST_ADMIN_APPROVAL`, `FAMILY_ADMIN_ONLY`, or `AUTO_ENABLE_ON_FAMILY_CREATION`. | APPROVED |
| D5-B | Markpoint: FamilyGroup owner, FamilyMembership identity, member request + FamilyAdmin approval/direct activation, ACTIVE Membership default access, explicit restrictions and ServiceAdmin; no separate Participant now. | APPROVED |
| D5-C | Markpoint System Actor: `ServicePrincipal` represents non-human Markpoint→Wagle automated events, scoped to the event FamilyGroup and approved Wagle room. | APPROVED |
| D6 | `WAGLE_REALTIME_PUSH: REQUIRED`; WebSocket foreground, Web Push background, durable DB/Outbox SSOT, at-least-once delivery, per-Room ordering, deduplication and recovery. | APPROVED |

`ServicePrincipal` is never a human participant. Do not automatically convert `player_id` to either `family_membership_id` or `service_principal_id`.

## D1 — Family Semantics, Multi-Family Membership and Communication Boundary

**Status:** `APPROVED`

**Approved invariant:** `FamilyGroup` is the organisational, communication, and data-isolation boundary. An `Account` may hold multiple `FamilyMembership`s. `ActiveFamilyContext` scopes current foreground screen work only; `AuthorizedFamilySet` is the complete set of FamilyGroups for which the Account holds an active Membership. Realtime uses one `Account + Device + Session` connection with multiplexed AuthorizedFamilySet family channels. `FamilyAdmin` is a `FamilyMembership + FamilyGroup` scoped role.

몽글은 가족용 플랫폼이며 기본 조직 경계는 `FamilyGroup`이다. 비가족 조직·범용 Group은 현재 제품 범위에 포함하지 않는다. 하나의 Account는 `0..N` `FamilyMembership`을 통해 `0..N` FamilyGroup에 속할 수 있고, Membership마다 상태·역할·권한·서비스 참여가 독립적이다.

### ActiveFamilyContext

- 활성 Membership이 없으면 가족 생성 또는 참여 흐름으로 진입한다.
- 하나면 자동 선택할 수 있고, 복수이면 가족 선택 화면을 제공한다.
- 전환 시 서버가 Membership 상태, 역할, 권한, 서비스 이용권을 다시 평가한다.
- 한 가족의 탈퇴·정지·승인 대기는 다른 가족 Membership에 영향을 주지 않는다.

### Family Communication Boundary

- 와글와글의 인간 간 Room, Direct Message, Participant, 검색·초대는 하나의 FamilyGroup 내부로만 제한한다.
- Participant는 Room의 FamilyGroup에 속한 활성 FamilyMembership이어야 한다.
- 서로 다른 FamilyGroup 간 Room 생성·메시지·구성원 검색·초대는 금지한다.
- 동일 Account가 여러 가족에 속해도 Room, 메시지, 읽음 상태, 알림은 FamilyGroup별로 격리한다. ActiveFamilyContext는 다른 Authorized Family의 background delivery를 막지 않는다.
- 서비스 시스템 메시지도 지정 FamilyGroup 및 Service Room 범위를 벗어나지 않는다.
- 클라이언트의 FamilyGroup ID만 신뢰하지 않고 Session, Membership, Room 소유권을 서버에서 교차 검증한다.

### FamilyAdmin

각 FamilyGroup에는 해당 가족 범위에서만 활동하는 Family Admin이 존재한다. Family Admin은 Platform Admin이나 Service Admin과 별개이며, 권한은 Account 전역이 아니라 FamilyMembership과 FamilyGroup Scope에 귀속한다. 후보 관리 범위는 초대 코드, 가입 요청, 구성원 상태, 가족 역할, 가족 정보, 서비스 이용권, 가족 내 Wagle 관리, Markpoint 관리자 지정이다.

가족당 관리자 수, 최초/마지막 관리자, 이전·복구, Family Admin의 기본 서비스 권한은 **D4 Scoped RBAC**에서 결정한다.

### Naming

Logical terms: `FamilyGroup`, `FamilyMembership`, `ActiveFamilyContext`, `FamilyAdmin`. Physical names: `family_groups`, `family_memberships`. `groups`, `group_memberships`, `group_type` 일반화는 승인된 제품 요구 전까지 추가하지 않는다. 신규 그룹 선택 UI는 Account가 속한 FamilyGroup 중 활동 가족을 선택하는 화면이다.

## D2 — Platform Credential and FamilyAdmin-Provisioned Account

**Status:** `APPROVED`

몽글의 기본 Account 인증 수단은 `아이디 + 플랫폼 비밀번호`다. 이메일·전화번호·외부 계정은 기본 Account 생성과 로그인에 필수 조건이 아니다. FamilyAdmin은 자신의 FamilyGroup 범위에서 이메일이나 전화번호가 없는 구성원을 위해 독립 Account, 초기 아이디 및 임시 플랫폼 비밀번호를 발급하고 초기 비밀번호 재설정·가족 Membership 연결·가족 내 접근 복구를 수행할 수 있다.

FamilyAdmin이 만든 Account도 관리자 Account의 하위 프로필이 아닌 독립 Account다. 고유한 FamilyMembership, 역할, 메시지, 읽음 상태, Markpoint 기록과 서비스 참여 기록을 가진다. FamilyAdmin 권한은 해당 FamilyGroup으로 제한되며, 다른 FamilyGroup Membership·기록 또는 구성원의 개인 메시지 임의 열람 권한을 주지 않는다. 구체적인 권한 binding과 감사 정책은 D4 Scoped RBAC에서 계약화한다.

## D3 — Persistent Platform Session and Optional Wagle PIN

**Status:** `APPROVED`

아이디와 플랫폼 비밀번호 인증 성공 시 Account 기준 플랫폼 Session을 생성한다. Session은 PWA 종료·재실행 뒤에도 유지될 수 있는 장기 Session이되, 무기한 고정 인증이 아니라 만료·갱신·취소·기기별 폐기가 가능해야 한다. Session은 특정 FamilyGroup에 종속되지 않고 Account의 전체 `AuthorizedFamilySet`을 인식한다. ActiveFamilyContext와 관계없이 활성 Membership을 가진 가족의 Push와 관리 알림을 받을 수 있다.

와글와글 PIN은 사용자가 선택적으로 설정하는, 이미 로그인된 기기에서 가족대화방 화면 접근을 보호하는 추가 잠금이다. PIN은 플랫폼 Account 인증·플랫폼 비밀번호 대체·새 Account Session 생성이 아니며, 기존 Session을 종료하거나 갱신하지 않는다. PIN을 설정하지 않으면 추가 인증 없이 와글와글에 진입한다. PIN 잠금 상태에서도 허용된 FamilyGroup의 Push, unread 집계, 백그라운드 동기화, FamilyAdmin 승인 요청, Markpoint 알림과 플랫폼의 다른 서비스는 계속 동작한다.

PIN이 설정된 경우 Push 열람은 PIN 확인 뒤 대화 내용을 표시한다. PIN 확인 전 payload와 미리보기는 “새 가족 메시지가 있습니다” 수준으로 민감한 메시지 본문을 최소화한다. PIN 실패는 플랫폼 로그아웃이나 다른 서비스 차단으로 이어지지 않는다. 플랫폼 로그아웃, Account 정지, Session 취소 또는 기기 연결 해제 시 해당 Session의 개인 Push subscription은 폐기하거나 비활성화한다.

### D3-PIN-SCOPE — Personal Wagle PIN

**Status:** `APPROVED`

와글와글 PIN은 `Account + Device` 단위의 개인 선택형 화면 잠금이다. FamilyGroup 공용 PIN과 FamilyGroup별 별도 PIN은 지원하지 않는다. 하나의 Account가 복수 FamilyGroup에 소속돼도 한 기기에서는 하나의 개인 PIN을 사용하며, 사용자는 기기별로 PIN을 설정하거나 생략할 수 있다.

PIN 해제는 FamilyGroup 또는 Room 접근 권한을 부여하지 않는다. 실제 대화 접근은 플랫폼 Session, FamilyMembership 상태, FamilyGroup Scope, Room Participant 및 Permission을 서버에서 재검증한다. FamilyAdmin은 구성원의 PIN을 열람할 수 없다. PIN 복구는 기존 PIN을 조회하지 않고 해당 기기의 PIN을 초기화한다. PIN 실패는 플랫폼 Session, 다른 서비스, 백그라운드 Push, unread 집계 또는 다른 FamilyGroup 이용을 차단하지 않는다.

## D4 — FamilyAdmin and ServiceAdmin Separation

**Status:** `APPROVED` — Option C

`FamilyAdmin`과 개별 서비스의 `ServiceAdmin`은 서로 다른 역할이다. 모든 관리 역할은 Account 전역이 아닌 FamilyMembership에 귀속한다.

```text
Account → FamilyMembership → FamilyGroup Role (FamilyAdmin)
Account → FamilyMembership → FamilyGroup → Service Scope → ServiceAdmin Role
```

FamilyAdmin은 해당 FamilyGroup에서 가입 승인·거절, 초대 코드 생성·폐기, 가족 정보, FamilyMembership 상태와 가족 역할, 이메일·전화가 없는 구성원 Account 및 초기 자격증명, 가족별 서비스 활성화·중단, 서비스별 ServiceAdmin 지정·회수(자기 자신 포함)를 관리한다. FamilyAdmin이라는 이유만으로 Markpoint 등 개별 서비스의 업무 운영 권한은 자동으로 부여되지 않는다.

ServiceAdmin은 특정 FamilyGroup 안의 특정 서비스 Scope에서만 업무 운영 권한을 가진다. Markpoint ServiceAdmin의 대상 업무는 미션 생성·수정, 완료 승인·반려, 포인트 지급·차감·조정, 레벨·보상 운영 및 서비스 업무 기록 관리다. FamilyAdmin이 Markpoint를 직접 운영하려면 자신의 FamilyMembership에 별도의 Markpoint ServiceAdmin 역할을 받아야 한다.

서비스 관리자 부재가 영구 운영 블로커가 되지 않도록 FamilyAdmin은 자신 또는 다른 활성 FamilyMembership을 ServiceAdmin으로 즉시 지정할 수 있다. 권한 지정·회수는 감사 로그에 기록한다. Family 탈퇴 시 해당 Family의 모든 역할은 종료되고, Membership 정지 시 해당 Family 관리 권한도 중지한다. 마지막 FamilyAdmin 보호 정책을 적용한다. 활성 서비스에 최소 ServiceAdmin이 필요한지와 마지막 ServiceAdmin 제거 시 경고·후임 지정 절차는 서비스별 정책으로 정의한다. 포인트 차감·대량 조정 같은 민감 작업에는 사유 입력 또는 추가 확인을 요구할 수 있다.

FamilyAdmin이나 ServiceAdmin 역할은 다른 FamilyGroup 관리, 구성원의 플랫폼 비밀번호 또는 개인 PIN 열람, 구성원 명의 로그인, 개인 DM 임의 열람, 플랫폼 전체 Account 삭제, 자신의 Service Scope 밖 업무 데이터 변경 권한을 자동으로 부여하지 않는다.

## D5-A — Core Capability and Family Service Entitlement

**Status:** `APPROVED`

몽글 기능은 핵심 플랫폼 기능과 선택형 가족 서비스로 구분한다. Account, FamilyGroup, FamilyMembership, FamilyAdmin 기능, 와글와글 가족 소통, realtime 연결 및 Push는 FamilyGroup 생성과 동시에 기본 제공되는 핵심 플랫폼 기능이다. 와글와글은 `ServiceSubscription`의 부재·비활성화·정지로 사용 또는 Push 수신이 차단되지 않는다.

마크포인트와 향후 **Family-owned 선택 서비스**는 FamilyGroup별 `ServiceSubscription`으로 활성화한다. 이는 현 단계에서 과금 계약이 아니라 “특정 FamilyGroup이 특정 선택 서비스를 사용할 수 있는 상태”를 뜻한다.

**Scope note:** D5-A는 와글와글 Core Capability와 FamilyGroup 소유 선택 서비스의 Entitlement만 정의한다. 모든 선택 서비스를 FamilyGroup 소유 또는 FamilyGroup Subscription으로 처리한다는 뜻이 아니다. 개인형·가족형·혼합형 소유 및 등록 계약은 D5-A1/A2/A3을 따른다. `ServiceSubscription`은 Service Instance나 모든 서비스 소유권의 정본이 아니다.

| State | Meaning | Transition authority |
|---|---|---|
| `INACTIVE` | 해당 가족이 선택 서비스를 사용하지 않음 | D5-A3의 서비스별 정책에 따라 FamilyMember 요청·직접 활성화 또는 FamilyAdmin 활성화 |
| `ACTIVE` | 해당 가족이 선택 서비스를 사용 중 | FamilyAdmin 또는 명시된 서비스 정책에 따라 `INACTIVE`로 전환 |
| `SUSPENDED` | 운영·보안·정책 사유로 플랫폼이 일시 제한 | 플랫폼만 설정·해제 가능 |

서비스 활성화는 서비스 업무 권한을 부여하지 않는다. FamilyAdmin은 활성화·중단의 관리자 권한과 ServiceAdmin 지정·회수를 보유하되, 등록·활성화의 개시 주체는 D5-A3 서비스 정책에 따라 FamilyMember일 수 있다. 실제 서비스 업무는 명시적으로 지정된 ServiceAdmin만 수행한다. `ACTIVE` Subscription만으로 FamilyMember 또는 FamilyAdmin에게 Markpoint 업무 권한이 생기지 않는다.

선택 서비스 비활성화는 플랫폼 로그인, 가족 전환, 와글와글 또는 Push를 차단하지 않는다. 비활성화 시 기존 서비스 기록을 자동 삭제하지 않으며, 재활성화 시 승인된 보존 정책에 따라 재사용할 수 있다. ServiceSubscription과 서비스 데이터는 FamilyGroup별로 격리하고, 특정 서비스의 장애·중단·정지는 다른 몽글 서비스에 영향을 주지 않아야 한다.

## D5-A1 — Service Ownership Scope

**Status:** `APPROVED`

`Service Definition`은 플랫폼이 제공하는 서비스 종류와 정책 정의이며, 지원 Owner Scope, 등록 가능 Actor, 활성화 방식, 기본 접근·관리·보존·Push/Event 정책을 선언할 수 있다. `Service Instance`는 특정 Account 또는 FamilyGroup이 실제 사용하는 논리적 서비스 단위다. 둘은 논리적 계약 용어이며 새 물리 테이블·모델 도입을 뜻하지 않는다.

| Service type | Owner | Human identity | Key boundary |
|---|---|---|---|
| `CORE_FAMILY` | FamilyGroup | FamilyMembership | Family 생성 시 제공, Family 간 소통·데이터 교차 금지 |
| `PERSONAL` | Account | Account | ActiveFamilyContext·가족 탈퇴와 무관, FamilyAdmin 자동 접근 없음 |
| `FAMILY` | FamilyGroup | FamilyMembership | 등록자와 무관하게 FamilyGroup에 데이터 귀속 |
| `PERSONAL_OR_FAMILY` | instance별 Account 또는 FamilyGroup | 해당 Owner Scope의 Account 또는 FamilyMembership | 한 instance는 하나의 명확한 Owner Scope를 가짐 |

개인 서비스와 가족 서비스의 데이터·권한·Push·보존은 섞지 않는다. Owner Scope는 개인→가족 또는 가족→개인으로 묵시 전환되지 않으며, 필요하면 명시적 이전·복제·공유 정책이 필요하다.

## D5-A2 — Service Registration Authority

**Status:** `APPROVED`

`Registrant`(등록·개설·활성화 요청 Actor), `Owner`(Account 또는 FamilyGroup), `User`(접근 가능한 Account 또는 FamilyMembership), `ServiceAdmin`(설정·업무 관리자), `ServicePrincipal`(시스템 이벤트를 발행하는 비인간 주체)은 분리한다. 동일할 수는 있어도 자동으로 동일시하지 않는다.

FamilyMember도 서비스 정책에 따라 개인 서비스를 직접 등록하거나, 가족 서비스 개설을 요청하거나, 허용된 가족 서비스를 직접 개설하거나, 기존 가족 서비스 참여를 요청할 수 있다. 가족 서비스의 Owner는 누가 등록했든 FamilyGroup이고, 등록자 탈퇴·정지·Account 삭제가 서비스나 기존 기록을 자동 삭제하지 않는다. 등록자에게 Owner 또는 ServiceAdmin 권한을 자동 부여할지는 Service Definition 정책으로 결정한다.

## D5-A3 — Family Service Activation Policy Framework

**Status:** `APPROVED`

Family 서비스의 등록·활성화 방식은 Service Definition별로 다음 중 하나를 선언한다.

| Policy | Contract |
|---|---|
| `MEMBER_SELF_ACTIVATE` | 허용된 FamilyMember가 즉시 개설 |
| `MEMBER_REQUEST_ADMIN_APPROVAL` | FamilyMember 요청 후 FamilyAdmin 승인 |
| `FAMILY_ADMIN_ONLY` | FamilyAdmin만 직접 개설·활성화 |
| `AUTO_ENABLE_ON_FAMILY_CREATION` | FamilyGroup 생성 시 자동 제공 |

개별 서비스가 어느 정책을 택하는지는 별도 PM 결정이다. 가족 서비스 접근도 Owner Scope만으로 자동 부여되지 않으며, 서비스 정책에 따라 ACTIVE Membership 기본 접근, 구성원 제외, 명시적 접근 지정, Role/Permission 기반 접근 중 하나를 사용한다. `ServiceAccessBinding`은 이 관계의 논리적 명칭일 뿐 신규 물리 테이블을 확정하지 않는다.

## D5-B — Human Service Identity and Access Policy

**Status:** `APPROVED` — Markpoint access policy

개인 소유 서비스의 인간 Identity 정본은 Account이고, 가족 소유 서비스의 인간 Identity 정본은 FamilyMembership이다. 서비스별 Profile은 부가 데이터이지 새로운 사람 Identity가 아니다.

Markpoint는 `FAMILY` 서비스로 FamilyGroup이 소유하며 FamilyMembership을 인간 Identity로 사용한다. FamilyMember는 FamilyGroup용 Markpoint 개설을 요청할 수 있고, FamilyAdmin은 승인·활성화하거나 직접 활성화할 수 있다. `ServiceSubscription: ACTIVE`와 `FamilyMembership: ACTIVE`이면 기본 MEMBER 접근이 부여되며, 미션·포인트 활동은 선택적이다. 필요한 구성원별 이용 제한만 명시 정책으로 적용한다.

FamilyMember는 자기 미션·포인트·레벨 조회와 허용된 미션 수행을, FamilyAdmin은 활성화·중단·ServiceAdmin 지정·회수와 제한 정책 관리를, 명시적 Markpoint ServiceAdmin은 미션·승인·포인트·레벨·보상 업무를 수행한다. 등록자에게 ServiceAdmin 역할은 자동 부여되지 않는다. 별도 가입·탈퇴 Lifecycle이 없으므로 현 단계에는 `MarkpointParticipant`를 도입하지 않는다.

## D5-C — Machine Service Principal

**Status:** `APPROVED`

Markpoint 자동 알림은 FamilyAdmin, ServiceAdmin 또는 일반 FamilyMember의 명의가 아니라 와글와글의 `마크포인트` 시스템 주체 명의로 표시한다. 기술적으로 이 비인간 주체는 `ServicePrincipal`으로 표현한다. ServicePrincipal은 FamilyMembership·ServiceAdmin·Registrant·Owner를 대체하지 않으며, 사람의 수동 메시지와 자동 알림을 명확히 구분한다.

자동 알림은 원본 이벤트가 발생한 FamilyGroup의 승인된 Wagle 대화방에만 전송하며, FamilyGroup 간 교차 전송은 금지한다. FamilyAdmin이나 등록자의 변경·탈퇴는 시스템 Actor의 동작을 중단시키지 않는다. Markpoint가 비활성화 또는 정지된 FamilyGroup에는 신규 자동 알림을 발행하지 않는다.

각 시스템 메시지는 원본 Markpoint 이벤트와 추적 가능하게 연결되고, 동일 미션·승인·포인트 이벤트가 중복 메시지로 전송되지 않도록 이벤트 식별자와 중복 방지 처리를 요구한다. 기존 `service_principals`와 Wagle binding의 물리적 재사용 적합성은 구현 단계의 검증 항목이지만, 이 승인된 논리 계약을 뒤집는 결정은 아니다.

## D6 — Wagle Realtime, Push and Recovery Contract

**Status:** `APPROVED`

와글와글은 Foreground realtime 전달에 WebSocket, PWA가 닫혔거나 background일 때 알림에 Web Push를 사용한다. 둘은 전달 수단일 뿐 메시지 내용·순서·읽음 상태의 최종 SSOT가 아니다. 서버의 영구 저장 데이터가 SSOT다.

### Storage and delivery semantics

메시지는 수신자 전달 전에 DB에 영구 저장하고, 발행용 Outbox 기록과 같은 Transaction 경계에서 처리한다. 저장 완료 뒤에만 발신자에게 성공을 응답한다. 이후 Realtime/Push 실패는 저장 메시지를 유실시키거나 성공을 되돌리지 않는다. 전달은 `at-least-once`이며, exactly-once를 주장하지 않는다. 모든 메시지·이벤트에는 고유 식별자가 있고 클라이언트와 서버 모두 중복 제거를 지원한다.

`SENT`(서버 저장 완료)와 FamilyMembership의 읽음 상태는 durable contract다. 사용자에게 표시하는 기본 상태 집합은 `PENDING`, `SENT`, `FAILED`, `READ`다. 기기별 수신 확인은 내부 복구·관측 목적으로만 사용하고, **사용자용 `DELIVERED` 표시는 별도 PM 승인 전 도입하지 않는다**. `READ`를 화면에서 어떻게 표현하는지는 D6-P4에서 관련 구현 Task Start Gate 전에 결정한다. 순서는 전역이 아닌 `FamilyGroup + Room` 단위이며, 각 Room은 `room_sequence` 또는 동등한 단조 증가 순서를 가진다. 전역 순서 보장은 요구하지 않으며 구현해서도 안 된다.

### Connection, authorization and isolation

`Account + Device + Session`은 하나의 논리적 realtime 구독 범위를 가진다. 여러 탭·재연결·연결 교체에서는 복수 물리 WebSocket이 일시 존재할 수 있으며, 각각 고유 연결 ID와 서버 Lifecycle/dedup 관리가 필요하다. 논리 구독 범위는 전체 `AuthorizedFamilySet`을 처리하고, ActiveFamilyContext는 다른 활성 FamilyGroup의 realtime/Push를 차단하지 않는다.

Room, 메시지, Participant, Read State, unread count, cursor, retry 및 실패 기록은 FamilyGroup별로 격리한다. Membership 정지·탈퇴·회수는 해당 FamilyGroup 구독만 제거한다. Account 정지, 전체 Session 취소 또는 명시적 로그아웃만 그 Account Session의 전체 realtime/Push 권한을 종료한다.

### Web Push and recovery

Web Push는 보장된 전달 경로나 SSOT가 아닌 빠른 background 알림이다. 누락·지연·중복과 무관하게 앱 실행·재연결 시 서버의 durable history로 누락 메시지와 상태를 복구한다. payload의 본문 공개 수준은 D6-P1에서 구현 Task Start Gate 전에 결정한다. Push open은 Session, Account 상태, FamilyMembership, FamilyGroup Scope, Room Participant 및 Permission을 재검증하고, 권한 상실 시 데이터를 표시하지 않는다. 개인 Wagle PIN 잠금에서도 Push/unread는 유지하되 PIN 확인 전 본문을 노출하지 않는다.

Room별 mute·알림 설정(D6-P2), foreground Push 억제 및 Push 묶음 기준(D6-P3)은 구현 Task Start Gate 전에 결정한다. 어떤 policy를 선택해도 개별 서버 메시지 기록·순서는 보존한다. Push subscription은 Account와 Device/PWA Installation에 연결하며 로그아웃, Account 정지, Session 취소, 기기 연결 해제 또는 Account 전환 시 기존 Account 권한을 폐기한다.

### Resume and idempotency

클라이언트는 마지막 처리 Cursor 또는 Resume Token을 보존한다. 재연결 시 서버는 이후 누락 이벤트를 조회하고 고유 ID로 중복 제거한 뒤 구독을 재개한다. 재연결·서버 재시작·기기 절전·PWA 재실행·Push 누락에도 메시지가 유실되거나 중복 표시되지 않아야 한다.

클라이언트는 전송마다 `client_message_id`를 만들고, 동일 ID 재전송 시 서버는 새 메시지를 만들지 않고 기존 결과를 반환한다. 클라이언트는 최소 `PENDING`, `SENT`, `FAILED` 전송 상태를 표현한다. Outbox, Realtime, Push, retry 및 실패 보존은 이벤트·수신자·기기·FamilyGroup 단위로 격리되어 한 가족/기기/메시지 실패가 다른 정상 전달을 막지 않아야 한다.

### D6 implementation-policy deferrals

**Status:** `DEFERRED_TO_RELEVANT_TASK_START_GATE` / **Decomposition blocking:** `NON_BLOCKING_FOR_DECOMPOSITION`.

No default value is chosen for any row below. Each is decided by PM immediately
before the Start Gate of the implementation task that needs it. A task whose
scope depends on an undecided row must not be promoted to
`READY_FOR_IMPLEMENTATION`; the rest of the D6 core contract and the whole
decomposition proceed regardless. The authoritative register is
`agent-system/active.md`.

| ID | Deferred policy | Blocks at |
|---|---|---|
| D6-P1 | Push 알림 본문 공개 수준 | PWA Push subscription/payload task |
| D6-P2 | Room별 mute 및 알림 설정 | Room 알림 설정 task |
| D6-P3 | Push 묶음(foreground 억제 포함) 기준 | Push dispatch task |
| D6-P4 | 읽음 표시 방식 | Read-state UI task |
| D6-P5 | 온라인 상태·마지막 접속 공개 여부 | Presence task |
| D6-P6 | 메시지 수정·삭제 정책 | Message mutation task |
| D6-P7 | 메시지·시스템 이벤트 보존 기간 | Retention task |
| D6-P8 | 오프라인 발신 Queue의 v1 포함 여부 | Offline outbound queue task |

## D7 — Family-Scoped Route and API Contract

**Status:** `APPROVED`

가족용 기능과 Family-owned 서비스는 URL과 API에서 대상 FamilyGroup Scope를 명시한다. Target route shape의 예는 `/families/{familyId}/wagle`, `/families/{familyId}/markpoint`, `/families/{familyId}/ledger`다. Account-owned 개인 서비스는 FamilyGroup 경로와 분리하며, 예는 `/me/ledger`다. 이 예시는 승인된 Target contract이지 현재 모든 endpoint가 구현됐다는 주장이 아니다.

`ActiveFamilyContext`는 기본 진입·화면 이동 편의 상태일 뿐, 데이터 Owner Scope나 접근 권한을 판정하는 유일한 보안 기준이 아니다. 서버는 URL 또는 client가 전달한 `familyId`를 그대로 신뢰하지 않고 Account Session, FamilyMembership 및 상태, FamilyGroup Scope, ServiceSubscription 또는 Owner Scope, Role/Permission, Room 또는 Resource Owner Scope를 교차 검증한다.

이 계약은 서로 다른 가족 화면의 복수 탭 동시 사용, Push deep-link의 정확한 FamilyGroup 이동, 개인/가족 서비스 구분, 임의 FamilyGroup ID 교차 접근 차단과 ActiveFamilyContext 전환이 다른 탭 범위를 오염시키지 않는 동작을 요구한다.

## D8 — Legacy Data Reset and New Start

**Status:** `APPROVED` — `RESET`

`RESET`은 기존 포인트 잔치 데이터를 신규 몽글 DB로 이관하지 않는다는 뜻이며, 기존 데이터를 즉시 삭제한다는 뜻이 아니다. 신규 시스템 안정화·검수와 PM Legacy Retirement 승인 전에는 별도 백업·읽기 전용 보관이 가능하지만, Legacy는 신규 제품의 운영 데이터 소스나 자동 fallback이 아니다.

신규 Target 계약으로 Account, 플랫폼 아이디·비밀번호, FamilyGroup, FamilyMembership, FamilyAdmin/ServiceAdmin 역할, 플랫폼 Session, 개인 Wagle PIN, Wagle Room/Message/Read State, Markpoint ServiceSubscription, Mission/Approval/Point Ledger/Balance/Level/Reward를 처음부터 생성한다.

기존 `player`/`admin` 자동 Account 변환, 기존 PIN·credential 재사용, 가족관계·역할 자동 Membership 생성, 기존 포인트 잔액의 Opening Balance 반영, 미션·승인·레벨·보상·메시지 이관, 기존 test/fixture/preview 데이터의 신규 운영 데이터 사용은 금지한다. 기존 UI·route·API·인증 방식도 Target 호환 요구사항이 아니다. 기존 사용자는 신규 Account/FamilyGroup을 생성하거나 새로 가족에 참여한다.

기존 Identity/Group-Membership/Markpoint ledger/Mission-Approval history/Chat history migration, backfill 및 reconciliation은 출시 필수 작업에서 `SUPERSEDED_BY_D8_RESET`이다. Reset/Cutover는 빈 Target Schema 검증, seed·fixture 운영 데이터 혼입 방지, 신규 Account/FamilyGroup 생성 검증, 신규 Markpoint 초기 원장 불변식, Legacy 쓰기 중단·접근 통제, Legacy 읽기 전용 백업, 신규 Cutover·검증과 PM 승인 Legacy retirement로 구성한다. Legacy 데이터의 파괴적 삭제는 PM 승인 전 금지한다.

### Service mapping examples

| Service | Type | Owner / human identity | Registrant / activation | Access and admin | Subscription / push | PM status |
|---|---|---|---|---|---|---|
| 와글와글 | `CORE_FAMILY` | FamilyGroup / FamilyMembership | 시스템 제공 / `AUTO_ENABLE_ON_FAMILY_CREATION` | ACTIVE Membership, Family-scoped Room policy | 불필요 / AuthorizedFamilySet family push | APPROVED core contract |
| Markpoint | `FAMILY` | FamilyGroup / FamilyMembership | FamilyMember request → FamilyAdmin approval; FamilyAdmin direct activation | ACTIVE Membership 기본 접근, 명시적 Markpoint ServiceAdmin, 개별 제한 가능 | FamilyGroup entitlement 필요 / Family-scoped | APPROVED |
| 가계부 | `PERSONAL_OR_FAMILY` | 개인: Account; 가족: FamilyGroup / FamilyMembership | Scope별 정책 미결정 | 개인형은 FamilyAdmin 자동 접근 없음; 가족형 공개·Role 정책 미결정 | 개인형은 Account push, 가족형은 Family-scoped push | `DEFERRED_TO_RELEVANT_TASK_START_GATE` — 미래 서비스별 정책 |

가계부 행의 미결정 항목은 D5-A1/A2/A3 공통 프레임워크가 아니라 **해당 서비스 고유 정책**이다. D1–D8을 재개방하지 않으며, 와글와글·마크포인트 계획을 차단하지 않는다.

개인 서비스 Push는 `Account + Device + Session` 대상으로 Family Context 없이 전달되고, 가족 서비스 Push는 권한 있는 FamilyMembership에 `FamilyGroup + Service + Resource` Scope로 전달된다. 양쪽 모두 ActiveFamilyContext 선택 때문에 누락되지 않으며, Push open 시 Owner Scope와 접근 권한을 다시 검증한다. 개인·가족 서비스 장애는 서로의 Push를 차단하지 않는다.

## D1/D3/D4/D6/D7 — Multi-Family Non-Blocking Addendum

**Status:** `APPROVED` — approved multi-family model의 필수 보완 계약.

`ActiveFamilyContext`는 현재 화면의 조회·작성·관리 Scope일 뿐, 전체 권한이나 백그라운드 수신 범위가 아니다. `AuthorizedFamilySet`은 Session Account가 `ACTIVE` FamilyMembership을 가진 모든 FamilyGroup이다. Session은 특정 가족에 종속되지 않으며, Active Context가 없거나 A로 선택돼도 B/C의 Push·관리 알림을 수신한다. 전환은 재로그인·전체 Session 재발급 없이 대상 Membership/Role/Permission/ServiceSubscription만 서버에서 재평가한다.

### Realtime and Push

`Account + Device + Session`당 하나의 realtime connection이 AuthorizedFamilySet의 Family channel set을 다중화한다. 서버가 Session Account, Membership 상태, FamilyGroup, Room ownership, Service Entitlement, Role/Permission을 교차 검증해 구독을 결정한다. 임의 client `family_group_id` 구독은 허용하지 않는다. Membership 승인·탈퇴·정지·권한 회수는 구독 범위를 증분 갱신한다.

각 event는 최소 `event_id`, `family_group_id`, `event_type`, `service_scope`, `room_id 또는 resource_id`, `occurred_at`을 가진다. Push open은 Session과 Membership/Permission을 재검증하고, 허용 시에만 해당 Context로 전환한다. 권한 상실 상태에는 데이터가 아닌 접근 불가 상태를 제공하며 민감한 본문은 Push payload에 과도하게 넣지 않는다.

### Non-blocking and failure isolation

한 가족의 PENDING/SUSPENDED Membership, Room 오류, Outbox 실패, retry 실패는 다른 활성 가족의 접근·Push·전달을 막지 않는다. Family별 Outbox, cursor, read state, unread count, retry/failure record, 권한 변경을 격리한다. Family 수에 제품 의미의 임의 하드 제한을 두지 않는다; pagination/cursor/lazy/incremental sync 및 별도 Capacity Policy는 허용된다.

Family Admin도 모든 활성 FamilyGroup별로 가입 승인, 관리자 이전, 마지막 관리자 위험, 초대 코드, 관리 요청, 서비스 관리자 지정 관련 알림을 독립 수신한다. 한 가족의 admin 권한이 다른 가족 데이터 접근 권한이 되지 않는다.

## New-screen evidence addendum (0a–0g)

**Axis:** `CURRENT IMPLEMENTATION` / UI evidence. See
`MONGLE_NEW_SCREENS_CONTRACT_IMPACT_REVIEW.md` for full detail.

D1–D8 are `APPROVED` and are **not** reopened by anything in this section. What
remains open here is **screen-level and API-level detail that D1–D8 never
covered** — not the decisions themselves. Each item below is
`DEFERRED_TO_RELEVANT_TASK_START_GATE` for the named UI task in the
Implementation Backlog.

- **D1 (approved: family platform, `family_groups`/`family_memberships`):**
  the new screens are consistent family-framed UI evidence. 0g's group
  search/discovery surface raises a **new screen-level privacy question** D1
  does not answer — public directory vs. invite-only/contact-scoped discovery.
  Deferred to `MONGLE-W1-GROUP-DISCOVERY-UI-001`'s Start Gate.
- **D2 (approved: `아이디 + 플랫폼 비밀번호`; email/phone not required;
  FamilyAdmin may provision Accounts):** 0b's four signup affordances
  (email+password, phone+SMS, Google, Apple) are **additional optional
  credential surfaces beyond the approved baseline**, not alternatives to it.
  Each still needs its own `V1_REQUIRED`/`V1_OPTIONAL`/`DEFERRED`/
  `REFERENCE_ONLY` call at `MONGLE-W1-ACCOUNT-SIGNUP-UI-001`'s Start Gate.
- **D3 (approved: persistent Account-scoped Session; optional Account+Device
  Wagle PIN):** the 0b→0c split and 0f are concrete UI evidence for the
  no-active-membership and pending-membership session states. Screen behaviour
  for those states is deferred to the relevant W1 UI tasks.
- **D4 (approved: FamilyAdmin/ServiceAdmin separation, last-admin protection):**
  0d's "creator self-selects 자녀 as their own relationship while being the
  group's sole creating member" is a **relationship-vs-role edge case** — the
  creator still receives FamilyAdmin per D4; the open question is only the UI
  copy and confirmation flow. Invite-code issuance and join-approval authority
  detail is deferred to the 0e/0f/0g UI tasks.
- **D7 (approved: `/families/{familyId}/...` vs `/me/...`, server-side
  revalidation):** the exact paths `/onboarding/*`, `/signup`, `/groups`,
  `/groups/new`, `/groups/join`, `/groups/discover`, `/groups/pending` and
  their API operations are **not** fixed by D7 — pre-login and pre-family
  routes precede family scope by definition. These remain candidate shapes for
  the W1 UI tasks to specify; D7 governs family-scoped routes only.
