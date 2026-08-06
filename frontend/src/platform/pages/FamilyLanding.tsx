/**
 * 가족 홈 — the Family service hub.
 *
 * MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001 replaced a 15-line placeholder
 * that said member management "will be provided in a later step". Every
 * capability it deferred now exists on the backend, so the screen reads the
 * server-derived account context and shows what this account can actually do.
 *
 * Three distinctions it refuses to blur, each of which has already caused a
 * real defect on this project:
 *
 * - **Family admin is not service admin.** Holding `family.*` says nothing
 *   about Markpoint. The service-admin badge is driven only by the Markpoint
 *   permissions, which no FAMILY-scope role carries (migration `0006`).
 * - **A subscription that is not `active` means unavailable**, and the card
 *   says so instead of offering an entry point that would 403.
 * - **Losing one family is not a logout.** Every authorized family stays
 *   listed and switchable; the active one is a UI choice, not an authority.
 */
import { Link } from 'react-router-dom';

import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import { AccessBoundary } from '../access/AccessBoundary';
import { FamilyHomeContainer } from './FamilyHomeContainer';
import styles from './FamilyLanding.module.css';

const RELATIONSHIP_LABEL: Record<string, string> = {
  parent: '부모',
  child: '자녀',
  guardian: '보호자',
  sibling: '형제자매',
  other: '기타',
  unknown: '미확인',
};

function ServiceCard({
  name,
  status,
  to,
  description,
  testId,
}: {
  name: string;
  status: string;
  to: string;
  description: string;
  testId: string;
}) {
  const available = status === 'active';
  return (
    <article className={styles.serviceCard} data-testid={testId} data-status={status}>
      <div className={styles.serviceHead}>
        <h3 className={styles.serviceName}>{name}</h3>
        <span className={`${styles.statusPill} ${available ? styles.on : styles.off}`}>
          {available ? '이용 가능' : '이용 불가'}
        </span>
      </div>
      <p className={styles.muted}>{description}</p>
      {available ? (
        <Link className={styles.enter} to={to} data-testid={`${testId}-enter`}>
          들어가기
        </Link>
      ) : (
        // No entry point when the service is not active — offering one and
        // letting the server refuse would just move the failure later.
        <p className={styles.unavailableNote}>가족의 서비스 상태를 확인한 뒤 다시 시도해주세요.</p>
      )}
    </article>
  );
}

