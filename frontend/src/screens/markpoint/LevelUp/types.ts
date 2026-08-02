export type LevelUpModel = {
  playerInitial: string;
  playerName: string;
  level: number;
  levelTitle: string;
  bonusPoints: number;
};

export type LevelUpProps = {
  model: LevelUpModel;
  onConfirm?: () => void;
};
