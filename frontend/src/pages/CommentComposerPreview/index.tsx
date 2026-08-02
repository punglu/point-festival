import { CommentComposerScreen, commentComposerFixture } from '../../screens/wagle/CommentComposer';
export function CommentComposerPreview() {
  return <CommentComposerScreen model={commentComposerFixture} onCancel={() => undefined} onSubmit={() => undefined} />;
}
