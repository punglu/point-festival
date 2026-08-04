import styles from './MissionManagementScreen.module.css';
import { AdminDataGrid } from './components/AdminDataGrid';
import type { MissionManagementFilterStatus, MissionManagementProps } from './types';

const FILTERS: { status: MissionManagementFilterStatus; label: string }[] = [
  { status: 'all', label: '전체' },
  { status: 'active', label: '활성' },
  { status: 'completed', label: '완료' },
];

export function MissionManagementScreen({
  model,
  embedded,
  weekGridSlot,
  proposedSlot,
  onSelectPlayer,
  onSelectDate,
  onFilterStatus,
  onSearch,
  onOpenImport,
  onOpenAdd,
  onOpenTemplates,
  onBulkApprove,
}: MissionManagementProps) {
  return (
    <main className={`${styles.page} ${embedded ? styles.embedded : ''}`} data-canonical-screen-id="2e" data-canonical-screen-label="미션 관리" data-canonical-source="wave7-full-authority">
      {!embedded && (
        <aside>
          <b>몽글</b>
          {['대시보드', '미션 관리', '포인트 관리', '사용자 관리', '알림 관리', '설정'].map((name, index) => (
            <button key={name} type="button" className={index === 1 ? styles.active : ''}>○ <span>{name}</span></button>
          ))}
        </aside>
      )}
      <section className={styles.main}>
        <header>
          <div><h1>미션 목록 관리</h1><p>가족 미션을 만들고 관리할 수 있어요.</p></div>
          <button type="button" onClick={onOpenAdd}>＋ 미션 추가</button>
        </header>

        <div className={styles.stats}>
          {model.stats.map((s) => (
            <article key={s.label}><span>{s.label}</span><b>{s.value}</b></article>
          ))}
        </div>

        {weekGridSlot && <div className={styles.weekGridWrap}>{weekGridSlot}</div>}

        <div className={styles.actionBar}>
          <select
            value={model.selectedPlayerId ?? 'all'}
            onChange={(e) => onSelectPlayer?.(e.target.value === 'all' ? null : Number(e.target.value))}
          >
            <option value="all">전체 플레이어</option>
            {model.playerOptions.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <input type="date" value={model.selectedDate} onChange={(e) => onSelectDate?.(e.target.value)} />
          <button type="button" className={styles.actionBtn} onClick={onOpenImport}>📥 과거 미션 가져오기</button>
          <button type="button" className={styles.actionBtn} onClick={onOpenTemplates}>🔄 반복미션 관리</button>
        </div>

        {proposedSlot}

        {model.canBulkApprove && (
          <div className={styles.bulkApproveBar}>
            <button type="button" className={styles.bulkApproveBtn} onClick={onBulkApprove}>전체 승인</button>
          </div>
        )}

        <section className={styles.table}>
          <div className={styles.filters}>
            {FILTERS.map((f) => (
              <button
                key={f.status}
                type="button"
                className={model.filterStatus === f.status ? styles.filterActive : ''}
                onClick={() => onFilterStatus?.(f.status)}
              >
                {f.label}
              </button>
            ))}
            <input
              placeholder="미션 검색"
              value={model.searchQuery}
              onChange={(e) => onSearch?.(e.target.value)}
            />
          </div>
          <div className={styles.gridArea}>
            <AdminDataGrid
              rows={model.rows}
              rowKey={(row) => row.id}
              renderRow={(row) => row.content}
              loading={model.loading}
              emptyLabel="조건에 맞는 미션이 없어요."
            />
          </div>
        </section>
      </section>
    </main>
  );
}
