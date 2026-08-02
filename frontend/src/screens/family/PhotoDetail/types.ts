export type PhotoDetailModel = {
  title: string;
  meta: string;
  likeCount: number;
  commentCount: number;
  commentAuthor: string;
  commentText: string;
};

export type PhotoDetailProps = {
  model: PhotoDetailModel;
  onClose?: () => void;
  onMenu?: () => void;
  onPrev?: () => void;
  onNext?: () => void;
};
