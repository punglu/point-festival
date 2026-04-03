/**
 * 파비콘 동적 전환 유틸리티
 *
 * 사용법:
 *   import { setFavicon, setEventFavicon, resetFavicon } from '../shared/utils/favicon';
 *
 *   // 이벤트 발생 시 (예: 미읽은 알림)
 *   setEventFavicon();
 *
 *   // 원래대로 복원
 *   resetFavicon();
 */

const MAIN_FAVICON  = '/favicon-32x32.png';
const EVENT_FAVICON = '/favicon-event-32x32.png';
const MAIN_ICO      = '/favicon.ico';

/**
 * 특정 경로의 파비콘으로 변경
 */
export function setFavicon(pngHref: string, icoHref?: string): void {
  const pngLink = document.querySelector<HTMLLinkElement>(
    'link[rel="icon"][type="image/png"][sizes="32x32"]'
  );
  if (pngLink) {
    pngLink.href = pngHref;
  }

  if (icoHref) {
    const icoLink = document.querySelector<HTMLLinkElement>(
      'link[rel="icon"][sizes="48x48"]'
    );
    if (icoLink) {
      icoLink.href = icoHref;
    }
  }
}

/**
 * 이벤트 파비콘으로 전환
 */
export function setEventFavicon(): void {
  setFavicon(EVENT_FAVICON);
}

/**
 * 메인 파비콘으로 복원
 */
export function resetFavicon(): void {
  setFavicon(MAIN_FAVICON, MAIN_ICO);
}
