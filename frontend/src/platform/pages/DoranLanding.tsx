import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './PlatformPages.module.css';

export function DoranLanding() {
  const family = useFamilyContextStore((state) => state.context?.families.find((item) => item.id === state.activeFamilyId));
  const status = family?.services.find((service) => service.service_code === 'doran')?.status ?? 'unavailable';
  return (
    <section className={styles.page} aria-labelledby="doran-title">
      <p className={styles.eyebrow}>나란 서비스</p>
      <h1 id="doran-title">도란</h1>
      <p>가족 대화 서비스는 준비 중입니다. 아직 메시지나 대화방 기능은 제공하지 않습니다.</p>
      <span className={styles.badge}>{status === 'active' ? '서비스 준비 중' : '현재 사용할 수 없음'}</span>
    </section>
  );
}
