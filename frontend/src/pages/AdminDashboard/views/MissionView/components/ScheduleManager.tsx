import { useState, useEffect, useCallback } from 'react';
import { httpClient } from '../../../../../shared/api/httpClient';
import styles from './ScheduleManager.module.css';
import AppIcon from '../../../../../shared/components/AppIcon';

interface Template {
  id: number;
  player_id: number;
  text: string;
  point: number;
  day_of_week: number;
  is_active: boolean;
  group_id: string | null;
}

interface Player {
  id: number;
  name: string;
}

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];

interface ScheduleManagerProps {
  players: Player[];
  selectedPlayerId: number | null;
}

export default function ScheduleManager({ players, selectedPlayerId }: ScheduleManagerProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);

  // 폼 상태
  const [newText, setNewText] = useState('');
  const [newPoint, setNewPoint] = useState(5);
  const [newDays, setNewDays] = useState(127); // 매일

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await httpClient.get('/api/mission-templates');
      setTemplates(data);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadTemplates(); }, [loadTemplates]);

  const toggleDay = (bit: number) => {
    setNewDays(prev => prev ^ bit);
  };

  const handleCreate = async () => {
    if (!newText.trim()) return;
    // 전체 선택 시 모든 플레이어에게 각각 템플릿 생성, 특정 플레이어 선택 시 해당 1명만
    const targetPlayerIds = selectedPlayerId !== null
      ? [selectedPlayerId]
      : players.map((p) => p.id);
    if (targetPlayerIds.length === 0) return;

    // 2명 이상에게 할당 시 같은 group_id 공유 → 이후 일괄 삭제 가능
    const groupId = targetPlayerIds.length > 1 ? crypto.randomUUID() : undefined;
    try {
      await Promise.all(
        targetPlayerIds.map((pid) =>
          httpClient.post('/api/mission-templates', {
            player_id: pid,
            text: newText.trim(),
            point: newPoint,
            day_of_week: newDays,
            group_id: groupId,
          })
        )
      );
      // 생성 직후 오늘 날짜로 Lazy Init 실행 → 플레이어 화면에 즉시 반영
      await httpClient.post('/api/mission-templates/generate');
      setNewText('');
      setNewPoint(5);
      setNewDays(127);
      await loadTemplates();
    } catch {
      /* error toast */
    }
  };

  const handleDelete = async (id: number, groupId?: string | null) => {
    if (groupId) {
      const ok = confirm('이 반복 미션은 여러 플레이어에게 함께 설정되었습니다.\n모든 플레이어의 반복 미션을 함께 삭제하시겠습니까?\n\n[확인] 전체 삭제 / [취소] 이 항목만 삭제');
      try {
        if (ok) {
          await httpClient.delete(`/api/mission-templates/by-group/${groupId}`);
        } else {
          await httpClient.delete(`/api/mission-templates/${id}`);
        }
        await loadTemplates();
      } catch { /* ignore */ }
    } else {
      if (!confirm('이 반복 미션을 삭제하시겠습니까?')) return;
      try {
        await httpClient.delete(`/api/mission-templates/${id}`);
        await loadTemplates();
      } catch { /* ignore */ }
    }
  };

  const handleToggleActive = async (tmpl: Template) => {
    try {
      await httpClient.patch(`/api/mission-templates/${tmpl.id}`, {
        is_active: !tmpl.is_active,
      });
      await loadTemplates();
    } catch {
      /* ignore */
    }
  };

  const formatDays = (bitmask: number): string => {
    if (bitmask === 127) return '매일';
    return DAY_LABELS.filter((_, i) => bitmask & DAY_BITS[i]).join(', ');
  };

  const getPlayerName = (id: number) => players.find(p => p.id === id)?.name ?? '?';

  // 표시할 템플릿 필터링 (전체 or 특정 플레이어)
  const visibleTemplates = selectedPlayerId === null
    ? templates
    : templates.filter(t => t.player_id === selectedPlayerId);

  return (
    <div className={styles.container}>
      <h3 className={styles.sectionTitle}>
        <AppIcon name="checklist" size={20} /> 반복 미션 스케줄
        {selectedPlayerId !== null && players.find(p => p.id === selectedPlayerId) && (
          <span className={styles.playerTag}>
            {players.find(p => p.id === selectedPlayerId)!.name}
          </span>
        )}
      </h3>

      {/* 생성 폼 */}
      <div className={styles.createForm}>
        {/* Row 1: 요일 선택 */}
        <div className={styles.dayPicker}>
          {DAY_LABELS.map((label, i) => (
            <button
              key={label}
              type="button"
              className={`${styles.dayBtn} ${newDays & DAY_BITS[i] ? styles.dayActive : ''}`}
              onClick={() => toggleDay(DAY_BITS[i])}
            >
              {label}
            </button>
          ))}
        </div>

        <input
          type="text"
          placeholder="예: 이 닦기"
          value={newText}
          onChange={e => setNewText(e.target.value)}
          className={styles.input}
        />
        <input
          type="number"
          min={0}
          value={newPoint}
          onChange={e => setNewPoint(Number(e.target.value))}
          className={styles.pointInput}
        />
        <span className={styles.pointLabel}>P</span>
        <button onClick={handleCreate} className={styles.addBtn}>추가</button>
      </div>

      {/* 목록 */}
      {loading ? (
        <p className={styles.loading}>로딩 중...</p>
      ) : visibleTemplates.length === 0 ? (
        <p className={styles.empty}>등록된 반복 미션이 없습니다.</p>
      ) : (
        <div className={styles.list}>
          {visibleTemplates.map(tmpl => (
            <div key={tmpl.id} className={`${styles.card} ${!tmpl.is_active ? styles.inactive : ''}`}>
              <div className={styles.cardBody}>
                {selectedPlayerId === null && (
                  <span className={styles.playerBadge}>{getPlayerName(tmpl.player_id)}</span>
                )}
                <span className={styles.missionText}>{tmpl.text}</span>
                <span className={styles.pointBadge}>{tmpl.point}P</span>
              </div>
              <div className={styles.cardMeta}>
                <span className={styles.dayTags}>{formatDays(tmpl.day_of_week)}</span>
                <div className={styles.actions}>
                  <button
                    onClick={() => handleToggleActive(tmpl)}
                    className={styles.toggleBtn}
                  >
                    {tmpl.is_active ? '비활성화' : '활성화'}
                  </button>
                  <button onClick={() => handleDelete(tmpl.id, tmpl.group_id)} className={styles.deleteBtn}>
                    삭제
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
