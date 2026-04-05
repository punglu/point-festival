import { useAuthStore } from '../../../../shared/stores/useAuthStore';
import ChatModal from '../../../../shared/components/ChatModal';
import styles from './ChatView.module.css';

export default function ChatView() {
  const player = useAuthStore(s => s.player);
  const adminPlayerId = useAuthStore(s => s.adminPlayerId);
  const adminDisplayName = useAuthStore(s => s.adminDisplayName);

  const chatId = player?.id ?? adminPlayerId;
  const chatName = player?.name ?? adminDisplayName ?? '';

  if (!chatId) return (
    <div className={styles.noPlayer}>
      채팅을 사용할 수 없습니다. 다시 로그인해주세요.
    </div>
  );

  return (
    <div className={styles.container}>
      <ChatModal isOpen={true} onClose={() => {}} myId={chatId} myName={chatName} embedded={true} />
    </div>
  );
}
