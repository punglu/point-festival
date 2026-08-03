import MainLogo from '../../../shared/components/MainLogo';
import styles from './OnboardingScreen.module.css';
import type { OnboardingProps } from './types';

export function OnboardingScreen({ model, onFamilyNameChange, onNext, onHaveInviteCode }: OnboardingProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1r">
      <div className={styles.hero}>
        <MainLogo variant="smile" tone="default" size="welcome" className={styles.logo} />
        <h1>
          우리 가족만의
          <br />
          공간을 만들어보세요
        </h1>
        <p>1분이면 충분해요</p>
      </div>
      <div className={styles.card}>
        <div className={styles.progress}>
          <i className={styles.on} />
          <i />
          <i />
        </div>
        <span className={styles.step}>1단계 · 가족 이름 정하기</span>
        <label className={styles.field}>
          <span>가족 이름</span>
          <input
            className={styles.input}
            value={model.familyName}
            onChange={(e) => onFamilyNameChange?.(e.target.value)}
          />
        </label>
        <label className={styles.field}>
          <span>가족 대표 이미지 (선택)</span>
          <div className={styles.upload}>
            <i>▤</i>
            <b>사진 올리기</b>
          </div>
        </label>
        <div className={styles.notice}>
          <i>🛡</i>
          <span>다음 단계에서 가족 구성원을 초대할 수 있어요.</span>
        </div>
        {model.errorMessage && <div className={styles.error}>{model.errorMessage}</div>}
        <button type="button" className={styles.next} onClick={onNext} disabled={model.isSubmitting}>
          {model.isSubmitting ? '만드는 중…' : <>다음 <b>›</b></>}
        </button>
        <button type="button" className={styles.secondary} onClick={onHaveInviteCode}>
          이미 초대 코드가 있어요
        </button>
      </div>
    </main>
  );
}
