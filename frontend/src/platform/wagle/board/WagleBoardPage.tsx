import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyBoardScreen, familyBoardFixture } from '../../../screens/wagle/FamilyBoard';
import type { BoardPost } from '../../../screens/wagle/FamilyBoard';
import { CommentComposerScreen, commentComposerFixture } from '../../../screens/wagle/CommentComposer';
import { PopularPostsScreen, popularPostsFixture } from '../../../screens/wagle/PopularPosts';
import styles from './WagleBoardPage.module.css';

/**
 * `/wagle/board` — canonical 3c (가족 게시판), ROOT_OF per the W7.1 Ownership
 * Matrix, WAGLE-owned but a sibling surface to the chat room list rather than
 * a child of it. No board API exists yet (TRUE_FUNCTIONAL_GAP, W7.5 scope):
 * this container renders the canonical Screens with their fixtures as an
 * explicit pending adapter, not real board data. `onWrite` (새 글쓰기) has no
 * canonical target in the 64-screen scope, so it is left unwired here.
 */
export function WagleBoardPage() {
  const navigate = useNavigate();
  const [openPost, setOpenPost] = useState<BoardPost | null>(null);
  const [showPopular, setShowPopular] = useState(false);

  return (
    <div className={styles.wrap}>
      <FamilyBoardScreen
        model={familyBoardFixture}
        onBack={() => navigate('/wagle')}
        onTab={() => undefined}
        onSelectPost={setOpenPost}
      />
      <button type="button" className={styles.popularLink} onClick={() => setShowPopular(true)}>
        인기 게시글 보기
      </button>

      {showPopular && (
        <div className={styles.overlay} data-testid="wagle-board-popular-overlay">
          {/* 3e (인기 게시글) — CHILD_OF 3c, NO_ROUTE per the Ownership Matrix. */}
          <PopularPostsScreen model={popularPostsFixture} />
          <button type="button" className={styles.overlayClose} onClick={() => setShowPopular(false)} aria-label="닫기">
            ✕ 닫기
          </button>
        </div>
      )}

      {openPost && (
        <div className={styles.overlay} data-testid="wagle-board-comment-overlay">
          {/* 3d (댓글 작성) — CHILD_OF 3c, NO_ROUTE per the Ownership Matrix. */}
          <CommentComposerScreen model={commentComposerFixture} onCancel={() => setOpenPost(null)} />
        </div>
      )}
    </div>
  );
}
