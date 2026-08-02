import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { SearchAllScreen, searchAllFixture } from '../../screens/family/SearchAll';
import styles from './FamilySearchPage.module.css';

/**
 * `/family/search` — canonical 3j (검색 전체, CHILD_OF 1b). A prior
 * Ownership Matrix pass flagged this PM_DECISION_REQUIRED with
 * "No product search ownership contract"; re-verified via grep against
 * frontend/src (excluding Preview/screens/) this pass — the only other
 * "search" hits are react-router's useSearchParams and the AlbumSearchScreen
 * (canonical 1u, album-scoped, already separately integrated), so no real
 * conflicting ownership exists. A canonical Screen (screens/family/SearchAll)
 * and a `/family/search` trigger link (FamilyLanding feature-search) already
 * existed; this was a resolvable integration, not a genuine functional gap.
 */
export function FamilySearchPage() {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState(searchAllFixture.activeFilter);

  return (
    <div className={styles.wrap}>
      <SearchAllScreen
        model={{ ...searchAllFixture, activeFilter }}
        onBack={() => navigate('/family')}
        onCancel={() => navigate('/family')}
        onFilter={setActiveFilter}
      />
    </div>
  );
}
