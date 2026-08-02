export type BoardPost = { badge: string; badgeTone: 'blue' | 'yellow' | 'green'; author: string; time: string; title: string; summary: string; likes: number; comments: number };
export type FamilyBoardModel = { subtitle: string; tabs: string[]; activeTab: string; posts: BoardPost[] };
export type FamilyBoardProps = { model: FamilyBoardModel; onWrite?: () => void; onBack?: () => void; onTab?: (tab: string) => void; onSelectPost?: (post: BoardPost) => void };
