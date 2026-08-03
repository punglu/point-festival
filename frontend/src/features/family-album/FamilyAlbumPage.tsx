import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyAlbumScreen, familyAlbumFixture } from '../../screens/family/FamilyAlbum';
import { PhotoDetailScreen, photoDetailFixture } from '../../screens/family/PhotoDetail';
import { AlbumSearchScreen, albumSearchFixture } from '../../screens/family/AlbumSearch';
import { AlbumUploadProgressScreen, albumUploadProgressFixture } from '../../screens/family/AlbumUploadProgress';
import { AlbumShareSettingsScreen } from '../../screens/family/AlbumShareSettings';
import {
  listAlbums, listAlbumPhotos, searchAlbumPhotos,
  type FamilyAlbum, type FamilyAlbumPhoto,
} from '../../shared/api/familyAlbumApi';
import { listFamilyMembers, type FamilyMembershipSummary } from '../../shared/api/familyApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './FamilyAlbumPage.module.css';

type View = 'main' | 'photo' | 'search' | 'upload' | 'share';

function photoLabel(photo: FamilyAlbumPhoto): string {
  return photo.caption ?? `사진 ${photo.id}`;
}

/**
 * `/family/album` — canonical 1h (앨범, W7.5 Phase D SLICE-ALBUM-METADATA)
 * with 1p/1w/2y real, 2v (앨범 업로드 진행) staying fixture.
 *
 * **Metadata only, never a real image.** No storage abstraction exists
 * anywhere in the backend (same gate as avatar upload, `2z`) — every
 * "photo" here is a real caption/date row with no picture behind it.
 * `2v`'s own upload flow is `POLICY_BLOCKED`, not part of this Slice; its
 * entry point stays the static fixture it always was.
 */
