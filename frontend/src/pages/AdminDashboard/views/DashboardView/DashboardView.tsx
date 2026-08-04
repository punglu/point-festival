import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

import styles from './DashboardView.module.css';
import { useAdminData } from '../../hooks/useAdminData';
import PlayerStatusCard from './components/PlayerStatusCard';
import PendingMissionCard from './components/PendingMissionCard';
import WeeklyActivityChart from './components/WeeklyActivityChart';
import RecentAlerts from './components/RecentAlerts';
import MissionRanking from './components/MissionRanking';
import CardDetailTable from './components/CardDetailTable';
import BalanceSection from './components/BalanceSection';
import ActiveMissionDetailModal from './components/ActiveMissionDetailModal';
import { MissionStatisticsFilterScreen } from '../../../../screens/admin/MissionStatisticsFilter';
import type { MissionStatisticsFilterValue } from '../../../../screens/admin/MissionStatisticsFilter';
import { MissionApprovalScreen } from '../../../../screens/admin/MissionApproval';
import type { MissionApprovalModel } from '../../../../screens/admin/MissionApproval';
import { MissionStatisticsDashboardScreen } from '../../../../screens/admin/MissionStatisticsDashboard';
import type { MissionStatisticsDashboardModel } from '../../../../screens/admin/MissionStatisticsDashboard';
import { ParentDashboardScreen } from '../../../../screens/admin/ParentDashboard';
import type { ParentDashboardModel, ParentDashboardStatCardKey } from '../../../../screens/admin/ParentDashboard';
import type { MissionRankItem } from '../../types/admin.types';
import { getLocalToday } from '../../../../shared/utils/dateUtils';

