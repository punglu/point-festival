# Phase 1 Permission Matrix

**Status: APPROVED FOUNDATION REGISTRY / v0.1 (2026-07-26)**

This is a minimum registry, not a preallocation of every future permission.
`ALLOW` means an explicit permission bundle is expected; `OWN_ONLY` means the
current Account must additionally own the resource within the active Family;
`SERVICE_ROLE` means the named active service role (or an explicitly mapped
family role) is required; `PM_GATE` remains undecided. Backend enforces all
cells; frontend only presents UX.

| Action / permission candidate | owner | admin | member | restricted_member | service role / resource rule |
| --- | --- | --- | --- | --- | --- |
| `family.read` | ALLOW | ALLOW | ALLOW | ALLOW | active Membership required |
| `family.settings.manage` | ALLOW | PM_GATE | DENY | DENY | `family.settings.manage` |
| `family.members.read` | ALLOW | ALLOW | PM_GATE | PM_GATE | privacy policy follows PM Gate |
| `family.members.invite` | ALLOW | ALLOW | DENY | DENY | `family.members.invite` |
| `family.members.update` | ALLOW | ALLOW | DENY | DENY | cannot bypass owner safeguards |
| `family.members.remove` | ALLOW | ALLOW | DENY | DENY | final-owner rule applies |
| `family.roles.assign` | ALLOW | PM_GATE | DENY | DENY | no actor may grant beyond approved delegation policy |
| `family.ownership.transfer` | ALLOW | DENY | DENY | DENY | atomic owner-transfer workflow |
| `family.close` | ALLOW | DENY | DENY | DENY | closure lifecycle is deferred |
| `services.read` | ALLOW | ALLOW | ALLOW | ALLOW | active Membership required |
| `services.subscribe` | ALLOW | PM_GATE | DENY | DENY | subscription owner/control policy gate |
| `services.manage` | ALLOW | PM_GATE | DENY | DENY | service governance gate |
| `markpoint.own_missions.read` | ALLOW | ALLOW | OWN_ONLY | OWN_ONLY | target MarkPoint mapping required |
| `markpoint.missions.manage` | ALLOW | ALLOW | DENY | DENY | or `mission_manager` service role |
| `markpoint.own_points.read` | ALLOW | ALLOW | OWN_ONLY | OWN_ONLY | current actor's mapped participant only |
| `markpoint.points.adjust` | ALLOW | ALLOW | DENY | DENY | or `point_admin` service role; audit required |
| `markpoint.levels.manage` | ALLOW | ALLOW | DENY | DENY | explicit management permission |
| `markpoint.templates.manage` | ALLOW | ALLOW | DENY | DENY | `mission_manager` may be mapped later |
| `messaging.participate` | ALLOW | ALLOW | ALLOW | PM_GATE | membership plus room participation boundary |
| `messaging.rooms.create` | ALLOW | ALLOW | PM_GATE | DENY | `room_admin` can be delegated |
| `messaging.rooms.manage` | ALLOW | ALLOW | DENY | DENY | `room_admin` may be mapped later |
| `messaging.members.manage` | ALLOW | ALLOW | DENY | DENY | room/family boundary required |

## Role bundles

Initial mappings should remain deliberately small:

- `owner` contains all approved `admin` permissions plus ownership transfer,
  family close, and highest-level settings/subscription permissions.
- `admin` contains delegated family administration and explicitly approved
  service management; it does not inherently transfer ownership or close family.
- `member` contains read/participation and `OWN_ONLY` permissions, not
  cross-member management.
- `restricted_member` begins default-deny and receives only explicitly approved
  own-data/participation permissions.
- `mission_manager`, `point_admin`, and `room_admin` map only their service
  permissions and require the relevant active service subscription.

The `PM_GATE` cells are intentionally not guessed in API code. Foundation must
implement only approved cells and make absent permission mappings deny by
default.