export function FamilyLanding() {
  const context = useFamilyContextStore((s) => s.context);
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const selectFamily = useFamilyContextStore((s) => s.selectFamily);
  const serviceStatus = useFamilyContextStore((s) => s.serviceStatus);
  const can = useFamilyContextStore((s) => s.can);

  const family = context?.families.find((item) => item.id === activeFamilyId);
  const families = context?.families ?? [];

  if (!family) {
    // No active selection yet. This is the **normal** state for an account in
    // more than one family: the store deliberately auto-selects only when
    // there is exactly one, because guessing which family someone meant is
    // worse than asking.
    //
    // The selector must therefore live here too. An earlier revision of this
    // screen returned a bare "가족을 선택해주세요" with no list, which made a
    // multi-family account a dead end — the one case this Wave exists for.
    // Caught by Journey 1.
    return (
      <section className={styles.page} aria-labelledby="family-select-title">
        <header className={styles.header}>
          <p className={styles.eyebrow}>몽글 가족</p>
          <h1 id="family-select-title">가족을 선택해주세요</h1>
          <p className={styles.muted}>
            {families.length > 0
              ? '이용할 가족을 선택하면 서비스가 열립니다.'
              : '참여 중인 가족이 없습니다.'}
          </p>
        </header>
        {families.length > 0 && (
          <ul className={styles.familyList} data-testid="family-list">
            {families.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={styles.familyItem}
                  onClick={() => selectFamily(item.id)}
                  data-testid={`family-switch-${item.id}`}
                >
                  <span className={styles.familyItemName}>{item.name}</span>
                  <span className={styles.familyItemMeta}>
                    {item.services.filter((s) => s.status === 'active').length}개 서비스 이용 가능
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
        {families.length === 0 && (
          <Link to="/onboarding" className={styles.createFamilyLink} data-testid="go-onboarding">
            가족 만들기
          </Link>
        )}
      </section>
    );
  }

  const isFamilyAdmin = can('family.members.manage');
  const isMarkpointAdmin = can('markpoint.missions.manage') || can('markpoint.points.adjust');

  return (
    <section className={styles.page} aria-labelledby="family-title">
      <FamilyHomeContainer familyId={family.id} familyName={family.name} />

      <header className={styles.header}>
        <p className={styles.eyebrow}>몽글 가족</p>
        <h1 id="family-title" data-testid="family-name">
          {family.name}
        </h1>
        <p className={styles.muted}>
          내 역할:{' '}
          {RELATIONSHIP_LABEL[family.membership.relationship] ?? family.membership.relationship}
        </p>
        <div className={styles.badges}>
          {isFamilyAdmin && <span className={styles.badge}>가족 관리자</span>}
          {/* Deliberately a separate badge from the family one above: the two
              are different authorities, and showing one for the other is
              exactly the D4 violation this project already had to migrate out. */}
          {isMarkpointAdmin && (
            <span
              className={`${styles.badge} ${styles.serviceBadge}`}
              data-testid="service-admin-badge"
            >
              마크포인트 서비스 관리자
            </span>
          )}
        </div>
      </header>

      {families.length > 1 && (
        <section className={styles.block} aria-labelledby="family-switch">
          <h2 id="family-switch">내 가족</h2>
          <ul className={styles.familyList} data-testid="family-list">
            {families.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={`${styles.familyItem} ${item.id === activeFamilyId ? styles.familyActive : ''}`}
                  onClick={() => selectFamily(item.id)}
                  aria-current={item.id === activeFamilyId ? 'true' : undefined}
                  data-testid={`family-switch-${item.id}`}
                >
                  <span className={styles.familyItemName}>{item.name}</span>
                  <span className={styles.familyItemMeta}>
                    {item.services.filter((s) => s.status === 'active').length}개 서비스 이용 가능
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className={styles.block} aria-labelledby="family-services">
        <h2 id="family-services">서비스</h2>
        <div className={styles.services}>
          <ServiceCard
            name="마크포인트"
            status={serviceStatus('markpoint')}
            to="/markpoint"
            description="미션을 완료하고 포인트와 레벨을 쌓아요."
            testId="service-markpoint"
          />
          <ServiceCard
            name="와글와글"
            status={serviceStatus('wagle')}
            to="/wagle"
            description="가족과 서비스 소식을 한곳에서 나눠요."
            testId="service-wagle"
          />
        </div>
      </section>

      <section className={styles.block} aria-labelledby="family-features">
        <h2 id="family-features">가족 기능</h2>
        <div className={styles.services}>
          <Link to="/family/schedule" className={styles.featureLink} data-testid="feature-schedule">가족 일정</Link>
          <Link to="/family/album" className={styles.featureLink} data-testid="feature-album">앨범</Link>
          <Link to="/family/todo" className={styles.featureLink} data-testid="feature-todo">할 일</Link>
          <Link to="/family/members" className={styles.featureLink} data-testid="feature-members">가족 구성원</Link>
          <Link to="/family/notifications" className={styles.featureLink} data-testid="feature-notifications">알림</Link>
          <Link to="/family/rules" className={styles.featureLink} data-testid="feature-rules">가족 규칙</Link>
          <Link to="/family/search" className={styles.featureLink} data-testid="feature-search">검색</Link>
        </div>
      </section>

      <section className={styles.block} aria-labelledby="family-permissions">
        <h2 id="family-permissions">내 권한</h2>
        {family.permissions.length === 0 ? (
          <p className={styles.muted}>부여된 권한이 없습니다.</p>
        ) : (
          <ul className={styles.permissionList} data-testid="family-permissions">
            {family.permissions.map((permission) => (
              <li key={permission} className={styles.permission}>
                {permission}
              </li>
            ))}
          </ul>
        )}
      </section>
    </section>
  );
}

/** Route entry point (`/family`). `family.read` matches the same permission
 *  MongleAppShell already gates the nav link on — a member linked to this
 *  family only through another service (e.g. Markpoint) reaches the shared
 *  AccessBoundary "권한이 없어요" state instead of this screen once a Family
 *  is active. `allowFamilySelection`: this is the one screen responsible for
 *  producing that first selection, so it must stay reachable with none yet
 *  active — see AccessBoundary's own doc on the flag. */
export function FamilyLandingPage() {
  return (
    <AccessBoundary permission="family.read" allowFamilySelection>
      <FamilyLanding />
    </AccessBoundary>
  );
}