// canonical 2i (보호자 대시보드) -- W7.4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001:
// this Product Container now renders the expanded canonical Screen as its
// outer shell (header/cycle banner/stat cards, all real). The real
// product's 6 dashboard sections (PlayerStatusCard/BalanceSection/
// RecentAlerts/PendingMissionCard/WeeklyActivityChart/MissionRanking) are
// composed as named slots exactly as before -- none of their own internal
// data/interaction logic changed. The 4 canonical overlays this Container
// already wired (1m/2m/2x/3b) move into `overlaysSlot`, unchanged.
export default function DashboardView() {
  const navigate = useNavigate();
  const {
    players, missions, notifications, dailyPoints,
    stats, missionRanking, cycle, loading, reload,
    approveMission, rejectMission,
  } = useAdminData();

  const [selectedCard, setSelectedCard] = useState<ParentDashboardStatCardKey | null>(null);
  const [showStatsFilter, setShowStatsFilter] = useState(false);
  const [showActiveDetail, setShowActiveDetail] = useState(false);
  const [showApprovalQueue, setShowApprovalQueue] = useState(false);
  const [showStatsDashboard, setShowStatsDashboard] = useState(false);
  const [rankingFilter, setRankingFilter] = useState<MissionStatisticsFilterValue>({
    playerId: null,
    status: '전체',
  });

  const handleCardClick = (mode: ParentDashboardStatCardKey) => {
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

  // canonical 3b (미션 통계 필터): 가족 구성원 필터는 MissionRanking이 이미 갖고
  // 있던 실제 필터를 controlled prop으로 끌어올려 공유한다. 상태 필터는 '진행 중'
  // 선택 시에만 의미가 달라진다 — '미션 랭킹'은 원래 완료 미션 집계이므로 '전체'와
  // '완료'는 같은 결과를 낸다(실제 상태). '기간'은 여전히 실제 API가 없어 비활성.
  const activeRanking: MissionRankItem[] = useMemo(() => {
    const countMap: Record<string, { total: number; players: Record<string, number> }> = {};
    missions
      .filter((m) => m.status === 'active')
      .forEach((m) => {
        const playerName = players.find((p) => p.id === m.player_id)?.name ?? '?';
        if (!countMap[m.text]) countMap[m.text] = { total: 0, players: {} };
        countMap[m.text].total++;
        countMap[m.text].players[playerName] = (countMap[m.text].players[playerName] ?? 0) + 1;
      });
    return Object.entries(countMap)
      .map(([text, data]) => ({ text, totalCount: data.total, playerCounts: data.players }))
      .sort((a, b) => b.totalCount - a.totalCount)
      .slice(0, 8);
  }, [missions, players]);

  const rankingToShow = rankingFilter.status === '진행 중' ? activeRanking : missionRanking;

  // canonical 1m (미션 승인 대기함): PendingMissionCard는 이미 상위 4건을
  // 미리보기했지만 실제 승인/반려 액션이 없었다(전체 보기 -> /admin/missions로
  // 이탈만 함). 여기서 real pending_approval 전체를 실제 승인/반려 액션과 함께
  // 보여준다. '오늘 승인/반려' 카운트는 오늘 갱신된 completed/rejected 미션 수.
  const today = getLocalToday();
  const approvalModel: MissionApprovalModel = useMemo(() => {
    const pending = missions.filter((m) => m.status === 'pending_approval');
    const approvedToday = missions.filter((m) => m.status === 'completed' && m.updated_at?.slice(0, 10) === today).length;
    const rejectedToday = missions.filter((m) => m.status === 'rejected' && m.updated_at?.slice(0, 10) === today).length;
    return {
      pendingCount: pending.length,
      approvedTodayCount: approvedToday,
      rejectedTodayCount: rejectedToday,
      pendingPoints: pending.reduce((sum, m) => sum + m.point, 0),
      items: pending.map((m) => ({
        id: m.id,
        playerName: players.find((p) => p.id === m.player_id)?.name ?? '?',
        title: m.text,
        meta: `${m.date} 제출 · +${m.point}P`,
      })),
    };
  }, [missions, players, today]);

  // canonical 2x (미션 통계 대시보드): 대시보드가 이미 계산해 둔 실 데이터
  // (stats.cycleRate/totalActiveMissions, childPlayers별 이번 주기 완료율)를
  // 그대로 재사용한다 — 새 통계 엔진을 만들지 않는다.
  const statsDashboardModel: MissionStatisticsDashboardModel = useMemo(() => {
    const cyclePoints = missions
      .filter((m) => m.status === 'completed' && m.date >= cycle.startDate && m.date <= cycle.endDate)
      .reduce((sum, m) => sum + m.point, 0);
    const members = childPlayers.map((p) => {
      const pm = missions.filter((m) => m.player_id === p.id && m.date >= cycle.startDate && m.date <= cycle.endDate);
      const rate = pm.length > 0 ? Math.round((pm.filter((m) => m.status === 'completed').length / pm.length) * 100) : 0;
      return { name: p.name, value: rate };
    });
    return {
      title: cycleLabel ? `이번 주기 미션 통계 (${cycleLabel})` : '이번 주기 미션 통계',
      completion: `${stats.cycleRate}%`,
      active: `${stats.totalActiveMissions}건`,
      points: `${cyclePoints}P`,
      members,
    };
  }, [missions, childPlayers, cycle, cycleLabel, stats.cycleRate, stats.totalActiveMissions]);

  // canonical 2i (보호자 대시보드): 실제 4개 스탯 카드를 canonical의 typed
  // statCards 계약으로 노출한다 -- 값은 useAdminData가 이미 계산해 둔 것 그대로.
  const dashboardModel: ParentDashboardModel = useMemo(() => ({
    title: '안녕하세요, 관리자님',
    cycleLabel,
    selectedStatCard: selectedCard,
    statCards: [
      { key: 'points', label: '이번 주기 진행률', value: `${stats.cycleRate}%`, subtext: `완료 ${stats.completedThisWeek} / 전체 ${stats.cycleTotal}` },
      { key: 'active', label: '활성 미션', value: stats.totalActiveMissions, subtext: `오늘 ${stats.todayNewMissions}건` },
      {
        key: 'pending', label: '승인 대기', value: stats.pendingApproval,
        subtext: stats.pendingApproval > 0 ? '확인 필요' : '모두 처리됨',
        subtextColor: stats.pendingApproval > 0 ? '#D97706' : '#059669',
      },
      { key: 'completed', label: '이번 주기 완료', value: stats.completedThisWeek, subtext: `목표 ${stats.weeklyGoal}건` },
    ],
  }), [cycleLabel, selectedCard, stats]);

  if (loading) {
    return <div className={styles.loading}>데이터 로딩 중...</div>;
  }

  return (
    <ParentDashboardScreen
      model={dashboardModel}
      embedded
      onRefresh={reload}
      onOpenMissions={() => navigate('/admin/missions')}
      onSelectStatCard={handleCardClick}
      detailPanelSlot={
        selectedCard && (
          <>
            {selectedCard === 'active' && (
              <button type="button" className={styles.filterButton} onClick={() => setShowActiveDetail(true)}>
                활성 미션 상세 보기
              </button>
            )}
            {selectedCard === 'points' && (
              <button type="button" className={styles.filterButton} onClick={() => setShowStatsDashboard(true)}>
                미션 통계 대시보드 보기
              </button>
            )}
            <CardDetailTable
              mode={selectedCard}
              missions={missions}
              players={players}
              cycleLabel={cycleLabel}
            />
          </>
        )
      }
      playerStatusSlot={
        <PlayerStatusCard players={players} missions={missions} dailyPoints={dailyPoints} />
      }
      balanceSlot={
        <BalanceSection missions={missions} players={childPlayers} cycleLabel={cycleLabel} />
      }
      alertsSlot={<RecentAlerts notifications={notifications} />}
      pendingMissionSlot={
        <PendingMissionCard missions={missions} players={players} onViewAll={() => setShowApprovalQueue(true)} />
      }
      weeklyActivitySlot={
        <>
          <WeeklyActivityChart missions={missions} players={players} cycle={cycle} />
          <div className={styles.rankingHeader}>
            <button type="button" className={styles.filterButton} onClick={() => setShowStatsFilter(true)}>
              통계 필터
            </button>
          </div>
        </>
      }
      rankingSlot={
        <MissionRanking
          ranking={rankingToShow}
          players={players}
          cycle={cycle}
          selectedPlayer={rankingFilter.playerId}
          onSelectPlayer={(id) => setRankingFilter((f) => ({ ...f, playerId: id }))}
        />
      }
      overlaysSlot={
        <>
          {/* 활성 미션 상세 리스트 (실제 미션 조회 기능, canonical 대응 없음).
              행 클릭 시 canonical 2m (MissionDetailFormScreen, embedded)이
              실제 미션 데이터로 열리고 onDelete가 실제
              adminApi.deleteMission을 호출한다. */}
          <ActiveMissionDetailModal
            open={showActiveDetail}
            onClose={() => setShowActiveDetail(false)}
            missions={missions}
            players={players}
            cycle={cycle}
            onChanged={reload}
          />

          {showStatsDashboard && (
            <div className={styles.overlay} data-testid="admin-mission-stats-dashboard-overlay">
              <MissionStatisticsDashboardScreen
                embedded
                model={statsDashboardModel}
                onClose={() => setShowStatsDashboard(false)}
                onOpenFilter={() => { setShowStatsDashboard(false); setShowStatsFilter(true); }}
              />
            </div>
          )}

          {showApprovalQueue && (
            <div className={styles.overlay} data-testid="admin-mission-approval-overlay">
              <MissionApprovalScreen
                embedded
                model={approvalModel}
                onClose={() => setShowApprovalQueue(false)}
                onApprove={(id) => void approveMission(id)}
                onReject={(id) => void rejectMission(id)}
              />
            </div>
          )}

          {showStatsFilter && (
            <div className={styles.overlay} data-testid="admin-mission-stats-filter-overlay">
              {/* canonical 3b (미션 통계 필터) — 가족 구성원/미션 상태는 실제
                  필터다 (MissionRanking과 공유하는 rankingFilter state;
                  '진행 중'은 실제 active 미션에서 새로 집계). '기간'은 여전히
                  실제 API가 없어 비활성 상태로 disclosed. */}
              <MissionStatisticsFilterScreen
                players={childPlayers.map((p) => ({ id: p.id, name: p.name }))}
                value={rankingFilter}
                onClose={() => setShowStatsFilter(false)}
                onApply={(value) => { setRankingFilter(value); setShowStatsFilter(false); }}
              />
            </div>
          )}
        </>
      }
    />
  );
}
