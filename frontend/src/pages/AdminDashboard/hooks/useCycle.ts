import { useMemo } from 'react';

export interface CycleInfo {
  startDate: string;
  endDate: string;
  displayStart: string;
  displayEnd: string;
  label: string;
}

/**
 * 포인트 주기 계산 훅
 * 매주 월요일 시작, 일요일 23:30 마감
 */
export function useCycle(referenceDate?: string): CycleInfo {
  return useMemo(() => {
    const ref = referenceDate ? new Date(referenceDate) : new Date();
    const day = ref.getDay(); // 0=일, 1=월, ...

    // 월요일 기준으로 이번 주 시작일 계산
    const diff = day === 0 ? -6 : 1 - day;
    const monday = new Date(ref);
    monday.setDate(ref.getDate() + diff);

    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);

    const fmt    = (d: Date) => d.toISOString().slice(0, 10);
    const fmtDot = (d: Date) => fmt(d).replace(/-/g, '.');

    return {
      startDate:    fmt(monday),
      endDate:      fmt(sunday),
      displayStart: fmtDot(monday),
      displayEnd:   fmtDot(sunday),
      label:        `이번 주기 (${fmtDot(monday)} ~ ${fmtDot(sunday)})`,
    };
  }, [referenceDate]);
}
