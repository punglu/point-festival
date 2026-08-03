import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyBoardScreen, familyBoardFixture } from '../../../screens/wagle/FamilyBoard';
import type { BoardPost } from '../../../screens/wagle/FamilyBoard';
import { CommentComposerScreen } from '../../../screens/wagle/CommentComposer';
import { PopularPostsScreen, popularPostsFixture } from '../../../screens/wagle/PopularPosts';
import {
  listRooms, createRoom, listMessages, sendMessage, listParticipants, listPopularPosts,
  type WagleMessage,
} from '../../../shared/api/wagleApi';
import { listFamilyMembers } from '../../../shared/api/familyApi';
import { useFamilyContextStore } from '../../../shared/stores/useFamilyContextStore';
import styles from './WagleBoardPage.module.css';

// Reuses a plain Wagle GROUP Room as the board (W7.5 Phase D
// REUSE-WAGLE-ROOMS-AS-BOARD) rather than a new Post aggregate -- per the
// Phase D Slice Mapping's own recommendation. This sentinel title identifies
// that Room; it is never shown to the user (the Screen renders its own
// "가족 게시판" heading regardless of the underlying Room's title).
const BOARD_ROOM_TITLE = '__family_board__';

const BADGE_TONE: Record<string, BoardPost['badgeTone']> = { 공지: 'blue', 건의: 'yellow', 자유: 'green' };

const POPULAR_RANGE_TO_API: Record<string, 'week' | 'month' | 'all'> = {
  '이번 주': 'week',
  '이번 달': 'month',
  '전체': 'all',
};

/** A "post" is a top-level TEXT message whose body encodes `[category] title`
 *  on its first line and the summary on the rest -- no schema change, since
 *  reusing existing Wagle messages is this Slice's whole point. Only the
 *  decode direction is needed here: `onWrite` has no canonical compose
 *  screen to encode a new post from (see this file's own top comment), so
 *  no post is ever created through this UI yet. */
function decodePost(message: WagleMessage, nameByMembershipId: Map<string, string>): BoardPost {
  const body = message.body ?? '';
  const match = /^\[(.+?)\]\s*(.*)$/s.exec(body);
  const category = match ? match[1] : '자유';
  const rest = match ? match[2] : body;
  const [title, ...summaryLines] = rest.split('\n');
  const author = message.sender_participant_id ? nameByMembershipId.get(message.sender_participant_id) ?? '가족' : '가족';
  return {
    badge: category,
    badgeTone: BADGE_TONE[category] ?? 'green',
    author,
    time: new Date(message.created_at).toLocaleString('ko-KR'),
    title: title || '(제목 없음)',
    summary: summaryLines.join('\n'),
    // Real (W7.5 Phase D SLICE-WAGLE-BOARD-REACTIONS): `reaction_count` comes
    // straight from the API. The *toggle* action has no trigger anywhere in
    // the frozen 3c/3e canonical Screens (no like button/callback exists in
    // either), so reacting is not reachable from this UI yet -- same
    // disclosed-gap shape as 1i/1v/2y/2z/3b/3j -- but the displayed count is
    // never fabricated.
    likes: message.reaction_count,
    comments: 0, // filled in after counting replies, see below
  };
}

/**
 * `/wagle/board` — canonical 3c (가족 게시판) with 3d (댓글 작성) real, per
 * W7.5 Phase D REUSE-WAGLE-ROOMS-AS-BOARD. A "post" is a top-level message
 * in a dedicated board Room; a "comment" is a reply to it, reusing `2g`'s
 * `reply_to_message_id` directly rather than a second reply concept.
 *
 * 3e (인기 게시글) is real (W7.5 Phase D SLICE-WAGLE-BOARD-REACTIONS): ranked
 * by real reaction_count + comment_count over the selected range, via
 * `GET .../wagle/board/popular`. Resolved as buildable rather than a PM
 * policy gate — both `3c` and `3e`'s own frozen designs already render
 * `♥ likes · 💬 comments` as a core visual element, so this makes an
 * already-designed-for stat real rather than inventing a new concept. The
 * reaction *toggle* itself has no trigger in either frozen canonical
 * Screen (no like button/callback exists in either), so reacting is not
 * reachable from this UI yet — same disclosed-gap shape as the other six
 * missing-input-control rows (`1i`/`1v`/`2y`/`2z`/`3b`/`3j`).
 *
 * `onWrite` (새 글쓰기) has no canonical target in the 64-screen scope (no
 * dedicated compose screen), so it stays unwired, same as the original
 * structural pass's own disclosed gap.
 */
