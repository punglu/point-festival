import { PopularPostsScreen, popularPostsFixture } from '../../screens/wagle/PopularPosts';
export function PopularPostsPreview() {
  return <PopularPostsScreen model={popularPostsFixture} onSelect={() => undefined} onRangeChange={() => undefined} />;
}
