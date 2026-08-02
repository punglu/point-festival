export type PopularPost = { rank: number; badge?: string; title: string; author: string; time: string; likes: number; comments: number };
export type PopularPostsModel = { title: string; subtitle: string; ranges: string[]; activeRange: string; posts: PopularPost[] };
export type PopularPostsProps = { model: PopularPostsModel; onSelect?: (rank: number) => void; onRangeChange?: (range: string) => void };
