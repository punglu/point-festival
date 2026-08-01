# MONGLE W6 Canonical UI Recovery Manifest

Task: `MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001`.

| source | size | sha256 | state | classification |
|---|---:|---|---|---|
| mobile HTML | 636567 | d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9 | tracked @ `0c2a040` | extended mobile structure |
| tablet HTML | 831509 | 24a02ab63b7e4aafccbbc064ba7f99d1ffe429ef4f43f8427f6699defcf571d6 | tracked @ `0c2a040` | tablet canonical master |
| tokenized HTML | 471252 | 1d11874d0bceb227b5cecd81bdb8954fd3d620818292f9b608300aa925da5327 | tracked @ `0c2a040` | partial derivative |
| style guide | 15170 | 50a6d5732ebdc27ddc5ce9e81d4b97cec8b74a74e13df1940b42ea99503ce41c | tracked @ `0c2a040` | approved visual guide |
| token CSS / JSON | 10935 / 10402 | 299d85c13d8ee43d4e020c357e7a095aced1bd7544436c71cf5520bbc433fff4 / 5b090133b3524d2b54399e47aaacca451d6c22203e397095f54f3ba942b6da5f | tracked @ `0c2a040` | canonical tokens |
| token/classification registers (4) | 4379 / 7015 / 2417 / 1971 | manifest-verified | tracked @ `0c2a040` | token/component/local/one-off rules |
| approved PNGs (login/home/point/chat/admin) | 1162884 / 1281570 / 1391374 / 1237417 / 1152637 | manifest-verified | tracked @ `0c2a040` | Tier 1M screens |
| SHA manifest / provenance | 2910 / 9871 | d32d64ed62056b88e87ca8b3a35d6e7ebc8c13f5ca58a5eb8c0d3459e74fede8 / e9dca5af6234e270fd0db5d48cb1ff77525514ef74f3b6e43c1fa94762fac190 | tracked @ `0c2a040` | integrity and authority |

All paths are under `engineering/phase2/evidence/mongle-wave6-tablet-canonical/`.
Manifest SHA values were rehashed and match `SHA256_MANIFEST.txt`.

Mobile parser result: 76 labeled nodes, 74 unique labels, 64 literal DOM IDs;
`1y` has three states and `2d` two steps, yielding 66 operational canonical IDs
and 69 live labeled states/steps. Seven unkeyed labels are superseded. Tablet
parser result: 66 keys inferred from the paired labels, 2 orientations, 132
renders, zero duplicate key/orientation pairs. Canonical CSS has 92 unique
declarations. R1 imports only its measured token delta; wholesale import is NO.

Parked, not deleted: `shared/api/{accountAuthApi,markpointApi,wagleApi}.ts`,
`useAuthStore.ts`, generated OpenAPI, access/session logic and functional E2E
intent. Noncanonical connected route count is zero after this baseline.
