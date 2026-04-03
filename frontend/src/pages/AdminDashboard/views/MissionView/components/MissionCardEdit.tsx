import { useState } from 'react';
import styles from './MissionCardEdit.module.css';
import { POINT_QUICK_VALUES } from '../../../constants/admin.constants';
import type { Mission } from '../../../types/admin.types';

interface Props {
  mission: Mission;
  onSave:   (data: { text: string; point: number }) => void;
  onCancel: () => void;
}

export default function MissionCardEdit({ mission, onSave, onCancel }: Props) {
  const [text,  setText]  = useState(mission.text);
  const [point, setPoint] = useState(mission.point);

  return (
    <div className={styles.card}>
      <div>
        <div className={styles.label}>미션 이름</div>
        <input
          className={styles.input}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="미션 이름"
        />
      </div>
      <div>
        <div className={styles.label}>포인트</div>
        <div className={styles.pointRow}>
          <input
            type="number"
            className={styles.pointInput}
            value={point}
            min={1}
            onChange={(e) => setPoint(Number(e.target.value))}
          />
          <div className={styles.quickBtns}>
            {POINT_QUICK_VALUES.map((v) => (
              <button key={v} className={styles.quickBtn} onClick={() => setPoint(v)}>
                {v}pt
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className={styles.actions}>
        <button className={styles.btnSave}   onClick={() => onSave({ text, point })}>저장</button>
        <button className={styles.btnCancel} onClick={onCancel}>취소</button>
      </div>
    </div>
  );
}
