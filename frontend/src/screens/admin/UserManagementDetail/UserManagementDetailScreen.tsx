import styles from './UserManagementDetailScreen.module.css';
import type { UserManagementDetailProps } from './types';

export function UserManagementDetailScreen({ model, embedded, onClose, onToggleLock }: UserManagementDetailProps) {
  return (
    <main className={`${styles.page} ${embedded ? styles.embedded : ''}`} data-canonical-screen-id="2a">
      {!embedded && (
        <aside>
          <b>몽글</b>
          {['대시보드', '미션 관리', '포인트 관리', '사용자 관리', '알림 관리', '설정'].map((name, index) => (
            <button type="button" key={name} className={index === 3 ? styles.active : ''}>○ <span>{name}</span></button>
          ))}
        </aside>
      )}
      <section className={styles.main}>
        <header>
          <div><span>사용자 관리</span><h1>{model.name} 사용자 상세</h1></div>
          {embedded && <button type="button" className={styles.close} aria-label="닫기" onClick={onClose}>×</button>}
        </header>
        <article className={styles.profile}>
          <i>{model.name.charAt(0)}</i>
          <div>
            <h2>{model.name}</h2>
            <span>{model.roleLabel} · {model.levelLabel}</span>
            <p>가입일 {model.joinedLabel} · 마지막 활동 {model.lastActiveLabel}</p>
          </div>
          <strong>{model.isActive ? '활성' : '비활성'}</strong>
        </article>
        <div className={styles.stats}>
          {[
            ['보유 포인트', model.pointsLabel],
            ['누적 획득', model.totalEarnedLabel],
            ['완료 미션', model.completedMissionsLabel],
            ['교환 횟수', model.redeemCountLabel],
          ].map(([label, value]) => (
            <article key={label}><span>{label}</span><b>{value}</b></article>
          ))}
        </div>
        <section className={styles.cards}>
          <article>
            <h2>최근 미션</h2>
            {model.recentMissions.length === 0 ? (
              <p className={styles.empty}>최근 미션이 없어요.</p>
            ) : (
              model.recentMissions.map((m, index) => (
                <div key={`${m.name}-${index}`}><span>{m.name}</span><b>{m.status}</b></div>
              ))
            )}
          </article>
          <article>
            <h2>권한 및 설정</h2>
            <div><span>PIN 상태</span><b>{model.pinStatusLabel}</b></div>
            <div><span>알림</span><b>{model.notificationLabel}</b></div>
            <div><span>보호자 승인</span><b>{model.guardianApprovalLabel}</b></div>
          </article>
        </section>
        <button className={styles.remove} type="button" onClick={onToggleLock}>
          {model.isActive ? '사용자 비활성화' : '사용자 활성화'}
        </button>
      </section>
    </main>
  );
}
