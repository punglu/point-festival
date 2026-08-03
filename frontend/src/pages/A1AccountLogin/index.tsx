import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLogo from '../../shared/components/MainLogo';
import { accountLogin } from '../../shared/api/accountAuthApi';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import styles from './A1AccountLogin.module.css';

function PersonIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8.2" r="3.4" /><path d="M5.4 19.6c1.4-3.7 3.9-5.5 6.6-5.6 2.7 0 5.2 1.9 6.6 5.6" /></svg>;
}

function LockIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><rect x="4.8" y="10.4" width="14.4" height="9.4" rx="2.6" /><path d="M8.4 10.4V7.8a3.6 3.6 0 0 1 7.2 0v2.6" /></svg>;
}

function EyeIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><path d="M2.8 12S6.4 6.2 12 6.2 21.2 12 21.2 12 17.6 17.8 12 17.8 2.8 12 2.8 12z" /><circle cx="12" cy="12" r="2.6" /></svg>;
}

function AddProfileIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><circle cx="9" cy="8.6" r="3.2" /><path d="M3.4 19.4c1.3-3.4 3.3-5 5.6-5s4.3 1.6 5.6 5" /><path d="M16.6 8h4.2M18.7 5.9v4.2" /></svg>;
}

function ShieldIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><path d="M12 3.6 19 6v6.2c0 4.2-2.8 6.9-7 8.2-4.2-1.3-7-4-7-8.2V6z" /><path d="M9.3 12.1l1.9 1.9 3.5-3.6" /></svg>;
}

/**
 * canonical 1a-1. W7.5: this form's submit was intentionally parked at A1
 * (`event.preventDefault()` only, no real login call) — now wired to the
 * real `POST /api/auth/account/login` via the already-built-but-orphaned
 * `shared/api/accountAuthApi.ts` (built in Wave 6 Target UI, never actually
 * called from any component before this). W7.5 Matrix `1a-1`:
 * FRONTEND_ADAPTER_REQUIRED -> WIRED_AND_VERIFIED.
 */
export default function A1AccountLoginPage() {
  const navigate = useNavigate();
  const setAccountLogin = useAuthStore((state) => state.accountLogin);
  const [accountId, setAccountId] = useState('');
  const [password, setPassword] = useState('');
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [rememberLogin, setRememberLogin] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const noOp = () => undefined;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!accountId.trim() || !password) {
      setErrorMessage('아이디와 비밀번호를 입력해주세요.');
      return;
    }
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const result = await accountLogin(accountId.trim(), password);
      setAccountLogin(result);
      navigate('/family');
    } catch {
      setErrorMessage('아이디 또는 비밀번호가 일치하지 않아요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className={styles.page} data-implementation-mode="ui-only" data-canonical-screen-id="1a-1">
      <header className={styles.hero}>
        <MainLogo variant="wordmark" tone="default" size={150} className={styles.logo} />
        <div className={styles.logoHalo} aria-hidden="true" />
        <h1 data-canonical-element="service-title">가족 플랫폼</h1>
        <p data-canonical-element="service-subtitle">아이디로 로그인하고 우리 가족과 연결돼요</p>
      </header>

      <form className={styles.sheet} onSubmit={handleSubmit}>
        <div className={styles.heading}>
          <h2 data-canonical-element="form-title">로그인</h2>
          <p>가족 계정 아이디와 비밀번호를 입력해 주세요.</p>
        </div>

        <label className={styles.fieldGroup}>
          <span className={styles.label} data-canonical-element="field-label">아이디</span>
          <span className={styles.field}>
            <span className={styles.leadingIcon}><PersonIcon /></span>
            <input data-testid="account-username" value={accountId} onChange={(event) => setAccountId(event.target.value)} autoComplete="username" aria-label="아이디" />
          </span>
        </label>

        <label className={styles.fieldGroup}>
          <span className={styles.label} data-canonical-element="field-label">비밀번호</span>
          <span className={styles.passwordField}>
            <span className={`${styles.leadingIcon} ${styles.passwordIcon}`}><LockIcon /></span>
            <input data-testid="account-password" value={password} onChange={(event) => setPassword(event.target.value)} type={passwordVisible ? 'text' : 'password'} autoComplete="current-password" aria-label="비밀번호" />
            <button className={styles.visibilityButton} type="button" onClick={() => setPasswordVisible((visible) => !visible)} aria-label={passwordVisible ? '비밀번호 숨기기' : '비밀번호 보기'}><EyeIcon /></button>
          </span>
          {errorMessage && (
            <span className={styles.error} data-canonical-element="error-text" role="status"><i aria-hidden="true">!</i>{errorMessage}</span>
          )}
        </label>

        <div className={styles.options}>
          <button className={styles.rememberButton} type="button" onClick={() => setRememberLogin((checked) => !checked)} aria-pressed={rememberLogin}>
            <span className={styles.checkbox} aria-hidden="true">{rememberLogin ? '✓' : ''}</span>로그인 상태 유지
          </button>
          <button className={styles.textAction} type="button" onClick={noOp}>비밀번호 찾기</button>
        </div>

        <button className={styles.submit} data-canonical-element="primary-button" data-testid="account-login-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? '로그인 중…' : '로그인'}</button>

        <div className={styles.divider} aria-hidden="true"><span /><em>또는</em><span /></div>

        <button className={styles.secondary} data-canonical-element="secondary-button" type="button" onClick={noOp}><AddProfileIcon />프로필 선택으로 돌아가기</button>

        <aside className={styles.notice}>
          <span className={styles.noticeIcon}><ShieldIcon /></span>
          <span className={styles.noticeCopy}><strong>가족 계정은 관리자 승인 후 사용할 수 있어요.</strong><span>아이디를 잊었다면 관리자에게 문의해 주세요.</span></span>
        </aside>

        <footer className={styles.footer} data-canonical-element="footer">
          <span>v1.0.0 · 가족 플랫폼</span>
          <button type="button" onClick={noOp}>관리자 로그인 <b aria-hidden="true">›</b></button>
        </footer>
      </form>
    </main>
  );
}
