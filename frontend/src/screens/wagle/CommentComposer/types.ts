export type CommentComposerPost = {
  badge: string;
  author: string;
  time: string;
  title: string;
  body: string;
};
export type CommentComposerComment = {
  author: string;
  message: string;
  time: string;
};
export type CommentComposerModel = {
  commentCount: number;
  post: CommentComposerPost;
  comments: CommentComposerComment[];
  placeholder: string;
  myInitial: string;
};
export type CommentComposerProps = {
  model: CommentComposerModel;
  onSubmit?: (text: string) => void;
  onCancel?: () => void;
};
