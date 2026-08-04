import type { FormEvent } from 'react';
import styles from './MissionCreateFormScreen.module.css';
import type { MissionCreateFormDateMode, MissionCreateFormProps } from './types';

const DATE_MODES: { mode: MissionCreateFormDateMode; labelKey: 'todayLabel' | 'tomorrowLabel' | null }[] = [
  { mode: 'today', labelKey: 'todayLabel' },
  { mode: 'tomorrow', labelKey: 'tomorrowLabel' },
  { mode: 'custom', labelKey: null },
];

export function MissionCreateFormScreen({
  model,
  embedded,
  onToggleAssignee,
  onToggleAllAssignees,
  onTitleChange,
  onDescriptionChange,
  onPointChange,
  onQuickPointSelect,
  onDateModeChange,
  onCustomDateChange,
  onCancel,
  onCreate,
}: MissionCreateFormProps) {
  const allSelected = model.assignees.length > 0 && model.selectedAssigneeIds.length === model.assignees.length;

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!model.canSubmit) return;
    onCreate?.({
      assigneeIds: model.selectedAssigneeIds,
      title: model.title,
      description: model.description,
      point: model.point,
      dateMode: model.dateMode,
      customDate: model.customDate,
    });
  };

  return (
    <main className={`${styles.screen} ${embedded ? styles.embedded : ''}`} data-canonical-screen-id="2l" data-canonical-screen-label="미션 만들기 폼" data-canonical-source="wave7-full-authority">
      {!embedded && (
        <aside className={styles.sidebar}>
          <strong>우리 가족</strong>
          <span>관리자 모드</span>
          <nav><b>대시보드</b><b className={styles.active}>미션 관리</b><b>포인트 관리</b><b>사용자 관리</b><b>알림 관리</b></nav>
        </aside>
      )}
      <section className={styles.content} aria-label="미션 만들기">
        <header>
          <div><span>미션 관리</span><h1>새 미션 만들기</h1><p>가족에게 전달할 미션을 설정해 보세요.</p></div>
          {!embedded && <button type="button" aria-label="닫기" onClick={onCancel}>×</button>}
        </header>
        <div className={styles.columns}>
          <form className={styles.form} onSubmit={handleSubmit}>
            <fieldset>
              <legend>대상 자녀</legend>
              <div className={styles.assigneeGroup}>
                <button
                  type="button"
                  className={allSelected ? styles.assigneeChipActive : styles.assigneeChip}
                  onClick={onToggleAllAssignees}
                >
                  모두
                </button>
                {model.assignees.map((a) => (
                  <button
                    type="button"
                    key={a.id}
                    className={model.selectedAssigneeIds.includes(a.id) ? styles.assigneeChipActive : styles.assigneeChip}
                    onClick={() => onToggleAssignee?.(a.id)}
                  >
                    {a.name}
                  </button>
                ))}
              </div>
            </fieldset>

            <label>미션 제목
              <input value={model.title} onChange={(e) => onTitleChange?.(e.target.value)} placeholder="미션 내용을 입력하세요" />
            </label>
            <label>설명
              <textarea value={model.description} onChange={(e) => onDescriptionChange?.(e.target.value)} />
            </label>
            <fieldset>
              <legend>미션 유형</legend>
              <div className={styles.pills}>
                <span className={styles.selected}>일상</span>
                <span>학습</span>
                <span>가족 협동</span>
              </div>
            </fieldset>
            <div className={styles.pair}>
              <label className={styles.pointLabel}>보상 포인트
                <div className={styles.pointRow}>
                  <input
                    type="number"
                    min={1}
                    value={model.point}
                    onChange={(e) => onPointChange?.(Number(e.target.value))}
                  />
                  <div className={styles.quickBtns}>
                    {model.quickPointOptions.map((v) => (
                      <button type="button" key={v} onClick={() => onQuickPointSelect?.(v)}>{v}pt</button>
                    ))}
                  </div>
                </div>
              </label>
              <label className={styles.toggle}>인증 사진 필수<i /></label>
            </div>
            <fieldset>
              <legend>날짜</legend>
              <div className={styles.dateGroup}>
                {DATE_MODES.map(({ mode, labelKey }) => (
                  <button
                    type="button"
                    key={mode}
                    className={model.dateMode === mode ? styles.dateBtnActive : styles.dateBtn}
                    onClick={() => onDateModeChange?.(mode)}
                  >
                    {labelKey ? model[labelKey] : '날짜 선택'}
                  </button>
                ))}
                {model.dateMode === 'custom' && (
                  <input
                    type="date"
                    value={model.customDate}
                    onChange={(e) => onCustomDateChange?.(e.target.value)}
                  />
                )}
              </div>
            </fieldset>
            <label className={styles.toggle}>보호자 승인 필요<i /></label>
            {model.validationMessage && <p className={styles.validation}>{model.validationMessage}</p>}
            <div className={styles.actions}>
              <button type="button" onClick={onCancel}>취소</button>
              <button type="submit" disabled={!model.canSubmit || model.submitting}>
                {model.submitting ? '만드는 중...' : '미션 만들기'}
              </button>
            </div>
          </form>
          <aside className={styles.preview}>
            <span>실시간 미리보기</span>
            <article>
              <i>🧹</i>
              <div><strong>{model.title || '미션 제목'}</strong><p>{model.description}</p></div>
              <b>+{model.point}P</b>
            </article>
            <p className={styles.note}>
              {model.selectedAssigneeIds.length > 0
                ? `${model.assignees.filter((a) => model.selectedAssigneeIds.includes(a.id)).map((a) => a.name).join('·')}의 오늘 미션에 바로 추가돼요.`
                : '대상 자녀를 선택해주세요.'}
            </p>
          </aside>
        </div>
      </section>
    </main>
  );
}
