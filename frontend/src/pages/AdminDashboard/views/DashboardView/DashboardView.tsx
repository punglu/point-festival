import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLocalToday, getWeekLabel, getMonday } from '../../../../shared/utils/dateUtils';
import styles from './DashboardView.module.css';
import { useAdminData } from '../../hooks/useAdminData';
import StatCard from '../../components/StatCard/StatCard';
import PlayerStatusCard from './components/PlayerStatusCard';
import PendingMissionCard from './components/PendingMissionCard';
import WeeklyActivityChart from './components/WeeklyActivityChart';
import RecentAlerts from './components/RecentAlerts';
import MissionRanking from './components/MissionRanking';
import CardDetailTable from './components/CardDetailTable';
import BalanceSection from './components/BalanceSection';

type CardMode = 'points' | 'active' | 'pending' | 'completed';

export default function DashboardView() {
  const navigate = useNavigate();
  const {
    players, missions, notifications, dailyPoints,
    stats, missionRanking, cycle, loading, reload,
  } = useAdminData();

  const today     = getLocalToday();
  const weekRange = getWeekLabel(getMonday());

  const [selectedCard, setSelectedCard] = useState<CardMode | null>(null);

  const handleCardClick = (mode: CardMode) => {
    setSelectedCard(prev => prev === mode ? null : mode);
  };

  const cycleLabel = useMemo(() => {
    if (!cycle?.startDate || !cycle?.endDate) return '';
    const fmt = (d: string) => d.replace(/-/g, '.');
    return `${fmt(cycle.startDate)} ~ ${fmt(cycle.endDate)}`;
  }, [cycle]);

  const childPlayers = useMemo(() => {
    return players.filter(p => p.role === 'player');
  }, [players]);

  if (loading) {
    return <div className={styles.loading}>데이터 로딩 중...</div>;
  }

  return (
    <div className={styles.view}>
      {/* 헤더 */}
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <h1 className={styles.title}>
            대시보드
            <span className={styles.weekRange}>{weekRange}</span>
          </h1>
          <p className={styles.dateText}>{today}</p>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.btnRefresh} onClick={reload}>새로고침</button>
          <button className={styles.btnNew} onClick={() => navigate('/admin/missions')}>
            + 새 미션
          </button>
        </div>
      </div>

      {/* 스탯 카드 4종 — 순서: 총 발행 → 활성 → 승인대기 → 완료 */}
      <div className={`${styles.statGrid} ${selectedCard ? styles.statGridHasSelection : ''}`}>
        <div
          className={`${styles.statCardWrap} ${selectedCard === 'points' ? styles.statCardSelected : ''}`}
          onClick={() => handleCardClick('points')}
        >
          <StatCard
            label="총 발행 포인트"
            value={`${stats.totalPointsIssued}pt`}
            subtext={cycle.label}
          />
        </div>
        <div
          className={`${styles.statCardWrap} ${selectedCard === 'active' ? styles.statCardSelected : ''}`}
          onClick={() => handleCardClick('active')}
        >
          <StatCard
            label="활성 미션"
            value={stats.totalActiveMissions}
            subtext={`오늘 ${stats.todayNewMissions}건`}
          />
        </div>
        <div
          className={`${styles.statCardWrap} ${selectedCard === 'pending' ? styles.statCardSelected : ''}`}
          onClick={() => handleCardClick('pending')}
        >
          <StatCard
            label="승인 대기"
            value={stats.pendingApproval}
            subtext={stats.pendingApproval > 0 ? '확인 필요' : '모두 처리됨'}
            subtextColor={stats.pendingApproval > 0 ? '#D97706' : '#059669'}
          />
        </div>
        <div
          className={`${styles.statCardWrap} ${selectedCard === 'completed' ? styles.statCardSelected : ''}`}
          onClick={() => handleCardClick('completed')}
        >
          <StatCard
            label="이번 주기 완료"
            value={stats.completedThisWeek}
            subtext={`목표 ${stats.weeklyGoal}건`}
          />
        </div>
      </div>

      {/* 상세 테이블 패널 (선택된 카드가 있을 때만) */}
      {selectedCard && (
        <div className={styles.detailPanel}>
          <CardDetailTable
            mode={selectedCard}
            missions={missions}
            players={players}
            cycleLabel={cycleLabel}
          />
        </div>
      )}

      {/* 1. 플레이어 현황 */}
      <PlayerStatusCard
        players={players}
        missions={missions}
        dailyPoints={dailyPoints}
      />

      {/* 2. 밸런싱 섹션 */}
      <BalanceSection missions={missions} players={childPlayers} />

      {/* 3. 최근 알림 */}
      <RecentAlerts notifications={notifications} />

      {/* 4. 승인 대기 미션 */}
      <PendingMissionCard missions={missions} players={players} />

      {/* 5. 이번 주 활동 랭킹 */}
      <WeeklyActivityChart missions={missions} players={players} cycle={cycle} />
      <MissionRanking ranking={missionRanking} players={players} cycle={cycle} />
    </div>
  );
}
