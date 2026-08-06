import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from '../pages/PlatformPages.module.css';

export function AccessBoundary({
  permission,
  children,
  allowFamilySelection = false,
}: {
  permission?: string;
  children: ReactNode;
  /**
   * MONGLE-W7-4-MULTI-FAMILY-ACTIVEFAMILY-PERSISTENCE-REMEDIATION-001.
   *
   * `FamilyLandingPage` is the *only* screen a multi-family Account can use
   * to create its first active-Family selection. Wrapping it in this same
   * boundary's default "no active Family yet" gate made that screen require
   * the very thing it exists to produce -- a deadlock with no way out: the
   * gate's own "가족 선택하기" link points back at `/family`, which would
   * show the identical gate again. `FamilyLanding` already implements its
   * own correct `activeFamilyId === null` state (the actual family-picker
   * list), so this flag lets that boundary consumer opt out of the generic
   * gate and reach its children immediately. No other consumer sets this;
   * every other screen (e.g. `/markpoint`) still correctly requires an
   * already-active Family before rendering anything.
   */
  allowFamilySelection?: boolean;
}) {
  const status = useFamilyContextStore((state) => state.status);
  const can = useFamilyContextStore((state) => state.can);
  const activeFamilyId = useFamilyContextStore((state) => state.activeFamilyId);

  if (status === 'loading' || status === 'idle') {
    return <section className={styles.page} role="status"><h1>몽글을 준비하고 있어요</h1><p>가족과 권한 정보를 확인하는 중입니다.</p></section>;
  }
  if (activeFamilyId === null && !allowFamilySelection) {
    // A dead end without the link: a multi-family account legitimately has no
    // active family until it picks one, and this screen used to say "choose a
    // family" while offering no way to do it.
    return (
      <section className={styles.page} role="alert">
        <h1>가족을 선택해주세요</h1>
        <p>활성 가족을 선택한 뒤 이 화면을 열 수 있습니다.</p>
        <Link to="/family" data-testid="go-select-family">가족 선택하기</Link>
      </section>
    );
  }
  // A permission is meaningless before any Family is active -- `can()` would
  // just report false for every permission with no Family to check it
  // against, which would surface as an incorrect "권한이 없어요" instead of
  // the actual picker. Once a Family *is* active, the permission check still
  // applies exactly as before.
  if (permission && activeFamilyId !== null && !can(permission)) {
    return <section className={styles.page} role="alert"><h1>권한이 없어요</h1><p>이 화면은 현재 가족에서 허용된 구성원만 사용할 수 있습니다.</p></section>;
  }
  return <>{children}</>;
}
