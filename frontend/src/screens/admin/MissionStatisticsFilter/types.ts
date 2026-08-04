export type MissionStatisticsFilterStatus = '전체' | '완료' | '진행 중';

export type MissionStatisticsFilterValue = {
  playerId: number | null;
  status: MissionStatisticsFilterStatus;
};

export type MissionStatisticsFilterPlayer = { id: number; name: string };

export type MissionStatisticsFilterProps = {
  players?: MissionStatisticsFilterPlayer[];
  value?: MissionStatisticsFilterValue;
  onApply?: (value: MissionStatisticsFilterValue) => void;
  onClose?: () => void;
};
