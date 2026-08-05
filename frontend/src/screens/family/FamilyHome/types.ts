export type FamilyHomeActivity = {
  tone: 'star' | 'level' | 'gift';
  glyph: string;
  title: string;
  meta: string;
  point: boolean;
  time: string;
};

export type FamilyHomeServiceIcon = 'markpoint' | 'schedule' | 'album' | 'todo';

export type FamilyHomeServiceTile = {
  id: string;
  label: string;
  sub: string;
  /** Mascot image + accent border — the frozen visual's one "primary" tile slot. */
  highlighted: boolean;
  /** False shows the "준비중" badge. Independent of `highlighted`: a family feature can be
   * real/available without being the primary tile, and the primary tile itself can be
   * unavailable (e.g. an inactive subscription). */
  available: boolean;
  icon: FamilyHomeServiceIcon;
};

export type FamilyHomeScreenModel = {
  greetingTitle: string;
  greetingSub: string;
  bellUnread: boolean;
  heroTitle: string;
  heroBody: string[];
  heroCtaLabel: string;
  activitiesTitle: string;
  activitiesMoreLabel: string;
  activities: FamilyHomeActivity[];
  servicesTitle: string;
  services: FamilyHomeServiceTile[];
};

export type FamilyHomeScreenProps = {
  model: FamilyHomeScreenModel;
  onHeroClick?: () => void;
  onActivityMore?: () => void;
  onServiceClick?: (id: string) => void;
  onBellClick?: () => void;
};
