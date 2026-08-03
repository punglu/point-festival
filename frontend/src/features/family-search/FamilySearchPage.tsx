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
 *
 * W7.5 Phase D SLICE-SEARCH: `GET /api/families/{family_id}/search?q=`
 * exists and is real and tested — a cross-entity search over Markpoint
 * mission titles and the caller's own visible Wagle messages (scoped first
 * pass, per the Phase D Slice Mapping; Album/Schedule search deliberately
 * not folded in here to keep this Slice's declared scope from growing
 * mid-implementation). **Design-contract gap found while wiring, same
 * shape as `2z`/`3b`**: the frozen canonical Screen's own search box
 * (`.searchBox`) renders `<span>{model.query}</span>` — a static label, not
 * an `<input>` — and the entry link from `FamilyLanding` passes no initial
 * query either. There is nothing on this Screen a real query could come
 * from, so the real, tested endpoint is not called here; wiring it to a
 * fabricated query would show fake-looking real data. Needs a PM/design
 * decision to add a real search input before this Screen's read side can
 * be used.
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
