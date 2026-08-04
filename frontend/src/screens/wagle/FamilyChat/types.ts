export type FamilyChatConnectionState =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'recovering'
  | 'offline'
  | 'authorization_lost';

export type FamilyChatParticipant = { id: string; name: string };

export type FamilyChatMessage = {
  id: string;
  kind: 'own' | 'other' | 'service';
  authorName?: string;
  body: string | null;
  deleted: boolean;
  tombstone?: string | null;
  time: string;
  serviceBadge?: string | null;
  replyPreview?: string;
};

export type FamilyChatModel = {
  roomTitle: string;
  participants: FamilyChatParticipant[];
  connectionState: FamilyChatConnectionState;
  connectionLabel: string;
  messages: FamilyChatMessage[];
  draft: string;
  sending: boolean;
  sendError?: string | null;
  replyBannerText?: string | null;
};

export type FamilyChatProps = {
  model: FamilyChatModel;
  onBack?: () => void;
  onDraftChange?: (value: string) => void;
  onSend?: () => void;
  onReplyMessage?: (messageId: string) => void;
  onCancelReply?: () => void;
  onOpenSettings?: () => void;
  onOpenFiles?: () => void;
};
