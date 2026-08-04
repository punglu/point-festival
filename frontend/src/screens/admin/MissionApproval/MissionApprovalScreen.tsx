import styles from './MissionApprovalScreen.module.css';
import type { MissionApprovalProps } from './types';

export function MissionApprovalScreen({ model, embedded, onApprove, onReject, onClose }: MissionApprovalProps) {
  return (
    <main className={`${styles.page} ${embedded ? styles.embedded : ''}`} data-canonical-screen-id="1m">
      {!embedded && (
        <aside>
          <div className={styles.brand}>몽글<b>우리 가족</b><span>관리자 모드</span></div>
          {['대시보드', '미션 관리', '포인트 관리', '사용자 관리', '알림 관리', '설정'].map((name, index) => (
            <button type="button" key={name} className={index === 1 ? styles.active : ''}>○ <span>{name}</span></button>
          ))}
          <footer><i>관</i><div><b>관리자</b><span>admin@ourfamily.com</span></div></footer>
        </aside>
      )}
      <section className={styles.main}>
        <header>
          <div>
            <h1>미션 승인 대기함</h1>
            <p>아이들이 제출한 완료 인증을 확인하고 승인해 주세요.</p>
          </div>
          <div className={styles.headerRight}>
            <strong>◷ 승인 대기 {model.pendingCount}건</strong>
            {embedded && <button type="button" className={styles.close} aria-label="닫기" onClick={onClose}>×</button>}
          </div>
        </header>
        <div className={styles.stats}>
          {[
            ['승인 대기', `${model.pendingCount}건`],
            ['오늘 승인', `${model.approvedTodayCount}건`],
            ['오늘 반려', `${model.rejectedTodayCount}건`],
            ['지급 예정 포인트', `${model.pendingPoints}P`],
          ].map(([label, value]) => (
            <div key={label}><span>{label}</span><b>{value}</b></div>
          ))}
        </div>
        <section className={styles.list}>
          <h2>승인 대기 미션</h2>
          {model.items.length === 0 ? (
            <p className={styles.empty}>승인 대기 중인 미션이 없어요.</p>
          ) : (
            model.items.map((item) => (
              <article key={item.id}>
                <i>{item.playerName}</i>
                <div className={styles.photo}>인증사진</div>
                <div><h3>{item.title}</h3><p>{item.playerName} · {item.meta}</p></div>
                <button type="button" onClick={() => onReject?.(item.id)}>반려</button>
                <button type="button" className={styles.approve} onClick={() => onApprove?.(item.id)}>승인</button>
              </article>
            ))
          )}
        </section>
      </section>
    </main>
  );
}
