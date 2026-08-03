import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { OnboardingScreen, onboardingFixture } from '../../screens/family/Onboarding';
import { PinInitialSetupScreen, pinInitialSetupFixture } from '../../screens/auth/PinInitialSetup';
import { FamilyInviteAcceptanceScreen, familyInviteAcceptanceFixture } from '../../screens/family/FamilyInviteAcceptance';
import { createFamily } from '../../shared/api/familyApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './OnboardingFlowPage.module.css';

type Step = 'create' | 'pin' | 'invite';

/**
 * `/onboarding` — canonical 1r (온보딩, ROOT_OF) with 2s (PIN 최초 설정,
 * CHILD_OF 1r per the W7.1 Ownership Matrix) as step 2, and 2w (가족 초대
 * 수락, a separate ROOT_OF entry reachable via "이미 초대 코드가 있어요")
 * as an alternate branch. W7.5: `1r`'s "다음" step calls the real
 * `POST /api/families`. `2s`'s PIN entry was attempted against the real
 * Wagle device-PIN endpoint (the only Account-native PIN concept this
 * product has) and found a genuine contract mismatch, not just missing
 * wiring: the backend requires a 6-digit PIN (`PIN은 숫자 6자리여야
 * 합니다`), while this frozen W7.3 canonical Screen has a 4-dot/4-key
 * design. Extending the UI to 6 digits would be a visual-baseline
 * redesign, out of W7.5 scope — reverted to local-only flow state;
 * reclassified `DESIGN_CONTRACT_MISMATCH`/`HUMAN_GATE` in the W7.5 Matrix.
 * `2w`'s self-service invite-code join remains unwired for a separate
 * reason — no backend flow exists for it at all (`POLICY_REQUIRED`).
 */
export function OnboardingFlowPage() {
  const navigate = useNavigate();
  const reloadFamilyContext = useFamilyContextStore((state) => state.load);
  const [step, setStep] = useState<Step>('create');
  const [familyName, setFamilyName] = useState(onboardingFixture.familyName);
  const [pinDigits, setPinDigits] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleCreateFamily = async () => {
    if (!familyName.trim()) {
      setErrorMessage('가족 이름을 입력해주세요.');
      return;
    }
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await createFamily(familyName.trim());
      await reloadFamilyContext();
      setStep('pin');
    } catch {
      setErrorMessage('가족을 만들지 못했어요. 잠시 후 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (step === 'invite') {
    return (
      <div className={styles.wrap}>
        <FamilyInviteAcceptanceScreen
          model={familyInviteAcceptanceFixture}
          onAccept={() => navigate('/family')}
          onDecline={() => setStep('create')}
        />
      </div>
    );
  }

  if (step === 'pin') {
    return (
      <div className={styles.wrap}>
        <PinInitialSetupScreen
          model={{ ...pinInitialSetupFixture, filledCount: pinDigits }}
          onBack={() => setStep('create')}
          onKeyPress={() => {
            setPinDigits((n) => {
              const next = Math.min(n + 1, 4);
              if (next === 4) {
                // Real PIN-save API requires a 6-digit PIN; this Screen's
                // frozen W7.3 design is 4-digit (DESIGN_CONTRACT_MISMATCH,
                // W7.5 Matrix) — advance the local flow state only.
                setTimeout(() => navigate('/family'), 0);
              }
              return next;
            });
          }}
        />
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <OnboardingScreen
        model={{ familyName, isSubmitting, errorMessage }}
        onFamilyNameChange={setFamilyName}
        onNext={handleCreateFamily}
        onHaveInviteCode={() => setStep('invite')}
      />
    </div>
  );
}
