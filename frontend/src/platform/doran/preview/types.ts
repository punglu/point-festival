export type DoranPreviewRoomKind = 'DIRECT' | 'GROUP' | 'SERVICE';

export interface DoranPreviewRoom {
  id: string;
  kind: DoranPreviewRoomKind;
  name: string;
  preview: string;
  time: string;
  unread?: number;
}

export type DoranPreviewMessageDirection = 'incoming' | 'outgoing';

export type DoranPreviewMessageReadState = 'sending' | 'sent' | 'read' | 'failed';

export interface DoranPreviewMessage {
  id: string;
  direction: DoranPreviewMessageDirection;
  text: string;
  timestamp: string;
  readState: DoranPreviewMessageReadState;
  // GROUP room에서만 의미가 있다 — 발신자가 항상 하나뿐인 DIRECT에서는 헤더의
  // 상대 Avatar로 이미 충분해 사용하지 않는다(Wave 6.0B CP-2/CP-6 판단 근거 참조).
  sender?: { name: string };
}

export interface DoranPreviewServiceEvent {
  source: string;
  timestamp: string;
  title: string;
  description: string;
  pointLabel: string;
  ariaLabel: string;
}

export type DoranPreviewPageState = 'normal' | 'loading' | 'empty' | 'error' | 'disabled' | 'read-only';
