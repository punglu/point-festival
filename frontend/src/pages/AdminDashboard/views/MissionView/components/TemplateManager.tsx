import { useState, useEffect, useCallback } from 'react';
import { httpClient } from '../../../../../shared/api/httpClient';
import styles from './TemplateManager.module.css';

interface Template {
  id: number;
  player_id: number;
  text: string;
  point: number;
  day_of_week: number;
  is_active: boolean;
  group_id?: string | null;
}

interface Player {
  id: number;
  name: string;
}

interface TemplateManagerProps {
  isOpen: boolean;
  onClose: () => void;
  players: Player[];
  onOpenCreateModal: () => void;
  onOpenEditModal: (template: Template) => void;
}

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];

export default function TemplateManager({
  isOpen, onClose, players, onOpenCreateModal, onOpenEditModal
}: TemplateManagerProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);

  // 삭제 모달 상태
  const [deleteMode, setDeleteMode] = useState(false);
  const [deleteTargetIds, setDeleteTargetIds] = useState<number[]>([]);
  const [deleteOption, setDeleteOption] = useState<'template' | 'template_and_missions'>('template');
  const [dateStart, setDateStart] = useState('');
  const [dateEnd, setDateEnd] = useState('');
  const [preview, setPreview] = useState<{
    template_count: number;
    mission_count: number;
    completed_count: number;
    pending_count: number;
  } | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await httpClient.get('/api/mission-templates');
      setTemplates(data);
    } catch { /* */ } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) loadTemplates();
  }, [isOpen, loadTemplates]);

  const groupedTemplates = templates.reduce<Record<string, Template[]>>((acc, t) => {
    const key = t.group_id || `single_${t.id}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(t);
    return acc;
  }, {});

  const formatDays = (bitmask: number) => {
    if (bitmask === 127) return '매일';
    const weekdays = 1 | 2 | 4 | 8 | 16;
    if (bitmask === weekdays) return '주중(월~금)';
    return DAY_LABELS.filter((_, i) => bitmask & DAY_BITS[i]).join(', ');
  };

  const getPlayerName = (id: number) => players.find(p => p.id === id)?.name ?? '?';

  const fetchPreview = async () => {
    try {
      const { data } = await httpClient.post('/api/mission-templates/batch-delete/preview', {
        template_ids: deleteTargetIds,
        delete_missions: deleteOption === 'template_and_missions',
        mission_date_start: dateStart || null,
        mission_date_end: dateEnd || null,
      });
      setPreview(data);
    } catch { /* */ }
  };

  const executeDelete = async () => {
    setDeleting(true);
    try {
      await httpClient.post('/api/mission-templates/batch-delete', {
        template_ids: deleteTargetIds,
        delete_missions: deleteOption === 'template_and_missions',
        mission_date_start: dateStart || null,
        mission_date_end: dateEnd || null,
      });
      setDeleteMode(false);
      setDeleteTargetIds([]);
      setPreview(null);
      await loadTemplates();
    } catch { /* */ } finally {
      setDeleting(false);
    }
  };

  const openDeleteForGroup = (groupTemplates: Template[]) => {
    setDeleteTargetIds(groupTemplates.map(t => t.id));
    setDeleteMode(true);
    setDeleteOption('template');
    setPreview(null);

    const today = new Date();
    const weekday = today.getDay();
    const mondayOffset = weekday === 0 ? -6 : 1 - weekday;
    const monday = new Date(today);
    monday.setDate(today.getDate() + mondayOffset);
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    setDateStart(monday.toISOString().slice(0, 10));
    setDateEnd(sunday.toISOString().slice(0, 10));
  };

  if (!isOpen) return null;

  // --- 삭제 확인 서브뷰 ---
  if (deleteMode) {
    return (
      <div className={styles.overlay} onClick={() => setDeleteMode(false)}>
        <div className={styles.modal} onClick={e => e.stopPropagation()}>
          <div className={styles.header}>
            <h3 className={styles.title}>반복미션 일괄 삭제</h3>
            <button className={styles.closeBtn} onClick={() => setDeleteMode(false)}>✕</button>
          </div>

          <div className={styles.dangerBanner}>
            이 작업은 되돌릴 수 없습니다. 삭제 전 내용을 확인해 주세요.
          </div>

          <div className={styles.section}>
            <label className={styles.sectionLabel}>삭제 대상</label>
            <div className={styles.optionRow}>
              <button
                className={`${styles.optionCard} ${deleteOption === 'template' ? styles.optionActive : ''}`}
                onClick={() => { setDeleteOption('template'); setPreview(null); }}
              >
                <strong>템플릿만</strong>
                <span>향후 자동생성 중단</span>
              </button>
              <button
                className={`${styles.optionCard} ${deleteOption === 'template_and_missions' ? styles.optionActive : ''}`}
                onClick={() => { setDeleteOption('template_and_missions'); setPreview(null); }}
              >
                <strong>템플릿 + 미션</strong>
                <span>생성된 미션도 함께 삭제</span>
              </button>
            </div>
          </div>

          {deleteOption === 'template_and_missions' && (
            <div className={styles.section}>
              <label className={styles.sectionLabel}>미션 삭제 날짜 범위</label>
              <div className={styles.dateRow}>
                <input type="date" value={dateStart} onChange={e => { setDateStart(e.target.value); setPreview(null); }} />
                <span>~</span>
                <input type="date" value={dateEnd} onChange={e => { setDateEnd(e.target.value); setPreview(null); }} />
              </div>
            </div>
          )}

          <button className={styles.previewBtn} onClick={fetchPreview}>
            삭제 미리보기
          </button>

          {preview && (
            <div className={styles.previewBox}>
              <div className={styles.previewRow}>
                <span>삭제될 템플릿</span>
                <span className={styles.dangerText}>{preview.template_count}건</span>
              </div>
              {deleteOption === 'template_and_missions' && (
                <>
                  <div className={styles.previewRow}>
                    <span>삭제될 미션 (active+pending 등)</span>
                    <span className={styles.dangerText}>{preview.mission_count}건</span>
                  </div>
                  {preview.pending_count > 0 && (
                    <div className={styles.warningBanner}>
                      ⚠️ 승인 대기 중 {preview.pending_count}건도 삭제됩니다
                    </div>
                  )}
                  <div className={styles.previewRow}>
                    <span>완료 미션 (보존)</span>
                    <span className={styles.successText}>{preview.completed_count}건</span>
                  </div>
                </>
              )}
            </div>
          )}

          <div className={styles.actionRow}>
            <button className={styles.cancelBtn} onClick={() => setDeleteMode(false)}>취소</button>
            <button
              className={styles.deleteBtn}
              onClick={executeDelete}
              disabled={!preview || deleting}
            >
              {deleting ? '삭제 중...' : '삭제 실행'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- 목록 뷰 ---
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>반복미션 관리</h3>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        <button className={styles.addBtn} onClick={onOpenCreateModal}>
          + 새 반복미션 추가
        </button>

        {loading ? (
          <div className={styles.loadingText}>로딩 중...</div>
        ) : Object.keys(groupedTemplates).length === 0 ? (
          <div className={styles.emptyText}>등록된 반복미션이 없습니다</div>
        ) : (
          <div className={styles.templateList}>
            {Object.entries(groupedTemplates).map(([groupKey, groupTemplates]) => {
              const first = groupTemplates[0];
              const playerNames = groupTemplates.map(t => getPlayerName(t.player_id)).join(', ');
              const isGroup = groupTemplates.length > 1;

              return (
                <div key={groupKey} className={styles.templateCard}>
                  <div className={styles.cardTop}>
                    <div className={styles.cardInfo}>
                      <span className={styles.cardTitle}>{first.text}</span>
                      <span className={styles.cardPoint}>{first.point}P</span>
                    </div>
                    <div className={styles.cardMeta}>
                      <span>{playerNames}{isGroup ? ` (${groupTemplates.length}명)` : ''}</span>
                      <span className={styles.dot} />
                      <span>{formatDays(first.day_of_week)}</span>
                    </div>
                  </div>
                  <div className={styles.cardActions}>
                    {!isGroup && (
                      <button className={styles.editBtn} onClick={() => onOpenEditModal(first)}>편집</button>
                    )}
                    <button className={styles.deleteTrigger} onClick={() => openDeleteForGroup(groupTemplates)}>
                      삭제
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
