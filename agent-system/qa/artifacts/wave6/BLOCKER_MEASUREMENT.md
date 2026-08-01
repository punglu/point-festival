# Wave 6 blocker — raw credential/endpoint measurement

Captured 2026-08-01 against the isolated `mc_phase1` stack, current source
(fingerprint `6807ece0…5df`, guard PASS).

Both tokens obtained through the product's own login routes:

```
account : POST /api/auth/account/login  {"username":"member.a", ...}   -> 152-char JWT
legacy  : POST /api/auth/login          {"player_id":4,"pin":"1234"}   -> 192-char JWT
```

| endpoint | Account token | legacy player token |
|---|---|---|
| `/api/account-context` | **401** | 200 |
| `/api/families/1/wagle/room-summaries` | **401** | 403 |
| `/api/me/markpoint/projection?family_id=1` | 200 | **401** |
| `/api/me/markpoint/weekly?family_id=1` | 200 | **401** |
| `/api/families/1/markpoint/missions` | 403 | **401** |
| `/api/families/1/markpoint/config` | 200 | **401** |

Auth dependency census (`grep` over the routers, counts are route-level):

```
family router            : 14 x Depends(get_current_user)   5 account-native
wagle router             : 15 x Depends(get_current_user)   0 account-native
markpoint_target router  :  0 legacy                       21 account-native
markpoint_access router  :  0 legacy                        3 account-native
```

`/api/account-context` resolves identity through `service.resolve_current_account`,
which reads `LegacyIdentityMapping` — so it requires a legacy player/admin
token by construction and rejects an Account Session with
`유효하지 않은 토큰 역할입니다`.

**Consequence:** no single credential reaches both the family context and the
Markpoint Target API. The family context store supplies `activeFamilyId` to
every Target screen, so the whole Wave 6 UI cannot function at runtime with
either token.
