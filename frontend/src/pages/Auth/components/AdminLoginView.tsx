import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from '../Auth.module.css';
import { adminLogin } from '../api/authApi';
import { useAuthStore } from '../../../shared/stores/useAuthStore';

interface Props {
  onBack: () => void;
}

export default function AdminLoginView({ onBack }: Props) {
  const navigate = useNavigate();
  const { adminLogin: storeAdminLogin } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      const res = await adminLogin(username, password, abortRef.current.signal);
      storeAdminLogin(res);
      navigate('/admin');
    } catch (err: unknown) {
      const httpErr = err as { response?: { data?: { detail?: string } }; name?: string };
      if (httpErr.name === 'AbortError' || httpErr.name === 'CanceledError') return;
      const detail = httpErr.response?.data?.detail || '아이디 또는 비밀번호가 올바르지 않습니다.';
      setError(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.authView}>
      {/* Indigo 헤더 */}
      <div className={styles.adminHeader}>
        <div className={styles.adminIcon}>⚙️</div>
        <h1 className={styles.authTitle}>관리자 로그인</h1>
        <p className={styles.authSubtitle}>관리자 계정으로 로그인하세요</p>
      </div>

      {/* 로그인 폼 */}
      <div className={styles.adminForm}>
        <form onSubmit={handleSubmit} className={styles.loginForm}>
          <div className={styles.formGroup}>
            <label className={styles.formLabel}>아이디</label>
            <input
              type="text"
              placeholder="아이디 입력"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.adminFormInput}
              autoComplete="username"
            />
          </div>
          <div className={styles.formGroup}>
            <label className={styles.formLabel}>비밀번호</label>
            <input
              type="password"
              placeholder="비밀번호 입력"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.adminFormInput}
              autoComplete="current-password"
            />
          </div>

          {error && <div className={styles.errorMessage}>{error}</div>}

          <button
            type="submit"
            className={styles.adminFormButton}
            disabled={isLoading || !username || !password}
          >
            {isLoading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <button className={styles.backLink} onClick={onBack}>
          ← 플레이어 선택으로
        </button>
      </div>
    </div>
  );
}
