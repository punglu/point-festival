import { useRef } from 'react';
import styles from './PhotoUpload.module.css';
import { compressImage } from '../../utils/compressImage';

interface Props {
  currentPhoto?: string;
  label?: string;
  onChange: (base64: string) => void;
}

export default function PhotoUpload({ currentPhoto, label = '사진 변경', onChange }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const base64 = await compressImage(file);
      onChange(base64);
    } catch {
      // ignore compression errors
    }
    e.target.value = '';
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.preview} onClick={() => inputRef.current?.click()}>
        {currentPhoto ? (
          <img src={currentPhoto} alt="photo" className={styles.photo} />
        ) : (
          <span className={styles.placeholder}>👤</span>
        )}
        <div className={styles.overlay}>
          <span className={styles.overlayIcon}>📷</span>
        </div>
      </div>
      <span className={styles.label}>{label}</span>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className={styles.fileInput}
        onChange={handleFileChange}
      />
    </div>
  );
}
