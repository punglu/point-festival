import type { ReactNode } from 'react';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from '../pages/PlatformPages.module.css';

export function AccessBoundary({ permission, children }: { permission?: string; children: ReactNode }) {
  const status = useFamilyContextStore((state) => state.status);
  const can = useFamilyContextStore((state) => state.can);
  const activeFamilyId = useFamilyContextStore((state) => state.activeFamilyId);

  if (status === 'loading' || status === 'idle') {
    return <section className={styles.page} role="status"><h1>나란을 준비하고 있어요</h1><p>가족과 권한 정보를 확인하는 중입니다.</p></section>;
  }
  if (activeFamilyId === null) {
    return <section className={styles.page} role="alert"><h1>가족을 선택해주세요</h1><p>활성 가족을 선택한 뒤 이 화면을 열 수 있습니다.</p></section>;
  }
  if (permission && !can(permission)) {
    return <section className={styles.page} role="alert"><h1>권한이 없어요</h1><p>이 화면은 현재 가족에서 허용된 구성원만 사용할 수 있습니다.</p></section>;
  }
  return <>{children}</>;
}
