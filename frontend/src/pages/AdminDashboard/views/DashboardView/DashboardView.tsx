import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DashboardView.module.css';
import { useAdminData } from '../../hooks/useAdminData';
import StatCard from '../../components/StatCard/StatCard';
import PlayerStatusCard from './components/PlayerStatusCard';
import PendingMissionCard from './components/PendingMissionCard';
import WeeklyActivityChart from './components/WeeklyActivityChart';
import RecentAlerts from './components/RecentAlerts';
import MissionRanking from './components/MissionRanking';
import ActiveMissionDetailModal from './components/ActiveMissionDetailModal';
import PendingApprovalModal from './components/PendingApprovalModal';
import CompletedMissionsModal from './components/CompletedMissionsModal';
import PointHistoryModal from './components/PointHistoryModal';

export default function DashboardView() {
  const navigate = useNavigate();
  const {
    players, missions, notifications, dailyPoints,
    stats, missionRanking, cycle, loading, reload,
    approveMission, rejectMission,
  } = useAdminData();

  const today = new Date().toISOString().slice(0, 10);

  const [activeDetailOpen,    setActiveDetailOpen]    = useState(false);
  const [pendingApprovalOpen, setPendingApprovalOpen] = useState(false);
  const [completedOpen,       setCompletedOpen]       = useState(false);
  const [pointHistoryOpen,    setPointHistoryOpen]    = useState(false);

  if (loading) {
    return <div className={styles.loading}>데이터 로딩 중...</div>;
  }

  return (
    <div className={styles.view}>
      {/* 헤더 */}
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <h1 className={styles.title}>대시보드</h1>
          <p className={styles.dateText}>{today}</p>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.btnRefresh} onClick={reload}>새로고침</button>
          <button className={styles.btnNew} onClick={() => navigate('/admin/missions')}>
            + 새 미션
          </button>
        </div>
      </div>

      {/* 스탯 카드 4열 */}
      <div className={styles.statGrid}>
        <StatCard
          label="활성 미션"
          value={stats.totalActiveMissions}
          subtext={`오늘 ${stats.todayNewMissions}건`}
          onClick={() => setActiveDetailOpen(true)}
        />
        <StatCard
          label="승인 대기"
          value={stats.pendingApproval}
          subtext={stats.pendingApproval > 0 ? '확인 필요' : '모두 처리됨'}
          subtextColor={stats.pendingApproval > 0 ? '#D97706' : '#059669'}
          onClick={() => setPendingApprovalOpen(true)}
        />
        <StatCard
          label="이번 주 완료"
          value={stats.completedThisWeek}
          subtext={`목표 ${stats.weeklyGoal}건`}
          onClick={() => setCompletedOpen(true)}
        />
        <StatCard
          label="총 발행 포인트"
          value={`${stats.totalPointsIssued}pt`}
          subtext={cycle.label}
          onClick={() => setPointHistoryOpen(true)}
        />
      </div>

      {/* 플레이어 현황 + 승인 대기 미션 */}
      <div className={styles.grid2}>
        <PlayerStatusCard
          players={players}
          missions={missions}
          dailyPoints={dailyPoints}
        />
        <PendingMissionCard missions={missions} players={players} />
      </div>

      {/* 이번 주 활동 (풀와이드) */}
      <WeeklyActivityChart missions={missions} players={players} cycle={cycle} />

      {/* 최근 알림 */}
      <RecentAlerts notifications={notifications} />

      {/* 미션 랭킹 (풀와이드) */}
      <MissionRanking ranking={missionRanking} players={players} cycle={cycle} />

      {/* 모달 */}
      <ActiveMissionDetailModal
        open={activeDetailOpen}
        onClose={() => setActiveDetailOpen(false)}
        missions={missions}
        players={players}
        cycle={cycle}
      />
      <PendingApprovalModal
        open={pendingApprovalOpen}
        onClose={() => setPendingApprovalOpen(false)}
        missions={missions}
        players={players}
        onApprove={approveMission}
        onReject={rejectMission}
      />
      <CompletedMissionsModal
        open={completedOpen}
        onClose={() => setCompletedOpen(false)}
        missions={missions}
        players={players}
        cycle={cycle}
      />
      <PointHistoryModal
        open={pointHistoryOpen}
        onClose={() => setPointHistoryOpen(false)}
        missions={missions}
        players={players}
        cycle={cycle}
      />
    </div>
  );
}
