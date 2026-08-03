import { useEffect, useState } from 'react';
import styles from '../Auth.module.css';
import PlayerCard from './PlayerCard';
import { authApi } from '../api/authApi';
import { SettingsIcon } from '../../../shared/components/icons/outline';
import MainLogo from '../../../shared/components/MainLogo';
import BrandCharacter from '../../../shared/components/BrandCharacter';

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

export default function PlayerSelectView({ onPlayerSelect, onAdminClick }: Props) {
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
      .then(res => res.json())
      .then(data => {
        if (data?.value && !controller.signal.aborted) {
          setThresholds(JSON.parse(data.value));
        }
      })
      .catch(() => {});

    return () => controller.abort();
  }, []);

  const lockedPlayer = players.find((p) => p.is_locked);

  return (
    <div className={styles.authView}>
      {/* 브랜드 헤더: 몽글이 축하형 캐릭터 + 19c 워드마크(for family) — 독립 자산/DOM */}
      <div className={styles.brandHeader}>
        <BrandCharacter
          variant="celebration"
          size="profileHero"
          decorative
          className={styles.brandCharacter}
        />
        <MainLogo
          variant="wordmark"
          tone="onBrand"
          size={132}
          descriptor
          className={styles.brandWordmark}
        />
        <p className={styles.brandSubtitle}>우리 가족의 공간, 함께 연결되는 하루</p>
      </div>

      {/* 프로필 선택 패널 */}
      <div className={styles.profilePanel}>
        <div className={styles.profilePanelHeading}>사용할 프로필을 선택하세요</div>

        <div className={styles.profileCardList}>
          {players.map((p) => (
            <PlayerCard
              key={p.id}
              name={p.name}
              photo={p.photo}
              level={thresholds ? calcLevel(p.total_points ?? 0, thresholds) : null}
              totalPoints={p.total_points ?? 0}
              isLocked={p.is_locked}
              onClick={() => onPlayerSelect({ id: p.id, name: p.name, photo: p.photo })}
            />
          ))}
        </div>

        {lockedPlayer && (
          <div className={styles.lockNotice}>
            {lockedPlayer.name}의 잠금은 안전을 위한 보호 조치입니다. 계속 잠겨 있다면 관리자에게
            문의해주세요.
          </div>
        )}

        <div className={styles.profileFooterRow}>
          {/* No dedicated settings destination exists in the app today
              (checked: no /settings route anywhere) — this icon activates
              the same admin-login entry as the link beside it, per PM
              direction to wire it to the existing entry point rather than
              leave it non-functional. */}
          <button
            type="button"
            className={styles.footerSettingsIcon}
            onClick={onAdminClick}
            aria-label="관리자 로그인"
          >
            <SettingsIcon size={20} />
          </button>
          <button className={styles.footerAdminLink} onClick={onAdminClick}>
            관리자 로그인 <span aria-hidden="true">›</span>
          </button>
        </div>
      </div>
    </div>
  );
}
