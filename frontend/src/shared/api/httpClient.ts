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

/** 로그인 API 경로 — 이 경로의 401은 전역 리다이렉트하지 않음 */
const AUTH_ENDPOINTS = ['/api/auth/login', '/api/auth/admin/login'];

httpClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const requestUrl = err.config?.url || '';

      // 로그인 API의 401은 "PIN/비밀번호 오류" → 호출자에게 에러 전달
      const isLoginRequest = AUTH_ENDPOINTS.some((ep) => requestUrl.includes(ep));

      if (!isLoginRequest) {
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
