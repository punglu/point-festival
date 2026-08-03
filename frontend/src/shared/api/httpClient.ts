import axios from 'axios';

export const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

httpClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('accessToken');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * 로그인 API 경로 — 이 경로의 401은 전역 리다이렉트하지 않음.
 *
 * `/api/auth/account/login` was missing here (W7.5): a wrong Account
 * username/password returned a real 401, which the global handler read as
 * "session expired" and force-redirected to `/`, discarding the login
 * screen's own error state before it could render — found via real
 * end-to-end Playwright verification of the wrong-password path, not by
 * inspection.
 */
const AUTH_ENDPOINTS = ['/api/auth/login', '/api/auth/admin/login', '/api/auth/account/login'];

/**
 * MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.
 *
 * Optional personal Wagle features (device screen lock, Push subscription)
 * require an Account-native Session. A caller signed in only with a legacy
 * MarkPoint player token gets a 401 from them, and that is a correct,
 * *expected* answer — "this feature is not available to you", not "your
 * session died".
 *
 * Without this list the global handler treated that 401 as an expired session
 * and logged the user out on entering the Wagle screen. An optional feature
 * must never be able to end a session; probing for it must be free.
 */
const OPTIONAL_ACCOUNT_ENDPOINTS = ['/api/me/wagle/'];

httpClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const requestUrl = err.config?.url || '';

      // 로그인 API의 401은 "PIN/비밀번호 오류" → 호출자에게 에러 전달
      const isLoginRequest = AUTH_ENDPOINTS.some((ep) => requestUrl.includes(ep));
      // 선택 기능(Wagle 기기 잠금·Push)의 401은 "이 계정에는 해당 없음"이며
      // 세션 만료가 아니다 → 전역 로그아웃 금지, 호출자가 조용히 처리한다.
      const isOptionalAccountFeature = OPTIONAL_ACCOUNT_ENDPOINTS.some((ep) =>
        requestUrl.includes(ep),
      );

      if (!isLoginRequest && !isOptionalAccountFeature) {
        // 보호 API의 401은 "토큰 만료/무효" → 전역 세션 정리
        sessionStorage.setItem('mc_session_expired', '1'); // Auth 페이지에서 메시지 표시용
        sessionStorage.removeItem('accessToken');
        localStorage.removeItem('loggedInPlayer');
        localStorage.removeItem('rememberMe');
        window.location.href = '/';
      }
    }
    return Promise.reject(err);
  },
);
