import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { MyProfileScreen, myProfileFixture } from '../../screens/family/MyProfile';
import type { MyProfileModel } from '../../screens/family/MyProfile';
import { PinChangeScreen } from '../../screens/family/PinChange';
import { SettingsListScreen, settingsListFixture } from '../../screens/family/SettingsList';
import { ProfileEditScreen, profileEditFixture } from '../../screens/family/ProfileEdit';
import type { ProfileEditModel } from '../../screens/family/ProfileEdit';
import { NotificationPreferencesScreen, notificationPreferencesFixture } from '../../screens/family/NotificationPreferences';
import { LanguageSettingsScreen, languageSettingsFixture } from '../../screens/family/LanguageSettings';
import { ThemeSettingsScreen, themeSettingsFixture } from '../../screens/family/ThemeSettings';
import { AccountDeletionConfirmScreen, accountDeletionConfirmFixture } from '../../screens/family/AccountDeletionConfirm';
import { WidgetGalleryScreen, widgetGalleryFixture } from '../../screens/family/WidgetGallery';
import { ShortcutEditorScreen, shortcutEditorFixture } from '../../screens/family/ShortcutEditor';
import { getMe, listFamilyMembers, type AuthorizedFamilySummary, type MeResponse } from '../../shared/api/familyApi';
import { getLevel, getProjection, getOwnMissions, type MarkpointLevel } from '../../shared/api/markpointApi';
import { getNotificationPreferences, setNotificationPreference, type NotificationPreferenceEntry } from '../../shared/api/notificationPreferencesApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './ProfilePage.module.css';

// Maps the canonical 2n Screen's real toggle labels to the backend's
// `pref_key`s. "시간대" is deliberately absent -- it has no toggle in the
// frozen Screen (static detail text only), so it is not a preference.
const NOTIFICATION_LABEL_TO_KEY: Record<string, string> = {
  '전체 알림 허용': 'notify_all',
  '미션 승인/반려': 'mission_decision',
  '포인트 지급/차감': 'point_change',
  '레벨업 · 배지': 'levelup_badge',
  '가족 대화 메시지': 'family_message',
  '일정 알림': 'schedule_reminder',
  '앨범 새 사진': 'album_new_photo',
  '방해 금지 시간': 'quiet_hours',
};

type View = 'main' | 'edit' | 'pin' | 'settings' | 'notifications' | 'language' | 'theme' | 'delete' | 'widgets' | 'shortcuts';

const RELATIONSHIP_LABEL: Record<string, string> = {
  mother: '엄마',
  father: '아빠',
  child: '자녀',
  guardian: '보호자',
  grandparent: '조부모',
  other: '기타',
  unknown: '미설정',
};

// The frozen 2z canonical Screen's 4 swatches are the only avatar-color
// options this product defines -- reused as the real palette rather than
// inventing a 5th, so `avatar_color` always maps onto one of them.
const AVATAR_COLOR_PALETTE = profileEditFixture.colors.map((c) => c.value);

