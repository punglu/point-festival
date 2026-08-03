import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyRulesScreen, familyRulesFixture } from '../../screens/family/FamilyRules';
import { FamilyRulesGuideScreen, familyRulesGuideFixture } from '../../screens/family/FamilyRulesGuide';
import { listRules, type FamilyRule } from '../../shared/api/familyRulesApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './FamilyRulesPage.module.css';

type View = 'rules' | 'guide';

/**
 * `/family/rules` — canonical 1v (가족 규칙, W7.5 Phase D SLICE-FAMILY-RULES)
 * with 2q nested (static guide content, unrelated to this Slice).
 *
 * Read side is real (`GET /api/families/{id}/rules`) with a real empty
 * state when a family has never set any. **Editing stays a disclosed gap,
 * not a backend gap**: the frozen canonical Screen has no form behind
 * "저장"/"규칙 선택"/"규칙 추가" — a real `PUT` (whole-list replace,
 * `FAMILY_MEMBERS_MANAGE`-gated) exists and is tested, but nothing on this
 * Screen collects a category/label/value to send it.
 */
export function FamilyRulesPage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [view, setView] = useState<View>('rules');
  const [rules, setRules] = useState<FamilyRule[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setLoadError(null);
    listRules(activeFamilyId, controller.signal)
      .then(setRules)
      .catch(() => { if (!controller.signal.aborted) setLoadError('가족 규칙을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, [activeFamilyId]);

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

  const lifeRules = (rules ?? []).filter((r) => r.category === 'life').map((r) => ({ name: r.label, value: r.value_text }));
  const pointRules = (rules ?? []).filter((r) => r.category === 'point').map((r) => ({ name: r.label, value: r.value_text }));
  // Loading and load-failure must never show the fixture's fake rule
  // content (e.g. "저녁 식사 시간: 오후 7:00") -- only real rules, a real
  // empty-state placeholder, or a real error message ever render here.
  const model = {
    ...familyRulesFixture,
    heroBody: loadError ?? familyRulesFixture.heroBody,
    lifeRules: rules === null ? [] : lifeRules.length > 0 ? lifeRules : [{ name: '등록된 생활 규칙이 없어요', value: '' }],
    pointRules: rules === null ? [] : pointRules.length > 0 ? pointRules : [{ name: '등록된 포인트 규칙이 없어요', value: '' }],
  };

  return (
    <div className={styles.wrap}>
      <FamilyRulesScreen
        model={model}
        onBack={() => navigate('/family')}
        onSave={() => undefined}
        onSelectRule={() => undefined}
        onAddRule={() => undefined}
      />
      <button type="button" className={styles.guideLink} onClick={() => setView('guide')}>가족 규칙 안내 보기</button>
    </div>
  );
}
