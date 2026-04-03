import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { useDashboard } from './hooks/useDashboard';
import styles from './UserDashboard.module.css';

import DateSelector from './components/DateSelector';
import ProfileCard from './components/ProfileCard';
import StoryCards from './components/StoryCards';
import MissionList from './components/MissionList';
import MissionProposal from './components/MissionProposal';
import FeedbackSection from './components/FeedbackSection';
import DeductionAccordion from './components/DeductionAccordion';
import RankingView from './components/RankingView';
import BottomNav from './components/BottomNav';
import StatDetailModal from './components/StatDetailModal';
import ConfettiEffect from './components/ConfettiEffect';

type StatType = 'earned' | 'balance' | 'pending';

export default function UserDashboard() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [statModal, setStatModal] = useState<StatType | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  const {
    player, selectedDate,
    cheers, feedbacks, deductions, dailyPoint,
    activeTab, activeNav, deductOpen, loading, levelThresholds, senders, parentPhotos, playerPhoto, playerStatusMsg, allPlayers,
    myProposals, activeMissions, totalDeducted, pendingPoints,
    setSelectedDate, setActiveTab, setActiveNav, setDeductOpen,
    quickDate, requestApproval, proposeMission, sendFeedback,
  } = useDashboard();

  // 나에게 온 메세지 뱃지 카운트
  const chatBadgeCount = feedbacks.filter(fb => fb.recipient === player?.name).length;

  const cheerData = senders.reduce<Record<string, string>>((acc, s) => {
    const found = cheers.find(c => c.sender === s.key);
    if (found) acc[s.key] = found.message;
    return acc;
  }, {});

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
            <img src="/favicon-192x192.png" alt="포인트 잔치" className={styles.brandLogo} />
            <span className={styles.brandName}>포인트 잔치</span>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout}>로그아웃</button>
        </div>

        <DateSelector
          selectedDate={selectedDate}
          quickDate={quickDate}
          setSelectedDate={setSelectedDate}
        />

        <ProfileCard
          player={player}
          photo={playerPhoto}
          initialStatusMsg={playerStatusMsg}
          dailyPoint={dailyPoint}
          pendingPoints={pendingPoints}
          levelThresholds={levelThresholds}
          onStatClick={type => setStatModal(type)}
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
            <div className={styles.tabWrapper}>
              <button
                className={`${styles.tab} ${activeTab === 'feedback' ? styles.tabActive : ''}`}
                style={{ width: '100%' }}
                onClick={() => setActiveTab('feedback')}
              >대화하기</button>
              {chatBadgeCount > 0 && (
                <span className={styles.tabBadge}>{chatBadgeCount}</span>
              )}
            </div>
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
              {activeTab === 'feedback' && (
                <FeedbackSection
                  feedbacks={feedbacks}
                  sendFeedback={sendFeedback}
                  playerId={player?.id ?? 0}
                  playerName={player?.name ?? ''}
                  playerPhoto={playerPhoto}
                  parentPhotos={parentPhotos}
                  senders={senders}
                  allPlayers={allPlayers}
                />
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
    </div>
  );
}
