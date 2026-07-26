# Doran Service Dock Preferences R2

**Status:** APPROVED CONTRACT / canonical R2 (2026-07-26)
**Current delivery state:** NOT IMPLEMENTED / Foundation R2-B and Frontend UX.

## PM-approved product behavior

The four default services are initial seed choices, not permanently fixed Dock
slots. A user may remove every Dock service; the all-services entry point always
remains available. Removing a Dock item never unsubscribes a Family service or
revokes a permission, and adding one never grants either.

Dock preference is scoped to **Account + Family** and stored by the backend as
the source of truth. It synchronizes across devices. Browser `localStorage` may
be an optimization cache only and cannot be the authority.

## Data and display model

Recommended persisted fields are:

| Field | Meaning |
| --- | --- |
| `account_id`, `family_id`, `service_id` | validated preference identity and scope |
| `placement_status` | `PINNED` or `HIDDEN` |
| `sort_order` | validated user ordering among pinned services |
| `preference_version` | optimistic multi-device conflict control |
| `created_at`, `updated_at` | audit and conflict metadata |

Final Dock visibility is the intersection of active service availability,
Family subscription, User permission, and this preference. A hidden/ineligible
item is not executable. When permission or subscription returns, an existing
preference may be restored. Account/Family changes must never mix preferences.

## Seed and lifecycle

- Apply the initial default seed only when the Account+Family has no preference
  record; do not overwrite an explicit existing configuration.
- New default services do not automatically alter existing users' explicit Dock.
- Users can add, hide, reorder, and reset to the then-current default seed from
  the all-services entry point.
- The all-services entry point cannot be hidden by preference.
- Backend validates service identifiers, service availability, duplicate rows,
  status, and ordering bounds.

## Multi-device conflict policy

`preference_version` is an integer. Every mutation supplies `expected_version`;
the backend compare-and-updates it and returns HTTP 409 on mismatch. The client
reloads the current preference, reapplies the user's requested intent, and
retries deliberately. Automatic last-write-wins overwrite is prohibited. Exact
endpoint shape and ordering maximum remain implementation details.

## Authority separation

Family service installation is separate from a user's service permission, which
is separate from Dock placement. Neither Family owner/admin nor a service
administrator gains Doran Room access through Dock preference. A Dock change
does not change subscription, permission, Room participation, Service Principal
scope, or service binding.

## Deferred implementation

Backend table/migration, API, authorization tests, sync UI, and all-services UI
are not delivered by the isolated Doran Foundation draft. They belong to
Foundation R2-B and Frontend UX after the relevant numeric limits/API details are
approved.
