import { useState, useMemo } from 'react';
import styles from './CardDetailTable.module.css';
import type { Mission, Player } from '../../../types/admin.types';

// ========================================
// 그룹 행 타입 (총 발행포인트 아코디언용)
// ========================================

interface GroupRow {
  key: string;
  date: string;
  playerId: number;
  playerName: string;
  totalCount: number;
  totalPoints: number;
  doneCount: number;
  donePoints: number;
  rate: number;
  missions: Mission[];
}

// ========================================
// Props
// ========================================

type CardMode = 'points' | 'active' | 'pending' | 'completed';

interface CardDetailTableProps {
  mode: CardMode;
  missions: Mission[];
  players: Player[];
  cycleLabel: string;
}

// ========================================
// 상태 pill 매핑
// ========================================

const STATUS_LABEL: Record<string, string> = {
  active: '진행중',
  completed: '완료',
  pending_approval: '승인대기',
  failed: '실패',
  proposed: '제안',
  rejected: '거절',
};

const STATUS_CLASS: Record<string, string> = {
  active: 'statusActive',
  completed: 'statusCompleted',
  pending_approval: 'statusPending',
  failed: 'statusFailed',
};

// ========================================
// 컴포넌트
// ========================================

export default function CardDetailTable({ mode, missions, players, cycleLabel }: CardDetailTableProps) {
  const [filterPlayerId, setFilterPlayerId] = useState<number | null>(null);
  const [expandedGroup, setExpandedGroup] = useState<string | null>(null);

  const playerMap = useMemo(() => {
    const map = new Map<number, string>();
    players.forEach(p => map.set(p.id, p.name));
    return map;
  }, [players]);

  const filtered = useMemo(() => {
    let list = [...missions];

    if (filterPlayerId !== null) {
      list = list.filter(m => m.player_id === filterPlayerId);
    }

    if (mode === 'active') list = list.filter(m => m.status === 'active');
    else if (mode === 'pending') list = list.filter(m => m.status === 'pending_approval');
    else if (mode === 'completed') list = list.filter(m => m.status === 'completed');

    list.sort((a, b) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      return a.player_id - b.player_id;
    });

    return list;
  }, [missions, mode, filterPlayerId]);

  const groupRows = useMemo<GroupRow[]>(() => {
    if (mode !== 'points') return [];

    const groups = new Map<string, GroupRow>();

    filtered.forEach(m => {
      const key = `${m.date}_${m.player_id}`;
      if (!groups.has(key)) {
        groups.set(key, {
          key,
          date: m.date,
          playerId: m.player_id,
          playerName: playerMap.get(m.player_id) || '?',
          totalCount: 0,
          totalPoints: 0,
          doneCount: 0,
          donePoints: 0,
          rate: 0,
          missions: [],
        });
      }
      const g = groups.get(key)!;
      g.totalCount += 1;
      g.totalPoints += m.point;
      if (m.status === 'completed') {
        g.doneCount += 1;
        g.donePoints += m.point;
      }
      g.missions.push(m);
    });

    groups.forEach(g => {
      g.rate = g.totalPoints > 0 ? Math.round((g.donePoints / g.totalPoints) * 100) : 0;
    });

    return Array.from(groups.values()).sort((a, b) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      return a.playerId - b.playerId;
    });
  }, [filtered, mode, playerMap]);

  const fmtDate = (d: string) => d.slice(5);

  const toggleGroup = (key: string) => {
    setExpandedGroup(prev => prev === key ? null : key);
  };

  return (
    <div className={styles.container}>
      {/* 헤더: 주기 라벨 + 플레이어 필터 */}
      <div className={styles.tableHeader}>
        {(mode === 'points' || mode === 'completed') ? (
          <span className={styles.cycleLabel}>{cycleLabel}</span>
        ) : (
          <span />
        )}
        <select
          className={styles.playerFilter}
          value={filterPlayerId ?? ''}
          onChange={(e) => setFilterPlayerId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">전체</option>
          {players.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {/* points 모드: 아코디언 그룹 */}
      {mode === 'points' && (
        <div className={styles.groupList}>
          {groupRows.length === 0 && (
            <div className={styles.empty}>이번 주기 데이터가 없습니다.</div>
          )}
          {groupRows.map(g => (
            <div key={g.key} className={styles.groupItem}>
              <div
                className={`${styles.groupRow} ${expandedGroup === g.key ? styles.groupRowActive : ''}`}
                onClick={() => toggleGroup(g.key)}
              >
                <span className={styles.grDate}>{fmtDate(g.date)}</span>
                <span className={styles.grName}>{g.playerName}</span>
                <span className={styles.grAssigned}>
                  배정 {g.totalCount}건 · {g.totalPoints}P
                </span>
                <span className={styles.grDone}>
                  완료 {g.doneCount}건 · {g.donePoints}P
                  <span className={styles.grRate}> ({g.rate}%)</span>
                </span>
                <span className={styles.grToggle}>
                  {expandedGroup === g.key ? '▼' : '▶'}
                </span>
              </div>

              {expandedGroup === g.key && (
                <div className={styles.drilldown}>
                  <table className={styles.detailTable}>
                    <thead>
                      <tr>
                        <th>일자</th>
                        <th>이름</th>
                        <th>미션명</th>
                        <th>포인트</th>
                        <th>상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      {g.missions.map(m => (
                        <tr key={m.id}>
                          <td data-label="일자">{fmtDate(m.date)}</td>
                          <td data-label="이름">{playerMap.get(m.player_id)}</td>
                          <td data-label="미션명">{m.text}</td>
                          <td data-label="포인트">{m.point}P</td>
                          <td data-label="상태">
                            <span className={`${styles.statusPill} ${styles[STATUS_CLASS[m.status] ?? '']}`}>
                              {STATUS_LABEL[m.status] ?? m.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* active / pending / completed 모드: flat 테이블 */}
      {mode !== 'points' && (
        <div className={styles.flatTableWrap}>
          {filtered.length === 0 && (
            <div className={styles.empty}>
              {mode === 'active' && '진행중인 미션이 없습니다.'}
              {mode === 'pending' && '승인 대기 미션이 없습니다.'}
              {mode === 'completed' && '완료된 미션이 없습니다.'}
            </div>
          )}
          {filtered.length > 0 && (
            <table className={styles.detailTable}>
              <thead>
                <tr>
                  <th>일자</th>
                  <th>이름</th>
                  <th>미션명</th>
                  <th>포인트</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(m => (
                  <tr key={m.id}>
                    <td data-label="일자">{fmtDate(m.date)}</td>
                    <td data-label="이름">{playerMap.get(m.player_id)}</td>
                    <td data-label="미션명">{m.text}</td>
                    <td data-label="포인트">{m.point}P</td>
                    <td data-label="상태">
                      <span className={`${styles.statusPill} ${styles[STATUS_CLASS[m.status] ?? '']}`}>
                        {STATUS_LABEL[m.status] ?? m.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
