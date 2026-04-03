import { useState } from 'react';
import styles from './PhotoUploadModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';
import PhotoUpload from '../../../../../shared/components/PhotoUpload/PhotoUpload';
import type { Player } from '../../../types/admin.types';

interface Props {
  open:    boolean;
  onClose: () => void;
  player:  Player;
  onSave:  (photo: string) => Promise<void>;
}

export default function PhotoUploadModal({ open, onClose, player, onSave }: Props) {
  const [photo,      setPhoto]      = useState<string | null>(player.photo);
  const [submitting, setSubmitting] = useState(false);

  const handleSave = async () => {
    if (!photo) return;
    setSubmitting(true);
    try {
      await onSave(photo);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title={`${player.name} 사진 변경`} width={360}>
      <div className={styles.body}>
        <PhotoUpload
          currentPhoto={photo ?? undefined}
          label={player.name}
          onChange={setPhoto}
        />
      </div>
      <button
        className={styles.btnSubmit}
        onClick={handleSave}
        disabled={submitting || !photo || photo === player.photo}
      >
        {submitting ? '저장 중...' : '사진 저장'}
      </button>
    </AdminModal>
  );
}
