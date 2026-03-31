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
    activeTab, activeNav, deductOpen, loading, levelThresholds, senders, parentPhotos,
    myProposals, activeMissions, totalDeducted, pendingPoints,
    setSelectedDate, setActiveTab, setActiveNav, setDeductOpen,
    quickDate, requestApproval, proposeMission, sendFeedback,
  } = useDashboard();

  const cheerData = senders.reduce<Record<string, string>>((acc, s) => {
    const found = cheers.find(c => c.sender === s.key);
    if (found) acc[s.key] = found.message;
    return acc;
  }, {});

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // 승인 요청 성공 시 confetti 트리거
  const handleApproval = async (missionId: number) => {
    await requestApproval(missionId);
    setShowConfetti(true);
    setTimeout(() => setShowConfetti(false), 100);
  };

  return (
    <div className={styles.container}>
      {/* Confetti 오버레이 (최상위) */}
      <ConfettiEffect trigger={showConfetti} />

      {/* 헤더 */}
      <header className={styles.header}>
        <span className={styles.headerTitle}>⛏️ 포인트 잔치</span>
        <button className={styles.logoutBtn} onClick={handleLogout}>로그아웃</button>
      </header>

      {/* 날짜 선택 */}
      <DateSelector
        selectedDate={selectedDate}
        quickDate={quickDate}
        setSelectedDate={setSelectedDate}
      />

      {/* 메인 콘텐츠 */}
      {activeNav === 'home' ? (
        <div className={styles.scrollArea}>
          {/* 응원 섹션 */}
          <StoryCards cheers={cheerData} parentPhotos={parentPhotos} senders={senders} />

          {/* 프로필 카드 + ExpBar */}
          <ProfileCard
            player={player}
            dailyPoint={dailyPoint}
            pendingPoints={pendingPoints}
            levelThresholds={levelThresholds}
            onStatClick={type => setStatModal(type)}
          />

          {/* 탭 바 */}
          <div className={styles.tabBar}>
            <button
              className={`${styles.tabBtn} ${activeTab === 'missions' ? styles.tabBtnActive : ''}`}
              onClick={() => setActiveTab('missions')}
            >
              미션
            </button>
            <button
              className={`${styles.tabBtn} ${activeTab === 'proposal' ? styles.tabBtnActive : ''}`}
              onClick={() => setActiveTab('proposal')}
            >
              제안
            </button>
            <button
              className={`${styles.tabBtn} ${activeTab === 'feedback' ? styles.tabBtnActive : ''}`}
              onClick={() => setActiveTab('feedback')}
            >
              답장
            </button>
          </div>

          {/* 탭 콘텐츠 */}
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
                  playerName={player?.name ?? ''}
                />
              )}
            </>
          )}

          {/* 차감 아코디언 */}
          <DeductionAccordion
            deductions={deductions}
            totalDeducted={totalDeducted}
            isOpen={deductOpen}
            onToggle={() => setDeductOpen(!deductOpen)}
          />
        </div>
      ) : (
        <div className={styles.scrollArea}>
          <RankingView currentPlayerId={player?.id ?? 0} />
        </div>
      )}

      {/* 하단 네비 */}
      <BottomNav activeNav={activeNav} setActiveNav={setActiveNav} />

      {/* 포인트 통계 모달 */}
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
