export type WaglePreviewRoomKind = 'DIRECT' | 'GROUP' | 'SERVICE';

export interface WaglePreviewRoom {
  id: string;
  kind: WaglePreviewRoomKind;
  name: string;
  preview: string;
  time: string;
  unread?: number;
}

export type WaglePreviewMessageDirection = 'incoming' | 'outgoing';

export type WaglePreviewMessageReadState = 'sending' | 'sent' | 'read' | 'failed';

export interface WaglePreviewMessage {
  id: string;
  direction: WaglePreviewMessageDirection;
  text: string;
  timestamp: string;
  readState: WaglePreviewMessageReadState;
  // GROUP room에서만 의미가 있다 — 발신자가 항상 하나뿐인 DIRECT에서는 헤더의
  // 상대 Avatar로 이미 충분해 사용하지 않는다(Wave 6.0B CP-2/CP-6 판단 근거 참조).
  sender?: { name: string };
}

export interface WaglePreviewServiceEvent {
  source: string;
  timestamp: string;
  title: string;
  description: string;
  pointLabel: string;
  ariaLabel: string;
}

export type WaglePreviewPageState = 'normal' | 'loading' | 'empty' | 'error' | 'disabled' | 'read-only';
