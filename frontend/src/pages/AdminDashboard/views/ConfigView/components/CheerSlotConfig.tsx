import styles from './CheerSlotConfig.module.css';
import PhotoUpload from '../../../../../shared/components/PhotoUpload/PhotoUpload';

interface CheerSender { key: string; name: string; }

interface Props {
  value:             string | null;  // JSON string: [{ key, name }]
  onChange:          (value: string) => void;
  photos:            Record<string, string | null>;
  onPhotoChange:     (key: string, base64: string) => void;
  cheerMsgs:         Record<string, string>;
  onCheerMsgChange:  (sender: 'dad' | 'mom', message: string) => void;
}

const DEFAULT_SENDERS: CheerSender[] = [
  { key: 'dad', name: '아빠' },
  { key: 'mom', name: '엄마' },
];

function parse(value: string | null): CheerSender[] {
  try {
    if (value) {
      const raw = JSON.parse(value);
      if (Array.isArray(raw)) {
        return raw.map((s: Record<string, unknown>) => ({
          key:  typeof s.key  === 'string' ? s.key  : String(s.key ?? ''),
          name: typeof s.name === 'string' ? s.name : (typeof s.label === 'string' ? s.label : '?'),
        }));
      }
    }
  } catch { /* ignore */ }
  return DEFAULT_SENDERS;
}

export default function CheerSlotConfig({ value, onChange, photos, onPhotoChange, cheerMsgs, onCheerMsgChange }: Props) {
  const senders = parse(value);

  const updateName = (index: number, name: string) => {
    const updated = senders.map((s, i) => i === index ? { ...s, name } : s);
    onChange(JSON.stringify(updated));
  };

  return (
    <div className={styles.section}>
      <div className={styles.sectionTitle}>응원 발신자 및 메세지 (오늘)</div>
      <div className={styles.slots}>
        {senders.map((s, i) => (
          <div key={s.key} className={styles.slotBlock}>
            <div className={styles.slotRow}>
              <PhotoUpload
                currentPhoto={photos[`photos.${s.key}`] ?? undefined}
                label=""
                onChange={(base64) => onPhotoChange(`photos.${s.key}`, base64)}
              />
              <input
                className={styles.slotInput}
                value={s.name}
                placeholder={`발신자 ${i + 1} 이름`}
                onChange={(e) => updateName(i, e.target.value)}
              />
            </div>
            <textarea
              className={styles.slotTextarea}
              value={cheerMsgs[s.key] ?? ''}
              placeholder={`${s.name}의 오늘 응원 메세지`}
              rows={3}
              onChange={(e) => onCheerMsgChange(s.key as 'dad' | 'mom', e.target.value)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
