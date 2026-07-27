import type { DoranPreviewPageState } from './types';

const PREVIEWABLE_STATES: readonly DoranPreviewPageState[] = ['normal', 'loading', 'empty', 'error'];

/**
 * 실제 API가 없는 정적 Gate 단계에서 loading/empty/error 상태를 PM 리뷰
 * 목적으로 확인하기 위한 preview 전용 resolver.
 *
 * 사용자에게 노출되는 선택 UI(버튼/드롭다운 등)를 만들지 않고, 문서화되지 않은
 * 쿼리 파라미터 값 하나만 읽는다. 값이 없거나 허용 목록에 없으면 항상 'normal'.
 * 'disabled'는 이 resolver의 대상이 아니다 — 실제 serviceStatus에서만 파생되며
 * 이 preview 값으로 대체되지 않는다(§9.2, 실제 API state 우선 원칙).
 *
 * Wave 3.1 M4: page-level 'read-only'는 미승인 정책이라 지원 목록에서 제거했다.
 * SERVICE room의 read-only는 room.kind==='SERVICE' 판정으로만 독립 유지되며,
 * DoranPreviewPageState 원본 타입(A source contract)은 변경하지 않는다 —
 * 'read-only' 쿼리 값은 단순히 미지원 값과 동일하게 'normal'로 수렴할 뿐이다.
 */
export function resolvePreviewPageState(rawValue: string | null): DoranPreviewPageState {
  if (!rawValue) return 'normal';
  const match = PREVIEWABLE_STATES.find((state) => state === rawValue);
  return match ?? 'normal';
}