export function FamilyAlbumPage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [view, setView] = useState<View>('main');
  const [albums, setAlbums] = useState<FamilyAlbum[] | null>(null);
  const [members, setMembers] = useState<FamilyMembershipSummary[]>([]);
  const [activeAlbum, setActiveAlbum] = useState<FamilyAlbum | null>(null);
  const [activeAlbumPhotos, setActiveAlbumPhotos] = useState<FamilyAlbumPhoto[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<FamilyAlbumPhoto[] | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [photoLoadError, setPhotoLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setLoadError(null);
    Promise.all([listAlbums(activeFamilyId, controller.signal), listFamilyMembers(activeFamilyId, controller.signal)])
      .then(([albumList, memberList]) => {
        setAlbums(albumList);
        setMembers(memberList);
      })
      .catch(() => { if (!controller.signal.aborted) setLoadError('앨범을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, [activeFamilyId]);

  const nameByMembershipId = useMemo(() => new Map(members.map((m) => [m.id, m.account_display_name])), [members]);

  const openAlbum = async (album: FamilyAlbum, next: 'photo' | 'share') => {
    if (activeFamilyId === null) return;
    setActiveAlbum(album);
    setPhotoLoadError(null);
    try {
      const photos = await listAlbumPhotos(activeFamilyId, album.id);
      setActiveAlbumPhotos(photos);
    } catch {
      // A failed fetch must never be indistinguishable from a real empty
      // album -- flag it so the photo view can say so instead of silently
      // rendering as "no photos here".
      setActiveAlbumPhotos([]);
      setPhotoLoadError('사진을 불러오지 못했어요.');
    }
    setView(next);
  };

  const runSearch = async (query: string) => {
    if (activeFamilyId === null || query.trim() === '') return;
    setSearchError(null);
    try {
      setSearchResults(await searchAlbumPhotos(activeFamilyId, query.trim()));
    } catch {
      // A failed search must never render as "검색 결과가 없어요" -- that
      // says "we looked and found nothing", which is a different, false
      // claim when the request itself never completed.
      setSearchResults(null);
      setSearchError('사진을 검색하지 못했어요.');
    }
  };

  if (view === 'photo') {
    const photo = activeAlbumPhotos[0];
    // A missing photo is always a real state -- either the album genuinely
    // has none, or the fetch failed (see `photoLoadError`) -- never the
    // fixture's fabricated "여름 여행" photo/comment.
    const model = photo
      ? { ...photoDetailFixture, title: activeAlbum?.title ?? photoDetailFixture.title, meta: `${nameByMembershipId.get(photo.uploaded_by_membership_id) ?? '가족'} · ${photo.taken_at ? new Date(photo.taken_at).toLocaleDateString('ko-KR') : '날짜 없음'} · 1/${activeAlbumPhotos.length}` }
      : { title: activeAlbum?.title ?? '앨범', meta: photoLoadError ?? '사진이 없어요', likeCount: 0, commentCount: 0, commentAuthor: '', commentText: '' };
    return <div className={styles.wrap}><PhotoDetailScreen model={model} onClose={() => setView('main')} /></div>;
  }
  if (view === 'search') {
    // The frozen Screen always renders one "matching album" card above the
    // photo grid; resolve it from the real album a result photo belongs to
    // (`album_id`) rather than always showing the fixture's invented
    // "여름 여행 · 남해" card regardless of what was actually searched.
    const albumById = new Map((albums ?? []).map((a) => [a.id, a]));
    const matchedAlbum = searchResults && searchResults.length > 0 ? albumById.get(searchResults[0].album_id) : undefined;
    const model = searchError
      ? { ...albumSearchFixture, query: searchQuery, summary: searchError, albumTitle: '', albumMeta: '', photos: [] }
      : searchResults === null
      ? { ...albumSearchFixture, query: searchQuery }
      : {
          ...albumSearchFixture,
          query: searchQuery,
          summary: `사진 ${searchResults.length}장 검색됨`,
          albumTitle: matchedAlbum?.title ?? '검색된 앨범이 없어요',
          albumMeta: matchedAlbum ? `사진 ${matchedAlbum.photo_count}장` : '',
          photos: searchResults.length > 0 ? searchResults.map(photoLabel) : ['검색 결과가 없어요'],
        };
    return (
      <div className={styles.wrap}>
        <AlbumSearchScreen
          model={model}
          onBack={() => setView('main')}
          onCancel={() => setView('main')}
          onSelectPhoto={() => setView('photo')}
          onSelectAlbum={() => setView('main')}
          onSelectRecent={(q) => { setSearchQuery(q); void runSearch(q); }}
        />
      </div>
    );
  }
  if (view === 'upload') {
    return <div className={styles.wrap}><AlbumUploadProgressScreen model={albumUploadProgressFixture} onClose={() => setView('main')} /></div>;
  }
  if (view === 'share' && activeAlbum) {
    // 2y read side is real (real album title/photo count/per-member enabled
    // state from `shared_with_membership_ids`). The write side
    // (`updateAlbumSharing`, real and tested at the API layer) is
    // intentionally not called from `onSave` here: the frozen canonical
    // Screen's member rows are plain `<label>`s with no `onClick`/`onChange`
    // handler at all, and the "저장하기" button has nothing to save --
    // same design-contract gap shape as `2z`/`3b`.
    const model = {
      album: activeAlbum.title,
      photoCount: activeAlbum.photo_count,
      members: members.map((m) => ({
        name: m.account_display_name,
        enabled: activeAlbum.shared_with_membership_ids === null || activeAlbum.shared_with_membership_ids.includes(m.id),
      })),
    };
    return (
      <div className={styles.wrap}>
        <AlbumShareSettingsScreen
          model={model}
          onBack={() => setView('main')}
          onSave={() => setView('main')}
        />
      </div>
    );
  }

  const realAlbums = albums ?? [];
  const heroAlbum = realAlbums[0];
  // Loading and load-failure must never show the fixture's fake albums
  // (e.g. "여름 여행", "엄마 생일") -- only real albums or a real empty
  // state ever render here.
  const model = {
    ...familyAlbumFixture,
    summary: albums === null ? (loadError ?? familyAlbumFixture.summary) : `사진 ${realAlbums.reduce((sum, a) => sum + a.photo_count, 0)}장 · 앨범 ${realAlbums.length}개`,
    heroTitle: albums === null ? '' : (heroAlbum?.title ?? '앨범이 없어요'),
    heroMeta: albums !== null && heroAlbum ? `사진 ${heroAlbum.photo_count}장 · ${nameByMembershipId.get(heroAlbum.created_by_membership_id) ?? '가족'}이 추가` : '',
    recentPhotos: [],
    albums: albums === null ? [] : realAlbums.map((a) => ({
      title: a.title,
      meta: `${a.photo_count}장`,
      person: nameByMembershipId.get(a.created_by_membership_id) ?? '가족',
    })),
  };

  return (
    <div className={styles.wrap}>
      <FamilyAlbumScreen
        model={model}
        onBack={() => navigate('/family')}
        onSearch={() => setView('search')}
        onUpload={() => setView('upload')}
        onSelectPhoto={() => { if (heroAlbum) void openAlbum(heroAlbum, 'photo'); }}
        onSelectAlbum={(album) => {
          const real = realAlbums.find((a) => a.title === album.title);
          if (real) void openAlbum(real, 'share');
        }}
      />
    </div>
  );
}
