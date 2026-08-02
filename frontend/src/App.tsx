import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { useAuthStore } from './shared/stores/useAuthStore';
import ToastContainer from './shared/components/Toast/ToastContainer';
import { FamilyContextLoader } from './shared/family/FamilyContextLoader';
import { MongleAppShell } from './platform/shell/MongleAppShell';
import A1AccountLoginPage from './pages/A1AccountLogin';
import { PointFestivalPreview } from './pages/PointFestivalPreview';
import { FamilyHomePreview } from './pages/FamilyHomePreview';
import { AdminPointManagementPreview } from './pages/AdminPointManagementPreview';
import { FamilyChatPreview } from './pages/FamilyChatPreview';
import { MyProfilePreview } from './pages/MyProfilePreview';
import { FamilySchedulePreview } from './pages/FamilySchedulePreview';
import { FamilyTodoPreview } from './pages/FamilyTodoPreview';
import { FamilyAlbumPreview } from './pages/FamilyAlbumPreview';
import { MissionDetailPreview } from './pages/MissionDetailPreview';
import { RewardExchangePreview } from './pages/RewardExchangePreview';
import { NotificationListPreview } from './pages/NotificationListPreview';
import { ScheduleAddPreview } from './pages/ScheduleAddPreview';
import { PhotoDetailPreview } from './pages/PhotoDetailPreview';
import { PinEntryPreview } from './pages/PinEntryPreview';
import { AccountLockPreview } from './pages/AccountLockPreview';
import { MissionApprovalPreview } from './pages/MissionApprovalPreview';
import { FamilyMembersPreview } from './pages/FamilyMembersPreview';
import { OnboardingPreview } from './pages/OnboardingPreview';
import { MissionRejectPreview } from './pages/MissionRejectPreview';
import { ChatSettingsPreview } from './pages/ChatSettingsPreview';
import { PinChangePreview } from './pages/PinChangePreview';
import { FamilyRulesPreview } from './pages/FamilyRulesPreview';
import { AlbumSearchPreview } from './pages/AlbumSearchPreview';
import { WeeklyReportPreview } from './pages/WeeklyReportPreview';
import { BasicModalPreview } from './pages/BasicModalPreview';
import { UserManagementDetailPreview } from './pages/UserManagementDetailPreview';
import { FileViewerPreview } from './pages/FileViewerPreview';
import { LevelUpPreview } from './pages/LevelUpPreview';
import { MissionManagementPreview } from './pages/MissionManagementPreview';
import { ChildInvitePreview } from './pages/ChildInvitePreview';
import { ChatReplyPreview } from './pages/ChatReplyPreview';
import { ExchangeConfirmPreview } from './pages/ExchangeConfirmPreview';
import { ParentDashboardPreview } from './pages/ParentDashboardPreview';
import { RewardShopPreview } from './pages/RewardShopPreview';
import { SettingsListPreview } from './pages/SettingsListPreview';
import { ProfileSelectorPreview } from './pages/ProfileSelectorPreview';
import { MissionCreateFormPreview } from './pages/MissionCreateFormPreview';
import { MissionDetailFormPreview } from './pages/MissionDetailFormPreview';
import { NotificationPreferencesPreview } from './pages/NotificationPreferencesPreview';
import { PointPolicyEditorPreview } from './pages/PointPolicyEditorPreview';
import { InvitationListPreview } from './pages/InvitationListPreview';
import { FamilyRulesGuidePreview } from './pages/FamilyRulesGuidePreview';
import { FamilyActivityLogPreview } from './pages/FamilyActivityLogPreview';
import { PinInitialSetupPreview } from './pages/PinInitialSetupPreview';
import { AdminNotificationSendPreview } from './pages/AdminNotificationSendPreview';
import { ScheduleDetailPreview } from './pages/ScheduleDetailPreview';
import { AlbumUploadProgressPreview } from './pages/AlbumUploadProgressPreview';
import { FamilyInviteAcceptancePreview } from './pages/FamilyInviteAcceptancePreview';
import { MissionStatisticsDashboardPreview } from './pages/MissionStatisticsDashboardPreview';
import { AlbumShareSettingsPreview } from './pages/AlbumShareSettingsPreview';
import { ProfileEditPreview } from './pages/ProfileEditPreview';
import { CalendarSharePreview } from './pages/CalendarSharePreview';
import { MissionStatisticsFilterPreview } from './pages/MissionStatisticsFilterPreview';
import { FamilyBoardPreview } from './pages/FamilyBoardPreview';
import { CommentComposerPreview } from './pages/CommentComposerPreview';
import { PopularPostsPreview } from './pages/PopularPostsPreview';
import { LanguageSettingsPreview } from './pages/LanguageSettingsPreview';
import { ThemeSettingsPreview } from './pages/ThemeSettingsPreview';
import { AccountDeletionConfirmPreview } from './pages/AccountDeletionConfirmPreview';
import { FamilyInviteCancelPreview } from './pages/FamilyInviteCancelPreview';
import { SearchAllPreview } from './pages/SearchAllPreview';
import { WidgetGalleryPreview } from './pages/WidgetGalleryPreview';
import { ShortcutEditorPreview } from './pages/ShortcutEditorPreview';
import pageStyles from './platform/pages/PlatformPages.module.css';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuthStore();
  if (!isLoggedIn) return <Navigate to="/" replace />;
  return <>{children}</>;
}

