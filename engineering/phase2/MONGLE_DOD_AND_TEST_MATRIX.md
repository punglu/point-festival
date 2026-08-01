# Definition of Done and Test Matrix

> Recalculated against `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED` /
> `FROZEN`, 2026-08-01). Rows below are **required contract coverage**, not
> claims that any test exists or passes today. Tests follow
> `agent-system/qa/TEST_POLICY.md`: run the relevant existing test first, add
> only the minimum test for an otherwise unprotected flow, and report actual
> PASS plus a Coverage Map update, or a `BLOCKED` reason.

## Test classes

| Test class | Purpose | In the Target coverage denominator? |
|---|---|---|
| `TARGET_PRODUCT` | protect an approved Target contract | **Yes** |
| `MIGRATION_GUARD` | protect the approved D8 Reset/Cutover boundary | **Yes** |
| `LEGACY_REFERENCE` | understand legacy behaviour only | No |
| `RETIREMENT_GUARD` | protect against regression in legacy behaviour that must survive **until** retirement | No — tracked separately, retired with Legacy |

A legacy behaviour test is never Target coverage. Where legacy regression
protection is genuinely needed before retirement, classify it
`LEGACY_REFERENCE` or `RETIREMENT_GUARD`, never `TARGET_PRODUCT`. No legacy test
is retired without approved supersession and equal-or-stronger Target coverage.

## Target coverage denominator

Every axis below is required Target coverage derived from a frozen decision.

| # | Coverage axis | Class | Frozen basis |
|---|---|---|---|
| 1 | Account credential login, failure, session issuance, revoke, device unlink | TARGET_PRODUCT | D2, D3 |
| 2 | FamilyAdmin account-issuance boundaries — own family only, independent Account, no credential/PIN read, no impersonation | TARGET_PRODUCT | D2, D4 |
| 3 | Multi-family membership and `ActiveFamilyContext` vs `AuthorizedFamilySet` separation | TARGET_PRODUCT | D1, D3 |
| 4 | Cross-family access deny, including substituted `familyId` and revoked-membership stale routes | TARGET_PRODUCT | D1, D7 |
| 5 | FamilyAdmin / ServiceAdmin separation, default deny, last-admin protection, role-change audit | TARGET_PRODUCT | D4 |
| 6 | Personal vs family service ownership isolation, including FamilyAdmin denied on a personal service | TARGET_PRODUCT | D5-A1, D5-A2 |
| 7 | Markpoint request, approval, direct activation, default access, explicit restriction, registrant-not-admin | TARGET_PRODUCT | D5-A3, D5-B |
| 8 | Durable message DB + Outbox atomicity in one transaction | TARGET_PRODUCT | D6 |
| 9 | Send idempotency — same `client_message_id` returns the existing result | TARGET_PRODUCT | D6 |
| 10 | Room-scoped ordering and cursor recovery, with no global-ordering assumption | TARGET_PRODUCT | D6 |
| 11 | Multi-tab and reconnect duplicate suppression across multiple physical sockets | TARGET_PRODUCT | D6 |
| 12 | PWA Push subscription and revocation on logout, suspension, Session revoke, device unlink, Account switch | TARGET_PRODUCT | D3, D6 |
| 13 | Push miss, delay or duplication → full recovery from durable history | TARGET_PRODUCT | D6 |
| 14 | Push deep-link reauthorization before any data is shown | TARGET_PRODUCT | D6, D7 |
| 15 | PIN-locked privacy — Push and unread continue, sensitive body hidden, other services unaffected | TARGET_PRODUCT | D3-PIN-SCOPE |
| 16 | One-family failure isolation across Outbox, cursor, retry and delivery | TARGET_PRODUCT | D1, D6 |
| 17 | Markpoint `ServicePrincipal` relay — correct actor, family/room binding, dedup, traceability, inactive/suspended deny | TARGET_PRODUCT | D5-C |
| 18 | New Markpoint ledger initial invariants with no legacy opening balance | TARGET_PRODUCT + MIGRATION_GUARD | D5-B, D8 |
| 19 | No Legacy, test, fixture or preview data contamination of operational data | MIGRATION_GUARD | D8 |
| 20 | Fresh cutover, empty-schema start and read-only Legacy archive | MIGRATION_GUARD | D8 |

## Required Target journeys

**D1/D7 multi-family:** an Account with three active families receives family
B's message and family C's admin notification while viewing family A; a Push
deep-link revalidates and only then switches context; a pending or suspended
membership in B or C never blocks A; arbitrary family subscription is denied;
one logical connection multiplexes authorized channels; membership approval and
revocation update subscriptions incrementally; per-family unread and read cursor
persist independently; a B Outbox failure does not stop A or C delivery;
reconnect resumes each family without duplicates; two tabs may use different
authorized family URLs without `ActiveFamilyContext` cross-tab leakage;
substituting an arbitrary `familyId` is denied; `/me/...` personal data stays
separate from `/families/{familyId}/...` data.

