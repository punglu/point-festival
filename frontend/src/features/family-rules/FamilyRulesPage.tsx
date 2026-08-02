import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyRulesScreen, familyRulesFixture } from '../../screens/family/FamilyRules';
import { FamilyRulesGuideScreen, familyRulesGuideFixture } from '../../screens/family/FamilyRulesGuide';
import styles from './FamilyRulesPage.module.css';

type View = 'rules' | 'guide';

/**
 * `/family/rules` — canonical 1v (가족 규칙, CHILD_OF 1b) with 2q nested.
 * frontend/src/features/family-rules/ was an empty scaffold with no real
 * entry point before this pass.
 */
export function FamilyRulesPage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('rules');

  if (view === 'guide') {
    return (
      <div className={styles.wrap}>
        <FamilyRulesGuideScreen
          model={familyRulesGuideFixture}
          onBack={() => setView('rules')}
          onConfirm={() => setView('rules')}
        />
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <FamilyRulesScreen
        model={familyRulesFixture}
        onBack={() => navigate('/family')}
        onSave={() => undefined}
        onSelectRule={() => undefined}
        onAddRule={() => undefined}
      />
      <button type="button" className={styles.guideLink} onClick={() => setView('guide')}>가족 규칙 안내 보기</button>
    </div>
  );
}
