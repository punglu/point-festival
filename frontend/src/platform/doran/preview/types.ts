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
