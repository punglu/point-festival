import styles from './ProfileEditScreen.module.css';
import type { ProfileEditProps } from './types';
export function ProfileEditScreen({ model, onBack, onSave }: ProfileEditProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="2z" data-canonical-screen-label="프로필 편집" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>✕</button>
        <h1>프로필 편집</h1>
        <button type="button" className={styles.done} onClick={onSave}>완료</button>
      </header>
      <div className={styles.avatarWrap}>
        <div className={styles.avatar}>
          {model.name.slice(0, 1)}
          <span className={styles.editBadge}>✎</span>
        </div>
        <span className={styles.avatarLabel}>사진 변경</span>
      </div>
      <label className={styles.field}>
        <span>이름</span>
        <div className={styles.input}>{model.name}</div>
      </label>
      <div className={styles.field}>
        <span>닉네임 색상</span>
        <div className={styles.colors}>
          {model.colors.map((c) => (
            <i key={c.value} className={c.selected ? styles.colorOn : styles.color} style={{ background: c.value }} />
          ))}
        </div>
      </div>
      <label className={styles.field}>
        <span>한 줄 소개</span>
        <div className={styles.bio}>{model.bio}</div>
      </label>
      <div className={styles.card}>
        <div className={styles.row}><span>생일</span><em>{model.birthday}</em></div>
        <div className={styles.row}><span>가족 내 역할</span><em>{model.familyRole}</em></div>
      </div>
      <button type="button" className={styles.save} onClick={onSave}>저장하기</button>
    </main>
  );
}
