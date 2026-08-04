import { useState } from 'react';
import styles from './MissionStatisticsFilterScreen.module.css';
import type { MissionStatisticsFilterProps, MissionStatisticsFilterStatus } from './types';

const STATUSES: MissionStatisticsFilterStatus[] = ['전체', '완료', '진행 중'];

export function MissionStatisticsFilterScreen({ players = [], value, onApply, onClose }: MissionStatisticsFilterProps) {
  const [playerId, setPlayerId] = useState<number | null>(value?.playerId ?? null);
  const [status, setStatus] = useState<MissionStatisticsFilterStatus>(value?.status ?? '전체');

  return (
    <main className={styles.screen} data-canonical-screen-id="3b" data-canonical-screen-label="미션 통계 필터" data-canonical-source="wave7-full-authority">
      <section>
        <header><h1>통계 필터</h1><button onClick={onClose} type="button">×</button></header>
        <label>기간<select defaultValue="최근 30일" disabled><option>최근 30일</option></select></label>
        <label>
          가족 구성원
          <select
            value={playerId ?? ''}
            onChange={(e) => setPlayerId(e.target.value === '' ? null : Number(e.target.value))}
          >
            <option value="">전체 가족</option>
            {players.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
        <label>
          미션 상태
          <div>
            {STATUSES.map((s) => (
              <button
                key={s}
                type="button"
                className={s === status ? styles.active : ''}
                onClick={() => setStatus(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </label>
        <footer>
          <button onClick={onClose} type="button">취소</button>
          <button onClick={() => onApply?.({ playerId, status })} type="button">적용하기</button>
        </footer>
      </section>
    </main>
  );
}
