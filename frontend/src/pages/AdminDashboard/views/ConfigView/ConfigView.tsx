import styles from './ConfigView.module.css';
import { useConfigView } from './hooks/useConfigView';
import CheerSlotConfig from './components/CheerSlotConfig';
import CycleConfig from './components/CycleConfig';
import LevelConfig from './components/LevelConfig';
import SystemConfig from './components/SystemConfig';

export default function ConfigView() {
  const { configs, setConfig, cheerMsgs, setCheerMessage, isDirty, saveAll, loading, saving, cycleDaysRemaining, handlePeriodChange } = useConfigView();

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>설정</h1>
        <div className={styles.headerRight}>
          {isDirty && <span className={styles.dirtyNote}>저장되지 않은 변경사항</span>}
          <button
            className={styles.btnSave}
            onClick={saveAll}
            disabled={saving || !isDirty}
          >
            {saving ? '저장 중...' : '저장'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className={styles.loading}>로딩 중...</div>
      ) : (
        <>
          <CheerSlotConfig
            value={configs['cheer.senders'] ?? null}
            onChange={(v) => setConfig('cheer.senders', v)}
            photos={configs}
            onPhotoChange={(key, base64) => setConfig(key as 'photos.dad' | 'photos.mom', base64)}
            cheerMsgs={cheerMsgs}
            onCheerMsgChange={setCheerMessage}
          />
          <CycleConfig
            value={configs['point.cycle'] ?? null}
            onChange={(v) => setConfig('point.cycle', v)}
            onPeriodChange={handlePeriodChange}
            cycleDaysRemaining={cycleDaysRemaining}
          />
          <LevelConfig
            value={configs['level.thresholds'] ?? null}
            onChange={(v) => setConfig('level.thresholds', v)}
          />
          <SystemConfig
            displayName={configs['admin.display_name'] ?? null}
            onDisplayName={(v) => setConfig('admin.display_name', v)}
          />
        </>
      )}
    </div>
  );
}
