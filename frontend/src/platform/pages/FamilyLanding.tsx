import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './PlatformPages.module.css';

export function FamilyLanding() {
  const family = useFamilyContextStore((state) => state.context?.families.find((item) => item.id === state.activeFamilyId));
  if (!family) return <section className={styles.page}><h1>가족을 선택해주세요</h1><p>활성 가족을 선택하면 가족 기능을 이용할 수 있습니다.</p></section>;
  return (
    <section className={styles.page} aria-labelledby="family-title">
      <p className={styles.eyebrow}>나란 가족</p>
      <h1 id="family-title">{family.name}</h1>
      <p>{family.membership.relationship === 'unknown' ? '관계 정보 검토가 필요합니다.' : `관계: ${family.membership.relationship}`}</p>
      <p className={styles.muted}>가족 구성원 관리 화면은 권한과 서비스 계약이 확정되는 다음 단계에서 제공합니다.</p>
    </section>
  );
}