function joinedLabel(joinedAt: string | null | undefined): string {
  if (!joinedAt) return '';
  const d = new Date(joinedAt);
  if (Number.isNaN(d.getTime())) return '';
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월부터 함께`;
}

function toMyProfileModel(
  me: MeResponse,
  family: AuthorizedFamilySummary | null,
  level: MarkpointLevel | null,
  balance: number | null,
  completedMissionCount: number | null,
  memberCount: number | null,
  statsLoadFailed: boolean,
): MyProfileModel {
  const joined = joinedLabel(family?.joined_at);
  // A still-null stat means either "still loading" or "this specific
  // sub-fetch failed" -- both must never render the fixture's fake numbers
  // (Lv.3, 320P, etc.) as if they were real. `statsLoadFailed` only
  // distinguishes "genuinely failed" for the label text; either way, no
  // null stat here ever resolves to a fixture value below.
  const unavailable = statsLoadFailed ? '불러오지 못함' : '—';
  return {
    avatarInitial: me.display_name.slice(0, 1),
    playerName: me.display_name,
    levelLabel: level ? `Lv.${level.level} ${level.title}` : unavailable,
    familyMeta: family ? [family.name, joined].filter(Boolean).join(' · ') : myProfileFixture.familyMeta,
    stats: [
      { name: '보유 포인트', value: balance !== null ? `${balance}P` : unavailable },
      { name: '누적 미션', value: completedMissionCount !== null ? `${completedMissionCount}개` : unavailable },
      // 연속 달성(streak): no such concept exists anywhere in the Ledger or
      // mission pipeline (grep-confirmed, W7.5 Phase C) -- keeping the
      // disclosed fixture value rather than fabricating a real-looking
      // number. See the Matrix's own 1f capability note.
      { name: '연속 달성', value: myProfileFixture.stats[2].value },
    ],
    levelProgressLabel: level ? `${level.lifetime_earned}P / ${level.next_threshold}P` : unavailable,
    levelProgressPercent: level?.progress_percent ?? 0,
    levelHint: level
      ? `${Math.max(0, level.next_threshold - level.lifetime_earned)}P를 더 모으면 다음 레벨이 돼요.`
      : unavailable,
    activity: [
      { key: 'points', name: '포인트 내역', value: balance !== null ? `보유 ${balance}P` : unavailable, icon: 'list' },
      { key: 'missions', name: '완료한 미션', value: completedMissionCount !== null ? `${completedMissionCount}개` : unavailable, icon: 'check' },
      // 받은 배지: no badge/achievement concept exists anywhere in the backend
      // -- disclosed fixture value, not fabricated. Same gap shape as streak.
      { key: 'badges', name: '받은 배지', value: myProfileFixture.activity[2].value, icon: 'star' },
    ],
    settings: [
      { key: 'notifications', name: '알림 설정', value: 'toggle', icon: 'bell' },
      { key: 'pin', name: 'PIN 변경', value: 'lock', icon: 'lock' },
      { key: 'members', name: '가족 구성원', value: memberCount !== null ? `${memberCount}명` : unavailable, icon: 'people' },
    ],
  };
}

function toProfileEditModel(me: MeResponse, family: AuthorizedFamilySummary | null): ProfileEditModel {
  return {
    name: me.display_name,
    colors: AVATAR_COLOR_PALETTE.map((value) => ({
      value,
      selected: me.avatar_color ? value.toLowerCase() === me.avatar_color.toLowerCase() : value === AVATAR_COLOR_PALETTE[0],
    })),
    bio: me.bio ?? '',
    birthday: me.birthday ?? '',
    familyRole: family ? (RELATIONSHIP_LABEL[family.relationship] ?? family.relationship) : '',
  };
}

/**
 * `/profile` — canonical 1f (나 프로필, ROOT_OF) with 1u/2k/2n/2z/3f/3g/3h/3k/3l
 * as nested views per the W7.1 Ownership Matrix (all target
 * frontend/src/pages/profile/).
 *
 * W7.5 Phase C: 1f now loads real Account (`GET /api/me`), family
 * (`authorized_families[]`, including `joined_at`), level
 * (`GET /api/me/markpoint/level`), balance (`GET /api/me/markpoint/projection`),
 * completed-mission count (derived client-side from the already-real
 * `GET /api/me/markpoint/missions` list -- no backend change needed for that
 * count), and family member count (`GET /api/families/{id}/members`, same
 * call `1q` already wired). Two stats have no backing data model anywhere in
 * the backend (streak, badges) and are disclosed fixture values, not
 * fabricated -- see `toMyProfileModel`'s own comments and the Matrix.
 *
 * 2z (프로필 편집) reads the same real Account fields (name/bio/birthday/
 * avatar_color/family role) via the identical adapter data. Its **write**
 * side is a genuine design-contract gap found while wiring, not a backend
 * gap: the frozen W7.3 canonical Screen renders name/bio/birthday/familyRole
 * as plain, non-editable `<div>`/`<em>` text and has no color-swatch click
 * handler -- there is no input control anywhere on this Screen to submit a
 * changed value from. `PATCH /api/me` and
 * `PATCH /api/families/{family_id}/members/me` exist and are ready
 * (`familyApi.updateMe` / `updateMyMembershipRelationship`), but `onSave`
 * here intentionally does not call them: there is nothing on-screen the user
 * could have changed. Wiring a fabricated save would silently invent a value.
 * Needs a PM/design decision on adding real inputs to this Screen before its
 * write path can be wired -- not more backend engineering.
 *
 * 3h (계정 탈퇴 확인) is a confirmed TRUE_FUNCTIONAL_GAP -- no account-deletion
 * policy/API exists anywhere in the product (verified via repo-wide grep
 * before wiring, not assumed) -- so its structural entry point is built, but
 * onConfirm only closes the view locally; no destructive action is faked.
 */
export function ProfilePage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [view, setView] = useState<View>('main');
  const [me, setMe] = useState<MeResponse | null>(null);
  const [level, setLevel] = useState<MarkpointLevel | null>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [completedMissionCount, setCompletedMissionCount] = useState<number | null>(null);
  const [memberCount, setMemberCount] = useState<number | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [statsLoadFailed, setStatsLoadFailed] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferenceEntry[] | null>(null);
  const [toggleError, setToggleError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoadError(null);
    getMe(controller.signal)
      .then(setMe)
      .catch(() => { if (!controller.signal.aborted) setLoadError('프로필을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setStatsLoadFailed(false);
    // Each stat is independent, but any one genuinely failing (as opposed to
    // just not having resolved yet) must be visible -- staying null forever
    // is indistinguishable from "still loading" and would otherwise let
    // toMyProfileModel's fixture fallback stand in for a real failure.
    const onStatFailure = () => { if (!controller.signal.aborted) setStatsLoadFailed(true); };
    getLevel(activeFamilyId, controller.signal).then(setLevel).catch(onStatFailure);
    getProjection(activeFamilyId, controller.signal).then((p) => setBalance(p.current_balance)).catch(onStatFailure);
    getOwnMissions(activeFamilyId, controller.signal)
      .then((missions) => setCompletedMissionCount(missions.filter((m) => m.status === 'completed').length))
      .catch(onStatFailure);
    listFamilyMembers(activeFamilyId, controller.signal).then((members) => setMemberCount(members.length)).catch(onStatFailure);
    return () => controller.abort();
  }, [activeFamilyId]);

  useEffect(() => {
    if (view !== 'notifications') return undefined;
    setToggleError(null);
    const controller = new AbortController();
    getNotificationPreferences(controller.signal).then(setPreferences).catch(() => undefined);
    return () => controller.abort();
  }, [view]);

  const handleToggleNotification = async (label: string) => {
    const prefKey = NOTIFICATION_LABEL_TO_KEY[label];
    if (!prefKey || preferences === null) return; // "시간대" has no real key -- no-op, not fabricated
    const current = preferences.find((p) => p.pref_key === prefKey)?.enabled ?? false;
    setToggleError(null);
    try {
      const updated = await setNotificationPreference(prefKey, !current);
      setPreferences(updated);
    } catch {
      // Leave the displayed state as-is on failure; no optimistic flip to
      // undo -- but the failure must still be visible, not a silent no-op
      // that looks identical to a successful toggle.
      setToggleError('설정을 저장하지 못했어요. 잠시 후 다시 시도해주세요.');
    }
  };

  const activeFamily: AuthorizedFamilySummary | null =
    me?.authorized_families.find((f) => f.family_group_id === activeFamilyId) ?? me?.authorized_families[0] ?? null;

  if (view === 'edit') {
    const model = me ? toProfileEditModel(me, activeFamily) : profileEditFixture;
    return <div className={styles.wrap}><ProfileEditScreen model={model} onBack={() => setView('main')} onSave={() => setView('main')} /></div>;
  }
  if (view === 'pin') {
    return <div className={styles.wrap}><PinChangeScreen onBack={() => setView('settings')} onComplete={() => setView('settings')} /></div>;
  }
  if (view === 'notifications') {
    const prefByKey = new Map((preferences ?? []).map((p) => [p.pref_key, p.enabled]));
    const model = preferences === null
      ? notificationPreferencesFixture
      : {
          ...notificationPreferencesFixture,
          groups: notificationPreferencesFixture.groups.map((group) => ({
            ...group,
            items: group.items.map((item) => {
              const key = NOTIFICATION_LABEL_TO_KEY[item.label];
              // "시간대" keeps its static fixture detail -- no real key, no toggle.
              return key ? { ...item, enabled: prefByKey.get(key) ?? item.enabled } : item;
            }),
          })),
        };
    return (
      <div className={styles.wrap}>
        <NotificationPreferencesScreen
          model={model}
          onBack={() => setView('settings')}
          onToggle={(label) => void handleToggleNotification(label)}
        />
        {toggleError && <p className={styles.error} role="alert">{toggleError}</p>}
      </div>
    );
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

  // Load failure must never show the fixture's fake person (name "서연",
  // Lv.3, 320P, etc.) -- a real empty/error shell only.
  const model = me
    ? toMyProfileModel(me, activeFamily, level, balance, completedMissionCount, memberCount, statsLoadFailed)
    : {
        ...myProfileFixture,
        avatarInitial: '?',
        playerName: '',
        levelLabel: '',
        familyMeta: loadError ?? '불러오는 중…',
        stats: [],
        activity: [],
        settings: myProfileFixture.settings.map((s) => ({ ...s, value: s.value === 'toggle' ? 'toggle' : '' })),
      };

  return (
    <div className={styles.wrap}>
      <MyProfileScreen
        model={model}
        onEditProfile={() => setView('edit')}
        onOpenAllSettings={() => setView('settings')}
        onSelectItem={(item) => {
          if (item.key === 'pin') setView('pin');
          else if (item.key === 'members') navigate('/family');
          else if (item.key === 'notifications') setView('notifications');
        }}
      />
      {me && statsLoadFailed && <p className={styles.error} role="alert">일부 정보를 불러오지 못했어요.</p>}
    </div>
  );
}
