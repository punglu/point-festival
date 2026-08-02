import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyAlbumScreen, familyAlbumFixture } from '../../screens/family/FamilyAlbum';
import { PhotoDetailScreen, photoDetailFixture } from '../../screens/family/PhotoDetail';
import { AlbumSearchScreen, albumSearchFixture } from '../../screens/family/AlbumSearch';
import { AlbumUploadProgressScreen, albumUploadProgressFixture } from '../../screens/family/AlbumUploadProgress';
import { AlbumShareSettingsScreen, albumShareSettingsFixture } from '../../screens/family/AlbumShareSettings';
import styles from './FamilyAlbumPage.module.css';

type View = 'main' | 'photo' | 'search' | 'upload' | 'share';

/**
 * `/family/album` — canonical 1h (앨범, CHILD_OF 1b) with 1p/1w/2v/2y nested
 * per the W7.1 Ownership Matrix. frontend/src/features/family-album/ was an
 * empty scaffold with no real entry point before this pass.
 */
export function FamilyAlbumPage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('main');

  if (view === 'photo') {
    return <div className={styles.wrap}><PhotoDetailScreen model={photoDetailFixture} onClose={() => setView('main')} /></div>;
  }
  if (view === 'search') {
    return <div className={styles.wrap}><AlbumSearchScreen model={albumSearchFixture} onBack={() => setView('main')} onCancel={() => setView('main')} onSelectPhoto={() => setView('photo')} onSelectAlbum={() => setView('main')} /></div>;
  }
  if (view === 'upload') {
    return <div className={styles.wrap}><AlbumUploadProgressScreen model={albumUploadProgressFixture} onClose={() => setView('main')} /></div>;
  }
  if (view === 'share') {
    return <div className={styles.wrap}><AlbumShareSettingsScreen model={albumShareSettingsFixture} onBack={() => setView('main')} onSave={() => setView('main')} /></div>;
  }

  return (
    <div className={styles.wrap}>
      <FamilyAlbumScreen
        model={familyAlbumFixture}
        onBack={() => navigate('/family')}
        onSearch={() => setView('search')}
        onUpload={() => setView('upload')}
        onSelectPhoto={() => setView('photo')}
        onSelectAlbum={() => setView('share')}
      />
    </div>
  );
}