// MONGLE-FE-ROUTE-ALIGNMENT-001 Wave 4: 등록되지 않은 경로 접근 시 빈 화면 대신
// 안내와 복귀 링크를 보여준다. 기존 route는 전혀 변경하지 않는다(최소 범위 복구).
function NotFoundPage() {
  return (
    <section className={pageStyles.page} role="alert">
      <h1>페이지를 찾을 수 없어요</h1>
      <p>주소가 바뀌었거나 존재하지 않는 페이지입니다.</p>
      <Link to="/">몽글로 돌아가기</Link>
    </section>
  );
}

function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, isAdmin } = useAuthStore();
  if (!isLoggedIn || !isAdmin) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function ProductContext({ children }: { children: React.ReactNode }) {
  return <FamilyContextLoader>{children}</FamilyContextLoader>;
}

export default function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          {/* "/" → 플레이어 선택 + PIN 인증 */}
          <Route
            path="/"
            element={
              <ProductContext><div data-domain="user"><AuthPage /></div></ProductContext>
            }
          />

          {/* "/dashboard" → 인증된 플레이어만 접근 */}
          <Route
            path="/dashboard"
            element={
              <ProductContext><ProtectedRoute>
                <MongleAppShell><div data-domain="user"><UserDashboard /></div></MongleAppShell>
              </ProtectedRoute></ProductContext>
            }
          />

          {/* "/admin/*" → Admin 계정만 접근 (내부 라우팅은 AdminDashboard/index.tsx) */}
          <Route
            path="/admin/*"
            element={
              <ProductContext><AdminProtectedRoute>
                <MongleAppShell><div data-domain="admin"><AdminDashboard /></div></MongleAppShell>
              </AdminProtectedRoute></ProductContext>
            }
          />

          {/* Wave 6 recovery baseline: `/family`, `/markpoint*`, and `/wagle`
              remain detached from noncanonical UI. `/login` is the ordered A1
              presentation-only reconstruction; API/session code remains parked. */}
          <Route path="/login" element={<ProductContext><A1AccountLoginPage /></ProductContext>} />

          {/* Wave 6 1b mobile visual-only preview (A2 가족 플랫폼 홈). Like 1c and
              1e it is deliberately not product navigation: no API, session,
              storage or dashboard connection, and it does NOT replace the
              `/family` product route. */}
          <Route path="/__wave6/1b" element={<FamilyHomePreview />} />

          {/* Wave 6 1c visual-only preview. This is intentionally not product
              navigation and has no API, session or dashboard connection. */}
          <Route path="/__wave6/1c" element={<PointFestivalPreview />} />

          {/* Wave 6 1e desktop visual-only preview. It is intentionally detached
              from the live admin routes, data services, and product navigation. */}
          <Route path="/__wave6/1e" element={<AdminPointManagementPreview />} />

          <Route path="/__wave6/1d" element={<FamilyChatPreview />} />

          <Route path="/__wave6/1f" element={<MyProfilePreview />} />

          <Route path="/__wave6/1g" element={<FamilySchedulePreview />} />

          <Route path="/__wave6/1i" element={<FamilyTodoPreview />} />

          <Route path="/__wave6/1h" element={<FamilyAlbumPreview />} />

          <Route path="/__wave6/1k" element={<MissionDetailPreview />} />

          <Route path="/__wave6/1l" element={<RewardExchangePreview />} />

          <Route path="/__wave6/1n" element={<NotificationListPreview />} />

          <Route path="/__wave6/1o" element={<ScheduleAddPreview />} />

          <Route path="/__wave6/1p" element={<PhotoDetailPreview />} />

          <Route path="/__wave6/1j" element={<PinEntryPreview />} />
          <Route path="/__wave6/1j-1" element={<AccountLockPreview />} />
          <Route path="/__wave6/1m" element={<MissionApprovalPreview />} />
          <Route path="/__wave6/1q" element={<FamilyMembersPreview />} />
          <Route path="/__wave6/1r" element={<OnboardingPreview />} />
          <Route path="/__wave6/1s" element={<MissionRejectPreview />} />
          <Route path="/__wave6/1t" element={<ChatSettingsPreview />} />
          <Route path="/__wave6/1u" element={<PinChangePreview />} />
          <Route path="/__wave6/1v" element={<FamilyRulesPreview />} />
          <Route path="/__wave6/1w" element={<AlbumSearchPreview />} />
          <Route path="/__wave6/1x" element={<WeeklyReportPreview />} />
          <Route path="/__wave6/1z" element={<BasicModalPreview />} />
          <Route path="/__wave6/2a" element={<UserManagementDetailPreview />} />
          <Route path="/__wave6/2b" element={<FileViewerPreview />} />
          <Route path="/__wave6/2c" element={<LevelUpPreview />} />
          <Route path="/__wave6/2e" element={<MissionManagementPreview />} />
          <Route path="/__wave6/2f" element={<ChildInvitePreview />} />
          <Route path="/__wave6/2g" element={<ChatReplyPreview />} />
          <Route path="/__wave6/2h" element={<ExchangeConfirmPreview />} />
          <Route path="/__wave6/2i" element={<ParentDashboardPreview />} />
          <Route path="/__wave6/2j" element={<RewardShopPreview />} />
          <Route path="/__wave6/2k" element={<SettingsListPreview />} />
          <Route path="/__wave6/1a" element={<ProfileSelectorPreview />} />
          <Route path="/__wave6/2l" element={<MissionCreateFormPreview />} />
          <Route path="/__wave6/2m" element={<MissionDetailFormPreview />} />
          <Route path="/__wave6/2n" element={<NotificationPreferencesPreview />} />
          <Route path="/__wave6/2o" element={<PointPolicyEditorPreview />} />
          <Route path="/__wave6/2p" element={<InvitationListPreview />} />
          <Route path="/__wave6/2q" element={<FamilyRulesGuidePreview />} />
          <Route path="/__wave6/2r" element={<FamilyActivityLogPreview />} />
          <Route path="/__wave6/2s" element={<PinInitialSetupPreview />} />
          <Route path="/__wave6/2t" element={<AdminNotificationSendPreview />} />
          <Route path="/__wave6/2u" element={<ScheduleDetailPreview />} />
          <Route path="/__wave6/2v" element={<AlbumUploadProgressPreview />} />
          <Route path="/__wave6/2w" element={<FamilyInviteAcceptancePreview />} />
          <Route path="/__wave6/2x" element={<MissionStatisticsDashboardPreview />} />
          <Route path="/__wave6/2y" element={<AlbumShareSettingsPreview />} />
          <Route path="/__wave6/2z" element={<ProfileEditPreview />} />
          <Route path="/__wave6/3a" element={<CalendarSharePreview />} />
          <Route path="/__wave6/3b" element={<MissionStatisticsFilterPreview />} />
          <Route path="/__wave6/3c" element={<FamilyBoardPreview />} />
          <Route path="/__wave6/3d" element={<CommentComposerPreview />} />
          <Route path="/__wave6/3e" element={<PopularPostsPreview />} />
          <Route path="/__wave6/3f" element={<LanguageSettingsPreview />} />
          <Route path="/__wave6/3g" element={<ThemeSettingsPreview />} />
          <Route path="/__wave6/3h" element={<AccountDeletionConfirmPreview />} />
          <Route path="/__wave6/3i" element={<FamilyInviteCancelPreview />} />
          <Route path="/__wave6/3j" element={<SearchAllPreview />} />
          <Route path="/__wave6/3k" element={<WidgetGalleryPreview />} />
          <Route path="/__wave6/3l" element={<ShortcutEditorPreview />} />

          {/* MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001:
              the `/naran/*` compatibility aliases were removed by explicit PM
              cutover. They are deliberately NOT redirected — keeping them
              registered, in any form, would keep a retired platform name alive
              in the router. Those paths now fall through to the catch-all
              below and render the not-found page. */}
          {/* MONGLE-FE-ROUTE-ALIGNMENT-001 Wave 4: 등록되지 않은 모든 경로의 최소 안전망.
              기존 route의 동작·우선순위는 변경하지 않는다 — React Router는 더 구체적인
              경로를 먼저 매칭하므로 이 catch-all은 위 어떤 route도 가리지 않는다. */}
          <Route path="*" element={<ProductContext><NotFoundPage /></ProductContext>} />
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </>
  );
}
