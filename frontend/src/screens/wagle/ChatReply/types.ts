export type ChatReplyBackgroundMessage = { tone: 'in' | 'out'; text: string };

export type ChatReplyModel = {
  roomTitle: string;
  backgroundMessages: ChatReplyBackgroundMessage[];
  quotedAuthor: string;
  quotedText: string;
  draftText: string;
};

export type ChatReplyProps = {
  model: ChatReplyModel;
  onReply?: () => void;
  onReact?: () => void;
  onCopy?: () => void;
  onReport?: () => void;
  onCancelQuote?: () => void;
  onDraftChange?: (value: string) => void;
  onSend?: () => void;
};
