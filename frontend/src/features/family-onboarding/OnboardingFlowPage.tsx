import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { OnboardingScreen, onboardingFixture } from '../../screens/family/Onboarding';
import { PinInitialSetupScreen, pinInitialSetupFixture } from '../../screens/auth/PinInitialSetup';
import { FamilyInviteAcceptanceScreen, familyInviteAcceptanceFixture } from '../../screens/family/FamilyInviteAcceptance';
import styles from './OnboardingFlowPage.module.css';

type Step = 'create' | 'pin' | 'invite';

/**
 * `/onboarding` — canonical 1r (온보딩, ROOT_OF) with 2s (PIN 최초 설정,
 * CHILD_OF 1r per the W7.1 Ownership Matrix) as step 2, and 2w (가족 초대
 * 수락, a separate ROOT_OF entry reachable via "이미 초대 코드가 있어요")
 * as an alternate branch. No family-creation or PIN-save API exists yet
 * (TRUE_FUNCTIONAL_GAP, W7.5 scope) — this container manages real
 * Screen-local step/digit state and advances through the flow, but does not
 * call a backend. Nothing here existed as a real product entry before this
 * pass (frontend/src/features/family-onboarding/ was an empty scaffold).
 */
export function OnboardingFlowPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('create');
  const [familyName, setFamilyName] = useState(onboardingFixture.familyName);
  const [pinDigits, setPinDigits] = useState(0);

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
                // Real PIN-save API does not exist yet — advance the local
                // flow state only, per the W7.4 data-wiring boundary.
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
        model={{ familyName }}
        onFamilyNameChange={setFamilyName}
        onNext={() => setStep('pin')}
        onHaveInviteCode={() => setStep('invite')}
      />
    </div>
  );
}
