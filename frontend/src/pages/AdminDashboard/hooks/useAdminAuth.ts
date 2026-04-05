import { useState, useEffect } from 'react';
import { useAuthStore } from '../../../shared/stores/useAuthStore';
import { adminApi } from '../api/adminApi';

export function useAdminAuth() {
  const { adminDisplayName, logout } = useAuthStore();
  const [adminPhoto, setAdminPhoto] = useState<string | null>(null);

  useEffect(() => {
    if (!adminDisplayName) return;
    const key = adminDisplayName === '아빠' ? 'photos.dad' : adminDisplayName === '엄마' ? 'photos.mom' : null;
    if (!key) return;
    const ctrl = new AbortController();
    adminApi.getConfig(key, ctrl.signal)
      .then((r) => { if (!ctrl.signal.aborted) setAdminPhoto(r.data.value || null); })
      .catch(() => {});
    return () => ctrl.abort();
  }, [adminDisplayName]);

  return { adminDisplayName, adminPhoto, logout };
}
