# Authorization Threat Model: Account, Family, and RBAC

**Status: APPROVED FOUNDATION THREAT MODEL / v0.1 (2026-07-26)**

| Threat | Backend control | Required Foundation evidence |
| --- | --- | --- |
| Caller substitutes another `family_id` | resolve active Membership and compare resource Family Group | A-family account cannot read/write B-family resource; DB invariant |
| Caller substitutes `membership_id` | load Membership by Account + Family context, never trust request ID alone | foreign Membership request denied |
| Caller substitutes `player_id` | resolve current mapped participant from Account/Membership or require delegated permission | self/other matrix and unchanged DB after denial |
| Client forges role name | server joins active Membership roles and registry mappings | altered client claim/body cannot gain permission |
| JWT carries stale permissions | JWT identifies Account only; server evaluates current membership | role removal/suspension immediately denies existing session |
| Account/Membership soft-deleted | active-state predicates in shared guards | deleted account or membership gets no permission |
| Final owner removed | atomic owner transfer/removal rule | final-owner removal rejected; no partial write |
| Admin self-escalates | explicit `family.roles.assign` delegation policy and audit | actor cannot grant owner/unapproved role |
| Service is unsubscribed | require active subscription plus scoped service role | service-role request denied after unsubscribe |
| Legacy mapping collision | unique source mapping and reviewed ambiguity state | duplicate/ambiguous mapping blocked from activation |
| Two families' data mix | non-null resource family FK and resource/membership join | cross-family API + DB suite |
| Frontend view bypass | backend `require_permission` and ownership guard | direct HTTP request remains denied |

## Guard composition target

```text
require_account
→ require_active_membership(family context)
→ require_permission(permission)
→ require_family_resource(resource)
→ optional require_self_or_permission(own permission, delegated permission)
```

Exact function/module names follow the existing backend layout during Foundation;
they are not created by this document. Errors must not disclose protected
resource existence beyond the approved API policy. Rejected writes must leave
domain rows and security/audit state unchanged except deliberately recorded,
safe audit events.
