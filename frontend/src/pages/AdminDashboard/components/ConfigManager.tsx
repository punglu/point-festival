import { useState, useEffect } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, ConfigItem } from '../api/adminApi';

export default function ConfigManager() {
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [editValues, setEditValues] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const abortController = new AbortController();
    adminApi.getConfigs(abortController.signal)
      .then((res) => {
        if (!abortController.signal.aborted) {
          setConfigs(res.data);
          const initial: Record<string, string> = {};
          res.data.forEach((c) => { initial[c.key] = c.value ?? ''; });
          setEditValues(initial);
        }
      })
      .catch(() => {});
    return () => abortController.abort();
  }, []);

  const handleSave = async (key: string) => {
    setLoading(true);
    try {
      await adminApi.updateConfig(key, editValues[key] || null);
      alert(`'${key}' 저장 완료`);
    } catch {
      alert('저장 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>설정 관리</div>

      {configs.length === 0 ? (
        <div className={styles.emptyMsg}>설정이 없습니다.</div>
      ) : (
        configs.map((c) => (
          <div key={c.key} className={styles.configRow}>
            <span className={styles.configKey}>{c.key}</span>
            <textarea
              className={styles.formTextarea}
              value={editValues[c.key] ?? ''}
              onChange={(e) => setEditValues((prev) => ({ ...prev, [c.key]: e.target.value }))}
              rows={2}
            />
            <button
              className={`${styles.btnPrimary} ${styles.btnSm}`}
              onClick={() => handleSave(c.key)}
              disabled={loading}
            >
              저장
            </button>
          </div>
        ))
      )}
    </div>
  );
}
