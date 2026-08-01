/**
 * One-time migration of the active-Family selection to the Mongle key.
 *
 * MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.
 *
 * This module is the **only** place the retired platform name may appear as a
 * storage key, and it appears solely as the migration's *source* value. Once a
 * browser has run this, the retired key is gone from that browser and the app
 * reads and writes the canonical key exclusively — there is no permanent
 * fallback and no dual-write.
 *
 * The retired key is not simply dropped: doing so would silently reset every
 * existing user's selected Family on their next visit, which is a user-data
 * loss disguised as a rename. The value is carried forward first, then the old
 * key is removed.
 */

/** Canonical key. Everything outside this module uses only this. */
export function activeFamilyStorageKey(accountId: number): string {
  return `mongle.activeFamily.${accountId}`;
}

/**
 * Retired key — migration source only.
 *
 * Deliberately built from a constant rather than inlined so a repository-wide
 * rename sweep cannot silently rewrite it into the canonical key and turn this
 * migration into a no-op that discards the user's selection. That exact failure
 * (a sweep rewriting a historical value) has already happened twice in this
 * migration effort.
 */
const RETIRED_KEY_NAMESPACE = 'na' + 'ran';

function retiredActiveFamilyStorageKey(accountId: number): string {
  return `${RETIRED_KEY_NAMESPACE}.activeFamily.${accountId}`;
}

function parseFamilyId(value: string | null): number | null {
  const parsed = value === null ? Number.NaN : Number(value);
  return Number.isInteger(parsed) ? parsed : null;
}

/**
 * Resolve the stored selection, migrating the retired key forward once.
 *
 * Order, and why:
 *
 * 1. Canonical present → it is the sole source of truth, even if its value is
 *    invalid. A stale retired value must never override a newer canonical one.
 *    The retired key is still purged, because leaving it behind is what keeps
 *    the old name alive in the browser.
 * 2. Canonical absent, retired value well-formed *and* still accessible to this
 *    account → copy forward, then purge.
 * 3. Anything else (absent, malformed, or referencing a Family this account can
 *    no longer reach) → purge without adopting the value. A malformed entry
 *    must not crash startup and must not select a Family the user cannot see.
 *
 * Idempotent: after the first run the retired key no longer exists, so every
 * later call takes step 1 and changes nothing. Touches only the two keys for
 * this one `accountId` — never a wildcard scan, never another account's key,
 * never another application's key.
 */
export function resolveActiveFamilyIdWithMigration(
  accountId: number,
  accessibleFamilyIds: readonly number[],
): number | null {
  const canonicalKey = activeFamilyStorageKey(accountId);
  const retiredKey = retiredActiveFamilyStorageKey(accountId);

  const canonicalRaw = localStorage.getItem(canonicalKey);
  if (canonicalRaw !== null) {
    localStorage.removeItem(retiredKey);
    return parseFamilyId(canonicalRaw);
  }

  const retiredId = parseFamilyId(localStorage.getItem(retiredKey));
  if (retiredId !== null && accessibleFamilyIds.includes(retiredId)) {
    localStorage.setItem(canonicalKey, String(retiredId));
    localStorage.removeItem(retiredKey);
    return retiredId;
  }

  localStorage.removeItem(retiredKey);
  return null;
}

/**
 * Clear this account's selection on explicit logout/reset.
 *
 * Both names are removed so a later login cannot resurrect a pre-logout
 * selection through a retired key that migration had not yet reached.
 */
export function clearActiveFamilySelection(accountId: number): void {
  localStorage.removeItem(activeFamilyStorageKey(accountId));
  localStorage.removeItem(retiredActiveFamilyStorageKey(accountId));
}
