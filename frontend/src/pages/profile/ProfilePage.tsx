import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { MyProfileScreen, myProfileFixture } from '../../screens/family/MyProfile';
import { PinChangeScreen } from '../../screens/family/PinChange';
import { SettingsListScreen, settingsListFixture } from '../../screens/family/SettingsList';
import { ProfileEditScreen, profileEditFixture } from '../../screens/family/ProfileEdit';
import { NotificationPreferencesScreen, notificationPreferencesFixture } from '../../screens/family/NotificationPreferences';
import { LanguageSettingsScreen, languageSettingsFixture } from '../../screens/family/LanguageSettings';
import { ThemeSettingsScreen, themeSettingsFixture } from '../../screens/family/ThemeSettings';
import { AccountDeletionConfirmScreen, accountDeletionConfirmFixture } from '../../screens/family/AccountDeletionConfirm';
import { WidgetGalleryScreen, widgetGalleryFixture } from '../../screens/family/WidgetGallery';
import { ShortcutEditorScreen, shortcutEditorFixture } from '../../screens/family/ShortcutEditor';
import styles from './ProfilePage.module.css';

type View = 'main' | 'edit' | 'pin' | 'settings' | 'notifications' | 'language' | 'theme' | 'delete' | 'widgets' | 'shortcuts';

/**
 * `/profile` — canonical 1f (나 프로필, ROOT_OF) with 1u/2k/2n/2z/3f/3g/3h/3k/3l
 * as nested views per the W7.1 Ownership Matrix (all target
 * frontend/src/pages/profile/). No profile-domain product container existed
 * before this pass. Real player identity is not yet threaded through (no
 * "current player" API call is wired here) — every screen uses its canonical
 * fixture as an explicit pending adapter (DATA_AND_BEHAVIOR_WIRING_PENDING).
 * 3h (계정 탈퇴 확인) is a confirmed TRUE_FUNCTIONAL_GAP — no account-deletion
 * policy/API exists anywhere in the product (verified via repo-wide grep
 * before wiring, not assumed) — so its structural entry point is built, but
 * onConfirm only closes the view locally; no destructive action is faked.
 */
export function ProfilePage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('main');

  if (view === 'edit') {
    return <div className={styles.wrap}><ProfileEditScreen model={profileEditFixture} onBack={() => setView('main')} onSave={() => setView('main')} /></div>;
  }
  if (view === 'pin') {
    return <div className={styles.wrap}><PinChangeScreen onBack={() => setView('settings')} onComplete={() => setView('settings')} /></div>;
  }
  if (view === 'notifications') {
    return <div className={styles.wrap}><NotificationPreferencesScreen model={notificationPreferencesFixture} onBack={() => setView('settings')} /></div>;
  }
  if (view === 'language') {
    return <div className={styles.wrap}><LanguageSettingsScreen model={languageSettingsFixture} onBack={() => setView('settings')} /></div>;
  }
  if (view === 'theme') {
    return <div className={styles.wrap}><ThemeSettingsScreen model={themeSettingsFixture} onBack={() => setView('settings')} /></div>;
  }
  if (view === 'delete') {
    return <div className={styles.wrap}><AccountDeletionConfirmScreen model={accountDeletionConfirmFixture} onBack={() => setView('settings')} onConfirm={() => setView('settings')} /></div>;
  }
  if (view === 'shortcuts') {
    return <div className={styles.wrap}><ShortcutEditorScreen model={shortcutEditorFixture} onBack={() => setView('widgets')} onConfirm={() => setView('widgets')} /></div>;
  }
  if (view === 'widgets') {
    return (
      <div className={styles.wrap}>
        <WidgetGalleryScreen model={widgetGalleryFixture} onBack={() => setView('settings')} onConfirm={() => setView('settings')} />
        <button type="button" className={styles.shortcutLink} onClick={() => setView('shortcuts')}>바로가기 편집</button>
      </div>
    );
  }
  if (view === 'settings') {
    return (
      <div className={styles.wrap}>
        <SettingsListScreen
          model={settingsListFixture}
          onBack={() => setView('main')}
          onOpenProfile={() => setView('edit')}
          onSelectNav={(item) => {
            if (item.key === 'pin') setView('pin');
            else if (item.key === 'members') navigate('/family');
            else if (item.key === 'delete-account') setView('delete');
            else if (item.key === 'notification-detail') setView('notifications');
            else if (item.key === 'language') setView('language');
            else if (item.key === 'theme') setView('theme');
            else if (item.key === 'widgets') setView('widgets');
          }}
        />
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <MyProfileScreen
        model={myProfileFixture}
        onEditProfile={() => setView('edit')}
        onOpenAllSettings={() => setView('settings')}
        onSelectItem={(item) => {
          if (item.key === 'pin') setView('pin');
          else if (item.key === 'members') navigate('/family');
          else if (item.key === 'notifications') setView('notifications');
        }}
      />
    </div>
  );
}
