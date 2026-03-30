import { useState } from 'react';
import styles from '../UserDashboard.module.css';
import { CheerResponse } from '../api/dashboardApi';
import CheerModal from './CheerModal';

interface Props {
  cheers: CheerResponse[];
}

const SENDERS = [
  { key: 'dad', label: '아빠', emoji: '👨' },
  { key: 'mom', label: '엄마', emoji: '👩' },
];

export default function StoryCards({ cheers }: Props) {
  const [selected, setSelected] = useState<CheerResponse | null>(null);

  const getCheer = (sender: string) =>
    cheers.find(c => c.sender === sender || c.sender === (sender === 'dad' ? '아빠' : '엄마'));

  return (
    <>
      <div className={styles.storyRow}>
        {SENDERS.map(({ key, label, emoji }) => {
          const cheer = getCheer(key);
          return (
            <button
              key={key}
              className={styles.storyCard}
              onClick={() => cheer && setSelected(cheer)}
              style={{ background: 'transparent', border: 'none', cursor: cheer ? 'pointer' : 'default' }}
            >
              <div className={styles.storyRing} style={{ opacity: cheer ? 1 : 0.4 }}>
                <div className={styles.storyAvatar}>{emoji}</div>
              </div>
              <span className={styles.storyName}>{label}</span>
            </button>
          );
        })}
      </div>

      {selected && (
        <CheerModal
          sender={selected.sender}
          message={selected.message}
          isOpen={true}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
