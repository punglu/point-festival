/**
 * 날짜 유틸리티 — 전체 FE에서 이 함수들만 사용하라.
 * toISOString().slice(0,10) 직접 사용 금지.
 * toISOString()은 UTC 기준이라 KST 오전 9시 이전에 어제가 반환되는 문제가 있음.
 */

/** Date 객체를 로컬 시간 기준 YYYY-MM-DD 문자열로 변환 */
export function formatDate(d: Date): string {
  const year  = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day   = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/** 로컬 시간 기준 오늘 날짜 문자열 (YYYY-MM-DD) */
export function getLocalToday(): string {
  return formatDate(new Date());
}

/** YYYY-MM-DD 문자열을 로컬 Date 객체로 파싱 */
export function parseDate(dateStr: string): Date {
  const [y, m, d] = dateStr.split('-').map(Number);
  return new Date(y, m - 1, d);
}

/**
 * 주어진 날짜가 속한 주의 월요일을 반환 (로컬 시간 기준)
 * 인자 생략 시 오늘 기준
 */
export function getMonday(d: Date = new Date()): string {
  const result = new Date(d);
  const day  = result.getDay(); // 0=일, 1=월, ..., 6=토
  const diff = day === 0 ? -6 : 1 - day;
  result.setDate(result.getDate() + diff);
  return formatDate(result);
}

/** 주어진 월요일(YYYY-MM-DD)로부터 7일간의 날짜 배열 생성 */
export function getWeekDates(mondayStr: string): string[] {
  const monday = parseDate(mondayStr);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return formatDate(d);
  });
}

/** 주간 이동: weekStart에서 +/- N주 */
export function shiftWeek(mondayStr: string, weeks: number): string {
  const d = parseDate(mondayStr);
  d.setDate(d.getDate() + weeks * 7);
  return formatDate(d);
}

/** 주간 범위 라벨 (YYYY.MM.DD ~ YYYY.MM.DD) */
export function getWeekLabel(mondayStr: string): string {
  const start = parseDate(mondayStr);
  const end   = new Date(start);
  end.setDate(start.getDate() + 6);
  const fmt = (d: Date) =>
    `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
  return `${fmt(start)} ~ ${fmt(end)}`;
}

/** 어제 날짜 (YYYY-MM-DD) */
export function getYesterday(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return formatDate(d);
}

/** N일 후 날짜 (YYYY-MM-DD) */
export function shiftDay(dateStr: string, days: number): string {
  const d = parseDate(dateStr);
  d.setDate(d.getDate() + days);
  return formatDate(d);
}
