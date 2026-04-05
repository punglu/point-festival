import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLocalToday, getMonday, shiftWeek } from '../../shared/utils/dateUtils';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { useDashboard } from './hooks/useDashboard';
import { httpClient } from '../../shared/api/httpClient';
import styles from './UserDashboard.module.css';

import WeeklyDateBar from './components/WeeklyDateBar';
import ProfileCard from './components/ProfileCard';
import StoryCards from './components/StoryCards';
import MissionList from './components/MissionList';
import MissionProposal from './components/MissionProposal';
import DeductionAccordion from './components/DeductionAccordion';
import ChatModal from '../../shared/components/ChatModal';
import RankingView from './components/RankingView';
import BottomNav from './components/BottomNav';
import StatDetailModal from './components/StatDetailModal';
import ConfettiEffect from './components/ConfettiEffect';
import WeeklyMissionModal from './components/WeeklyMissionModal';
import clusterLogo from '../../assets/logos/brand-icon.png';

type StatType = 'earned' | 'balance' | 'pending';

export default function UserDashboard() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [statModal, setStatModal] = useState<StatType | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [weeklyOpen, setWeeklyOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const [weekStart, setWeekStart] = useState(() => getMonday());
  const [weeklyMissions, setWeeklyMissions] = useState<Record<string, { status: string }[]>>({});

  const {
    player, selectedDate,
    cheers, deductions, dailyPoint,
    activeTab, activeNav, deductOpen, loading, levelThresholds, senders, parentPhotos, playerPhoto, playerStatusMsg,
    myProposals, activeMissions, totalDeducted, pendingPoints, totalEarned,
    setSelectedDate, setActiveTab, setActiveNav, setDeductOpen,
    requestApproval, proposeMission,
  } = useDashboard();

  // 채팅 안읽은 수 폴링
  useEffect(() => {
    if (!player) return;
    const fetchUnread = () => {
      httpClient.get<{ unread: number }>('/api/chat/unread')
        .then(res => setUnreadCount(res.data.unread))
        .catch(() => {});
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [player]);

  const cheerData = senders.reduce<Record<string, string>>((acc, s) => {
    const found = cheers.find(c => c.sender === s.key);
    if (found) acc[s.key] = found.message;
    return acc;
  }, {});

  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    httpClient.get('/api/missions/weekly', {
      params: { player_id: player.id, week_start: weekStart },
      signal: controller.signal,
    })
      .then(res => setWeeklyMissions(res.data))
      .catch(() => {});
    return () => controller.abort();
  }, [player, weekStart]);

  const handlePrevWeek = () => setWeekStart(shiftWeek(weekStart, -1));
  const handleNextWeek = () => setWeekStart(shiftWeek(weekStart,  1));
  const handleToday    = () => {
    const todayStr = getLocalToday();
    setWeekStart(getMonday());
    setSelectedDate(todayStr);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleApproval = async (missionId: number) => {
    await requestApproval(missionId);
    setShowConfetti(true);
    setTimeout(() => setShowConfetti(false), 100);
  };

  return (
    <div className={styles.dashboardContainer}>
      <ConfettiEffect trigger={showConfetti} />

      {/* 통합 헤더 (Indigo) */}
      <div className={styles.header}>
        <div className={styles.headerTop}>
          <div className={styles.brand}>
            <img src={clusterLogo} alt="로고" style={{ width: 34, height: 34, objectFit: 'contain', marginTop: -5 }} />
            <span className={styles.brandName}>포인트 잔치</span>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.chatBtn} onClick={() => setChatOpen(true)} aria-label="대화하기">
              💬
              {unreadCount > 0 && <span className={styles.chatBadge}>{unreadCount}</span>}
            </button>
            <button className={styles.logoutBtn} onClick={handleLogout}>로그아웃</button>
          </div>
        </div>

        <WeeklyDateBar
          weekStart={weekStart}
          selectedDate={selectedDate}
          missionsByDate={weeklyMissions}
          onSelectDate={setSelectedDate}
          onPrevWeek={handlePrevWeek}
          onNextWeek={handleNextWeek}
          onToday={handleToday}
        />

        <ProfileCard
          player={player}
          photo={playerPhoto}
          initialStatusMsg={playerStatusMsg}
          dailyPoint={dailyPoint}
          pendingPoints={pendingPoints}
          levelThresholds={levelThresholds}
          totalEarned={totalEarned}
          onStatClick={type => {
            if (type === 'pending') { setWeeklyOpen(true); return; }
            setStatModal(type);
          }}
        />
      </div>

      {activeNav === 'home' ? (
        <div className={styles.contentArea}>
          <StoryCards cheers={cheerData} parentPhotos={parentPhotos} senders={senders} />

          <div className={styles.tabContainer}>
            <button
              className={`${styles.tab} ${activeTab === 'missions' ? styles.tabActive : ''}`}
              onClick={() => setActiveTab('missions')}
            >미션</button>
            <button
              className={`${styles.tab} ${activeTab === 'proposal' ? styles.tabActive : ''}`}
              onClick={() => setActiveTab('proposal')}
            >제안</button>
          </div>

          {loading ? (
            <div className={styles.loading}>불러오는 중...</div>
          ) : (
            <>
              {activeTab === 'missions' && (
                <MissionList missions={activeMissions} requestApproval={handleApproval} />
              )}
              {activeTab === 'proposal' && (
                <MissionProposal myProposals={myProposals} proposeMission={proposeMission} />
              )}
            </>
          )}

          <DeductionAccordion
            deductions={deductions}
            totalDeducted={totalDeducted}
            isOpen={deductOpen}
            onToggle={() => setDeductOpen(!deductOpen)}
          />
        </div>
      ) : (
        <div className={styles.contentArea}>
          <RankingView currentPlayerId={player?.id ?? 0} />
        </div>
      )}

      <BottomNav activeNav={activeNav} setActiveNav={setActiveNav} />

      <StatDetailModal
        type={statModal}
        isOpen={statModal !== null}
        onClose={() => setStatModal(null)}
        missions={activeMissions}
        deductions={deductions}
        dailyPoint={dailyPoint}
      />

      <WeeklyMissionModal
        playerId={player?.id ?? 0}
        isOpen={weeklyOpen}
        onClose={() => setWeeklyOpen(false)}
        onSelectDate={(date) => { setWeekStart(getMonday(new Date(date + 'T00:00:00'))); setSelectedDate(date); setWeeklyOpen(false); }}
      />

      {player && (
        <ChatModal
          isOpen={chatOpen}
          onClose={() => setChatOpen(false)}
          myId={player.id}
          myName={player.name}
        />
      )}
    </div>
  );
}