**D2/D3/D4 identity:** a new Account is created and logs in with 아이디 +
플랫폼 비밀번호 with no legacy identity involved; a FamilyAdmin provisions an
independent Account inside its own family and is denied outside it; a
FamilyAdmin cannot read a member's password or PIN or act as them; a Session
survives PWA restart and still honours expiry, refresh, revoke and device
unlink; a revoked Session loses Push authority; a FamilyAdmin holds no automatic
Markpoint work authority until explicitly assigned ServiceAdmin; the last
FamilyAdmin cannot be removed unprotected; role changes are audited.

**D5 service ownership:** a personal service is registered and used with no
family selected and survives family switch and leave; a FamilyAdmin is denied
access to a member's personal service; a FamilyMember requests a family service
and a FamilyAdmin approves or rejects it, with the registrant gaining no
automatic Owner or Admin rights; `MEMBER_SELF_ACTIVATE` permits immediate
creation while `FAMILY_ADMIN_ONLY` denies an ordinary member; a registrar
leaving or being suspended leaves FamilyGroup-owned records intact for other
authorized users; a ServiceAdmin change preserves the service and its history
while re-evaluating scope; an `ACTIVE` Markpoint gives every `ACTIVE` membership
default access **without forcing mission participation**, and an explicit
per-member restriction is honoured.

**D6 messaging:** the message row and its Outbox row commit atomically before
`SENT` is reported, and a forced post-persist failure leaves no divergence; an
idempotent retry with the same `client_message_id` returns the existing result;
delivery is at-least-once with client and server deduplication; sequence is
monotonic per `FamilyGroup + Room`; Web Push loss or duplication is recovered
from durable history; a PIN-locked device hides message content while keeping
Push and unread; logout, revoke or device disconnect removes Push authority;
reconnect resumes from the cursor with no loss and no duplicate display; a
family or device Outbox or Push failure does not block another scope; user-facing
status is limited to `PENDING`, `SENT`, `FAILED`, `READ` with **no `DELIVERED`**.

**D8 reset and cutover:** the Target schema contains no legacy Player or Admin
import; new Account, FamilyGroup, FamilyMembership and Markpoint subscription
records are created only through Target flows; the point ledger opens without a
legacy balance; legacy PIN, message, fixture and preview data cannot become
Target operational data; legacy writes are frozen and access-controlled before
cutover; retained Legacy is read-only; no automatic Legacy fallback occurs;
destructive Legacy retirement happens only under explicit PM approval after
Target journey verification.

## Definition of Done per vertical slice

1. Frozen decision dependencies named, and any `D6-P*` or service-specific policy actually decided rather than assumed.
2. Server-side authorization on every operation, with default deny and cross-family denial verified.
3. Transaction and event behaviour verified where applicable — atomicity, idempotency, ordering scope, dedup.
4. FE state, error, empty and accessibility behaviour real, with no invented data where an API field is absent.
5. Migration safety and rollback stated where a migration is involved; migrations are single-writer.
6. The relevant existing test run first, plus the minimum new test for an otherwise unprotected flow.
7. Coverage Map updated.
8. **Actual execution evidence** — a reported PASS must be a real run, and a blocked run is reported as `BLOCKED` with its reason rather than as a pass.

## Deferred and evidence-only coverage

**`D6-P`-dependent coverage** — read display (`D6-P4`), mute and notification
settings (`D6-P2`), Push bundling and foreground suppression (`D6-P3`), Push
payload disclosure (`D6-P1`), presence (`D6-P5`), message edit/delete (`D6-P6`),
retention (`D6-P7`) and the offline outbound queue (`D6-P8`) — is
`DEFERRED_TO_RELEVANT_TASK_START_GATE`. It enters the denominator only when its
policy is decided, and it is not counted as a gap in the meantime.

**New-screen journeys (0a–0g evidence).** Implied `TARGET_PRODUCT` examples from
the 9 new screens, listed as required future coverage and **not** a coverage
claim: onboarding complete; signup success; signup failure; external-identity
signup cancelled; duplicate identity or verification; post-signup no-family
state; single-family auto selection; multi-family selection; family creation;
duplicate family name; valid-code join; invalid code; expired code;
already-a-member; family discovery; join-request creation; approval pending;
approval granted; join rejected; join-request cancelled; cross-family access
denied; unauthorized-approval attempt. The D1–D4/D7 contracts these rest on are
approved; what remains open is screen-level detail (discovery privacy, optional
additional signup surfaces, membership state-machine edges) at the owning UI
task's Start Gate.

**Future-service journeys.** Personal and family 가계부 instance isolation, and
any other not-yet-approved service's activation, access, visibility, admin and
retention journeys, are required contract rows that enter the denominator only
once that service's policy is approved.
