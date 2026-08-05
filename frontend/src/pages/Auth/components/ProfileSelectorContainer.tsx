import { useEffect, useState } from 'react';
import { authApi } from '../api/authApi';
import { ProfileSelectorScreen } from '../../../screens/auth/ProfileSelector';
import type { ProfileSelectorProfile } from '../../../screens/auth/ProfileSelector';

function calcLevel(totalPoints: number, thresholds: Record<number, number>): number {
  let level = 1;
  for (const [lv, threshold] of Object.entries(thresholds).sort((a, b) => Number(b[0]) - Number(a[0]))) {
    if (totalPoints >= threshold) { level = Number(lv); break; }
  }
  return level;
}

interface Player {
  id: number;
  name: string;
  photo: string | null;
  total_points: number;
  is_locked: boolean;
  role: string;
}

interface Props {
  onPlayerSelect: (player: { id: number; name: string; photo: string | null }) => void;
  onAdminClick: () => void;
}

/**
 * Product Adapter for canonical Screen 1a (profile-select step only). Fetches real
 * players/thresholds the same way the legacy player-select view did, maps them to the
 * canonical ViewModel, and preserves the legacy locked-profile guard at the container
 * level (PlayerCard used a `disabled` button; here `onSelect` is simply not forwarded
 * for a locked profile) — no auth policy change, no new backend call.
 */
export default function ProfileSelectorContainer({ onPlayerSelect, onAdminClick }: Props) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [thresholds, setThresholds] = useState<Record<number, number> | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    authApi.getPlayers(controller.signal)
      .then((list) => {
        if (!controller.signal.aborted) {
          setPlayers(list.filter((p) => p.role === 'player') as Player[]);
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setPlayers([]);
      });

    fetch('/api/configs/level.thresholds')
      .then((res) => res.json())
      .then((data) => {
        if (data?.value && !controller.signal.aborted) {
          setThresholds(JSON.parse(data.value));
        }
      })
      .catch(() => {});

    return () => controller.abort();
  }, []);

  const profiles: ProfileSelectorProfile[] = players.map((p) => {
    const level = thresholds ? calcLevel(p.total_points ?? 0, thresholds) : null;
    if (p.is_locked) {
      return {
        id: String(p.id),
        name: p.name,
        locked: true,
        lockReason: '잠김',
        lockRetry: '관리자에게 잠금 해제를 요청하세요',
      };
    }
    return {
      id: String(p.id),
      name: p.name,
      level: level !== null ? `Lv.${level} 모험가` : undefined,
      points: `${(p.total_points ?? 0).toLocaleString()}P`,
    };
  });

  const lockedPlayer = players.find((p) => p.is_locked);

  const model = {
    brand: '가족 플랫폼',
    tagline: '우리 가족의 공간, 함께 연결되는 하루',
    heading: '사용할 프로필을 선택하세요',
    profiles,
    ...(lockedPlayer
      ? {
          lockedNotice: {
            title: `${lockedPlayer.name}의 잠금은 안전을 위한 보호 조치입니다.`,
            body: '계속 잠겨 있다면 관리자에게 문의해주세요.',
          },
        }
      : {}),
    adminLoginLabel: '관리자 로그인',
  };

  const handleSelect = (key: string) => {
    const player = players.find((p) => String(p.id) === key) ?? players.find((p) => p.name === key);
    if (!player || player.is_locked) return;
    onPlayerSelect({ id: player.id, name: player.name, photo: player.photo });
  };

  return <ProfileSelectorScreen model={model} onSelect={handleSelect} onAdminLogin={onAdminClick} />;
}
