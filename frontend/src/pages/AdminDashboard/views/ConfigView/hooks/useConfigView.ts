import { useState, useEffect, useMemo } from 'react';
import { adminApi } from '../../../api/adminApi';
import { getLocalToday } from '../../../../../shared/utils/dateUtils';
import { useAdminToast } from '../../../hooks/useAdminToast';
import { useCycle } from '../../../hooks/useCycle';

const ALL_KEYS = [
  'cheer.senders',
  'point.cycle',
  'level.thresholds',
  'admin.display_name',
  'photos.dad',
  'photos.mom',
] as const;

type ConfigKey = typeof ALL_KEYS[number];
type CheerSender = 'dad' | 'mom';

const TODAY = getLocalToday();

export function useConfigView() {
  const { showToast } = useAdminToast();
  const cycle = useCycle();
  const [configs,        setConfigs]        = useState<Record<string, string | null>>({});
  const [original,       setOriginal]       = useState<Record<string, string | null>>({});
  const [cheerMsgs,      setCheerMsgs]      = useState<Record<CheerSender, string>>({ dad: '', mom: '' });
  const [cheerOriginal,  setCheerOriginal]  = useState<Record<CheerSender, string>>({ dad: '', mom: '' });
  const [loading,        setLoading]        = useState(true);
  const [saving,         setSaving]         = useState(false);

  useEffect(() => {
    const ctrl = new AbortController();
    setLoading(true);
    Promise.all([
      Promise.all(
        ALL_KEYS.map((key) =>
          adminApi.getConfig(key, ctrl.signal)
            .then((r) => ({ key, value: r.data.value }))
            .catch(() => ({ key, value: null as string | null }))
        )
      ),
      adminApi.getCheers(TODAY, ctrl.signal)
        .then((r) => r.data)
        .catch(() => []),
    ]).then(([configResults, cheers]) => {
      if (!ctrl.signal.aborted) {
        const map: Record<string, string | null> = {};
        configResults.forEach((r) => { map[r.key] = r.value; });
        setConfigs(map);
        setOriginal(map);

        const msgs: Record<CheerSender, string> = { dad: '', mom: '' };
        cheers.forEach((c) => {
          if (c.sender === 'dad' || c.sender === 'mom') msgs[c.sender] = c.message;
        });
        setCheerMsgs(msgs);
        setCheerOriginal({ ...msgs });
        setLoading(false);
      }
    });
    return () => ctrl.abort();
  }, []);

  const setConfig = (key: ConfigKey, value: string) => {
    setConfigs((prev) => ({ ...prev, [key]: value }));
  };

  const setCheerMessage = (sender: CheerSender, message: string) => {
    setCheerMsgs((prev) => ({ ...prev, [sender]: message }));
  };

  const isConfigDirty = ALL_KEYS.some((k) => configs[k] !== original[k]);
  const isCheerDirty  = ((['dad', 'mom'] as CheerSender[]).some((s) => cheerMsgs[s] !== cheerOriginal[s]));
  const isDirty = isConfigDirty || isCheerDirty;

  const saveAll = async () => {
    if (!isDirty) return;
    setSaving(true);
    try {
      const tasks: Promise<unknown>[] = [];

      const changed = ALL_KEYS.filter((k) => configs[k] !== original[k]);
      changed
        .filter((k) => configs[k] != null)
        .forEach((k) => tasks.push(adminApi.updateConfig(k, configs[k]!)));

      (['dad', 'mom'] as CheerSender[])
        .filter((s) => cheerMsgs[s] !== cheerOriginal[s] && cheerMsgs[s].trim() !== '')
        .forEach((s) =>
          tasks.push(adminApi.upsertCheer(TODAY, { date: TODAY, sender: s, message: cheerMsgs[s] }))
        );

      await Promise.all(tasks);
      setOriginal({ ...configs });
      setCheerOriginal({ ...cheerMsgs });
      showToast('success', '설정 저장 완료!');
    } catch {
      showToast('error', '저장 실패');
    } finally {
      setSaving(false);
    }
  };

  const cycleDaysRemaining = useMemo(() => {
    if (!cycle?.endDate) return null;
    const end = new Date(cycle.endDate + 'T23:59:59');
    const today = new Date();
    const diff = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  }, [cycle]);

  const handlePeriodChange = async (period: string) => {
    try {
      await adminApi.updateConfig('point_cycle', period);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const detail = axiosErr.response?.data?.detail || '주기 변경에 실패했습니다.';
      showToast('error', detail);
    }
  };

  return { configs, setConfig, cheerMsgs, setCheerMessage, isDirty, saveAll, loading, saving, cycleDaysRemaining, handlePeriodChange };
}