export function WagleBoardPage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [boardRoomId, setBoardRoomId] = useState<string | null>(null);
  const [boardUnavailable, setBoardUnavailable] = useState(false);
  const [messages, setMessages] = useState<WagleMessage[]>([]);
  const [nameByParticipantId, setNameByParticipantId] = useState<Map<string, string>>(new Map());
  const [activeTab, setActiveTab] = useState(familyBoardFixture.activeTab);
  const [openPostMessageId, setOpenPostMessageId] = useState<string | null>(null);
  const [showPopular, setShowPopular] = useState(false);
  const [popularRange, setPopularRange] = useState(popularPostsFixture.activeRange);
  const [popularPosts, setPopularPosts] = useState<Awaited<ReturnType<typeof listPopularPosts>> | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setLoadError(null);
    setBoardUnavailable(false);

    (async () => {
      const memberList = await listFamilyMembers(activeFamilyId, controller.signal);
      const rooms = await listRooms(activeFamilyId, controller.signal);
      let board = rooms.find((r) => r.title === BOARD_ROOM_TITLE);
      if (!board) {
        try {
          board = await createRoom(activeFamilyId, {
            room_type: 'GROUP',
            title: BOARD_ROOM_TITLE,
            participant_membership_ids: memberList.map((m) => m.id),
          });
        } catch {
          setBoardUnavailable(true);
          return;
        }
      }
      setBoardRoomId(String(board.id));
      const [page, participants] = await Promise.all([
        listMessages(activeFamilyId, String(board.id), { limit: 100 }, controller.signal),
        listParticipants(activeFamilyId, String(board.id), controller.signal),
      ]);
      setMessages(page.messages);
      setNameByParticipantId(new Map(participants.map((p) => [String(p.id), p.account_display_name])));
    })().catch(() => { if (!controller.signal.aborted) setLoadError('게시판을 불러오지 못했어요.'); });

    return () => controller.abort();
  }, [activeFamilyId]);

  useEffect(() => {
    if (activeFamilyId === null || !showPopular) return undefined;
    const controller = new AbortController();
    const apiRange = POPULAR_RANGE_TO_API[popularRange] ?? 'week';
    listPopularPosts(activeFamilyId, apiRange, controller.signal).then(setPopularPosts).catch(() => setPopularPosts([]));
    return () => controller.abort();
  }, [activeFamilyId, showPopular, popularRange]);

  const topLevel = messages.filter((m) => !m.reply_to_message_id && !m.deleted);
  const posts = topLevel.map((m) => {
    const post = decodePost(m, nameByParticipantId);
    post.comments = messages.filter((c) => c.reply_to_message_id === m.id).length;
    return post;
  });
  const visiblePosts = activeTab === '전체' ? posts : posts.filter((p) => p.badge === activeTab);

  const openPostMessage = messages.find((m) => m.id === openPostMessageId) ?? null;
  const openPostComments = openPostMessage
    ? messages.filter((m) => m.reply_to_message_id === openPostMessage.id && !m.deleted)
    : [];

  const handleSendComment = async (text: string) => {
    if (activeFamilyId === null || boardRoomId === null || !openPostMessage || text.trim() === '') return;
    setLoadError(null);
    try {
      await sendMessage(activeFamilyId, boardRoomId, {
        body: text.trim(),
        client_message_id: typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `comment-${Date.now()}`,
        reply_to_message_id: openPostMessage.id,
      });
      const page = await listMessages(activeFamilyId, boardRoomId, { limit: 100 });
      setMessages(page.messages);
    } catch {
      setLoadError('댓글을 등록하지 못했어요.');
    }
  };

  if (openPostMessage) {
    const decoded = decodePost(openPostMessage, nameByParticipantId);
    return (
      <div className={styles.wrap}>
        <CommentComposerScreen
          model={{
            commentCount: openPostComments.length,
            post: { badge: decoded.badge, author: decoded.author, time: decoded.time, title: decoded.title, body: decoded.summary },
            comments: openPostComments.map((c) => ({
              author: c.sender_participant_id ? nameByParticipantId.get(c.sender_participant_id) ?? '가족' : '가족',
              message: c.body ?? '',
              time: new Date(c.created_at).toLocaleString('ko-KR'),
            })),
            placeholder: '댓글을 입력하세요',
            myInitial: '나',
          }}
          onCancel={() => setOpenPostMessageId(null)}
          onSubmit={(text) => void handleSendComment(text)}
        />
        {/* A failed comment post must be visible right where the user just
            tried to send it, not only as a delayed subtitle after they
            navigate back to the board list. */}
        {loadError && <p className={styles.error} role="alert">{loadError}</p>}
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <FamilyBoardScreen
        model={{
          ...familyBoardFixture,
          activeTab,
          subtitle: boardUnavailable
            ? '아직 게시판이 만들어지지 않았어요. 보호자에게 문의하세요.'
            : loadError ?? familyBoardFixture.subtitle,
          posts: boardUnavailable ? [] : visiblePosts,
        }}
        onBack={() => navigate('/wagle')}
        onTab={setActiveTab}
        onSelectPost={(post) => {
          const real = topLevel.find((m) => decodePost(m, nameByParticipantId).title === post.title);
          if (real) { setLoadError(null); setOpenPostMessageId(String(real.id)); }
        }}
      />
      <button type="button" className={styles.popularLink} onClick={() => setShowPopular(true)}>
        인기 게시글 보기
      </button>

      {showPopular && (
        <div className={styles.overlay} data-testid="wagle-board-popular-overlay">
          {/* 3e (인기 게시글) — real ranking, see this file's own top comment. */}
          <PopularPostsScreen
            model={{
              ...popularPostsFixture,
              activeRange: popularRange,
              posts: (popularPosts ?? []).map((p, index) => ({
                rank: index + 1,
                title: p.body ?? '(내용 없음)',
                author: p.author_display_name,
                time: new Date(p.created_at).toLocaleString('ko-KR'),
                likes: p.reaction_count,
                comments: p.comment_count,
              })),
            }}
            onRangeChange={setPopularRange}
          />
          <button type="button" className={styles.overlayClose} onClick={() => setShowPopular(false)} aria-label="닫기">
            ✕ 닫기
          </button>
        </div>
      )}
    </div>
  );
}
