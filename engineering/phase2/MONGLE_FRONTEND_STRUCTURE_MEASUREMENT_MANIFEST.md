# MONGLE Frontend Structure Measurement Manifest

Task: `MONGLE-W6-FRONTEND-SOURCE-STRUCTURE-MEASUREMENT-001`  
Observed at: `2026-08-01T15:09:47Z`; branch: `dev-newmarkp`; HEAD: `78913b48e1147073f3b1c56b39de9eea28d5d9cf`.

## Measurement Command

`pwd`; `git branch --show-current`; `git rev-parse HEAD`; `git status --short`; `git diff --check`; `git ls-files frontend | sort`; `find frontend -path frontend/node_modules -prune -o -path frontend/dist -prune -o -type f -print | sort`; static relative-import extraction over `frontend/src/**/*.{ts,tsx}`.

## Output Summary

| Metric | Value |
| --- | --- |
| initial manifest SHA-256 | `8b37be767c2dd133362b6bcdd2c0edac740df794c5c2d532c494e8b4880760c5` |
| tracked files | 298 |
| worktree files | 314 |
| modified / untracked / deleted frontend paths | 8 / 14 / 0 |
| route declarations | 14 (6 top-level, 8 nested) |
| key navigation/link findings | 12 |
| relative static import statements | 420 |
| confirmed reverse dependencies | 1 |
| static import cycles | 0 |
| duplicate candidates | 4 |
| unknowns requiring decision | 5 |

This file is the complete frontend filesystem manifest. `UNTRACKED_OR_IGNORED` means present in the filesystem, absent from `git ls-files`, and not reported as an untracked path by Git. The current document hash is intentionally reported by the final verification rather than self-embedded.

## File Inventory

| path | tracked status | git status | extension | size | SHA-256 | top-level owner | candidate layer |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `frontend/.DS_Store` | UNTRACKED_OR_IGNORED | CLEAN | (none) | 6148 | eecff5a1c7e3d00289dbe4017192aea9b36d7b7823f6e9b951683a9ed9782fec | .DS_Store | application/composition |
| `frontend/.dockerignore` | TRACKED | CLEAN | (none) | 920 | 1adf252f31891b37a0b6275b87f07099a4c6d892cf2b830ecf8fc2024d01716b | .dockerignore | application/composition |
| `frontend/Dockerfile` | TRACKED | CLEAN | (none) | 1373 | 36b72ee97330b033f065cc2643e32491b62f0cdfced2ba7f916dec71ac7e7de9 | Dockerfile | application/composition |
| `frontend/eslint.config.js` | TRACKED | CLEAN | .js | 1248 | bf3aa70a11195724d738830e267e08fc4bcf7337719c68c5894e12801eb7944b | eslint.config.js | application/composition |
| `frontend/index.html` | TRACKED | CLEAN | .html | 1423 | 391ccf26e058083e4adb237bd6627e8f92880ea352e134aadd9ea0d15ef5fe3a | index.html | application/composition |
| `frontend/nginx.conf` | TRACKED | CLEAN | .conf | 3902 | d615d7a5a2b7a30769ae188d61ff4d27264de1cfb611e5b59e71bb2b5a0ba8aa | nginx.conf | application/composition |
| `frontend/package-lock.json` | TRACKED | CLEAN | .json | 136468 | f81972fdce704020e1ceae5ca1a3bdc7bf873feecb162198e3d948ddfab0e59a | package-lock.json | application/composition |
| `frontend/package.json` | TRACKED | CLEAN | .json | 1110 | 5b003a08a73d558dfb1cd7bbf55fc7a1a4a457180442f65b9384c041ba286466 | package.json | application/composition |
| `frontend/public/apple-touch-icon.png` | TRACKED | CLEAN | .png | 14232 | c71366186e47af7c6dba69f3895be5d6a2c49758022551a37f036b03dc1985ed | public | assets |
| `frontend/public/favicon-16x16.png` | TRACKED | CLEAN | .png | 533 | 511cdc0136dd4ab33816a1e5297eae40b0512ed57fe7489fd26f99a24df9642a | public | assets |
| `frontend/public/favicon-192x192.png` | TRACKED | CLEAN | .png | 15795 | 9830723e14363b02a0ede404cb9f0a24599b4040460fc80c1d2a60e9381e1434 | public | assets |
| `frontend/public/favicon-32x32.png` | TRACKED | CLEAN | .png | 1215 | b620d2a6557827bad750a74ea2a44be93c3c4c67640cbcfbc1fc7751e94fd58d | public | assets |
| `frontend/public/favicon-512x512.png` | TRACKED | CLEAN | .png | 69307 | c2d9917c943281e53a8bc8354cf04b8c6f623e645933cbf09c5b351e56012fad | public | assets |
| `frontend/public/favicon-event-32x32.png` | TRACKED | CLEAN | .png | 1674 | d73f9624aa0328c1262a87251833f9cb714ae9d12662a430eb801fd43f3ae9c4 | public | assets |
| `frontend/public/favicon.ico` | TRACKED | CLEAN | .ico | 555 | a95bc93b79fc6cce44e81b803ce2aef123c019586a926a6bfecce56874964d55 | public | assets |
| `frontend/public/logo-512.png` | TRACKED | CLEAN | .png | 164150 | de94a9fda45d87bef4c6b0f6c7be373b9c51284aabe3e6612899d4443e77a58f | public | assets |
| `frontend/public/logo-login.png` | TRACKED | CLEAN | .png | 89402 | 43fa4c58ec40c7b13f79f12a8ab0380aa6594530275c484a4bbc25537488e8ec | public | assets |
| `frontend/public/logo.png` | TRACKED | CLEAN | .png | 316590 | 03e339617af9bfbffb91930d8910fea666831dca06b82acf025dd9c3acb64b3d | public | assets |
| `frontend/public/manifest.json` | TRACKED | CLEAN | .json | 656 | fb1f5de9c75f9511c346547fac16d7e9654bf516d587375cb97da90ef2f212d3 | public | assets |
| `frontend/public/og-image.png` | TRACKED | CLEAN | .png | 157870 | d9ee3388c270988562394e39312c42e1fc8069492707b9111f0787969416dfb7 | public | assets |
| `frontend/public/sw.js` | TRACKED | CLEAN | .js | 3209 | 68d28dcc2edd2330ecbaa77f5e0038e491f74c97bfedd078c9efdc71e61e7b15 | public | assets |
| `frontend/src/.DS_Store` | UNTRACKED_OR_IGNORED | CLEAN | (none) | 6148 | 29be3b98fee728778ff8e7f66926de657e3ea0373afa4ffc95096a299a81106c | .DS_Store | application/composition |
| `frontend/src/App.tsx` | TRACKED |  M | .tsx | 4147 | a13fd79a0ae895103018f7a066f398c1f18065a578b6783ad90d900e44b7b023 | App.tsx | application/composition |
| `frontend/src/assets/icons/checklist.png` | TRACKED | CLEAN | .png | 21252 | b3aae26bff91a18867270befeb89dcf5815462a3fd64bcc853ed0620bac9c9cf | assets | assets |
| `frontend/src/assets/icons/coin.png` | TRACKED | CLEAN | .png | 12551 | bba85b6ab4cb92ab83e5dc084713ca45a7d46f3bfa54bfc2dbad9198e04be6eb | assets | assets |
| `frontend/src/assets/icons/flag.png` | TRACKED | CLEAN | .png | 18674 | 8e4daa39028b861f6627901ef0fa92c029afe4ecb91519d7f870b59234fe9466 | assets | assets |
| `frontend/src/assets/icons/gem.png` | TRACKED | CLEAN | .png | 18482 | 7094f71ca98c1a72d5f21177646be95bfec4e97b96d93d385fcd25b832810c38 | assets | assets |
| `frontend/src/assets/icons/levelup.png` | TRACKED | CLEAN | .png | 23654 | 88d01b3c55a13d440b7213192c5f5272ca3c38dae40eec42ccb2778d3f84bab1 | assets | assets |
| `frontend/src/assets/icons/lightbulb.png` | TRACKED | CLEAN | .png | 1611 | 97ab7ffcc774daee71254044e1d42dc8c6dbd58e58abb272a354493b5c416e60 | assets | assets |
| `frontend/src/assets/icons/medal-gold.png` | TRACKED | CLEAN | .png | 13351 | fde5ad0c0d0dab68f2cbbb1354e9735667627e6c83acb00d8692a1fb6830792c | assets | assets |
| `frontend/src/assets/icons/medal-silver.png` | TRACKED | CLEAN | .png | 14978 | da0542ead593d37c5ab05d4cc025ec3be16bb5462fb10b093f84ed6a1fad3e71 | assets | assets |
| `frontend/src/assets/icons/star.png` | TRACKED | CLEAN | .png | 16540 | 134850b597e9da478f32ae4ad740e2cdeb9378f6dd71de03c63a46b666af8890 | assets | assets |
| `frontend/src/assets/icons/trophy.png` | TRACKED | CLEAN | .png | 14683 | 07369393e695de5071014b1ced52e8279de6ec9e53453ff597f8c4a3cdb2a2c0 | assets | assets |
| `frontend/src/assets/logos/auth-logo.png` | TRACKED | CLEAN | .png | 222698 | 4417319771dbd08cc3e4f29f13987bbced6293986214061757fa9e87c95e24f0 | assets | assets |
| `frontend/src/assets/logos/brand-icon.png` | TRACKED | CLEAN | .png | 8333 | b0500829e4b98e8ee59e298bb5a138e8b72280436d97749fd745cea0b37d5324 | assets | assets |
| `frontend/src/assets/logos/family-platform-mascot.png` | TRACKED | CLEAN | .png | 484084 | dd5c48b3e670636b7822a5893e213ce8e99fd667b82b4cb53026e344bea4f0b8 | assets | assets |
| `frontend/src/generated/openapi.d.ts` | TRACKED |  M | .ts | 296440 | 270dbc28b23685b904d0b8d022332462d96a431a2d1fe733c9906407b044a3f0 | generated | generated |
| `frontend/src/main.tsx` | TRACKED | CLEAN | .tsx | 844 | a4c3b5b240c995e51aba14b318a1a5d7cf60636244c84ec644917dd7e53d9b4f | main.tsx | application/composition |
| `frontend/src/pages/A1AccountLogin/A1AccountLogin.module.css` | UNTRACKED | ?? | .module.css | 5623 | 2183a64af70b8d67896c278664b29fede5e95462ce8dc11f8ff982694bc64aca | pages | application/composition |
| `frontend/src/pages/A1AccountLogin/index.tsx` | UNTRACKED | ?? | .tsx | 5299 | bd4271a5d9d12b31b305d70cc13905bea206f81360e50708a20d0e628fb1b634 | pages | application/composition |
| `frontend/src/pages/AdminDashboard/AdminLayout.module.css` | TRACKED | CLEAN | .module.css | 1628 | d0ad40ab918ca4112567d790c8645340a25c3a1d1cd3fd0118b582e3fe377888 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/AdminLayout.tsx` | TRACKED | CLEAN | .tsx | 1309 | f0a21422cd9dbba86c6731ee0bf3fdafdb38176745a24ae46714b32a003ac888 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/api/adminApi.ts` | TRACKED | CLEAN | .ts | 6270 | 428544b5de154d7fbdc6aef103acc157bfcb3bc098ede6886b7446e00c502485 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/AdminBrandLogo/AdminBrandLogo.module.css` | TRACKED | CLEAN | .module.css | 613 | 67c7f6b8f69a3438aa1b69257a6f881914f183a44f8473c7af19ccd1d0190225 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/AdminBrandLogo/AdminBrandLogo.tsx` | TRACKED | CLEAN | .tsx | 627 | f29242b1fef6acacca0856e0a880635a659c1e3241c7208d14a66627594b799b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/AdminModal/AdminModal.module.css` | TRACKED | CLEAN | .module.css | 1041 | a53d3440cbbf9cd86a69c7f410c27b35c9b08b67d07e74c02f3019afeea0631d | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/AdminModal/AdminModal.tsx` | TRACKED | CLEAN | .tsx | 1569 | 75ae6d9a7ba429e05d13887e740461b0853f0ad1062ee6a1357765a8a1ac1599 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/AdminToast/AdminToast.module.css` | TRACKED | CLEAN | .module.css | 68 | a601a25246c89e94d94fec4425f2dc25f18c486c9717cc116c4f2af9b661fe86 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/AdminToast/AdminToast.tsx` | TRACKED | CLEAN | .tsx | 208 | 14f454f0cd3370ec9f168110c49457716b7b42d76aeaadae0a85d99b4004c543 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/CycleIndicator/CycleIndicator.module.css` | TRACKED | CLEAN | .module.css | 325 | f1a272d8c9a3483f9708a55a2be2a2439974cc1641dc47bd990cfa6cdc8ab9fd | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/CycleIndicator/CycleIndicator.tsx` | TRACKED | CLEAN | .tsx | 439 | 4143b69603544f5e09b902b81576228ac34b98a455fe7982a627f3c064359e96 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/DateSelector/DateSelector.module.css` | TRACKED | CLEAN | .module.css | 553 | 7ca72d8294e92e5cfbbd5d9aa03c379ae9fd4a8430e2fd8eac1941c1e616cabe | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/DateSelector/DateSelector.tsx` | TRACKED | CLEAN | .tsx | 992 | 505c706bd74c696b47db8ef492375a958b81ed4850df4297f91a3880093ef7b6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/MobileDrawer/MobileDrawer.module.css` | TRACKED | CLEAN | .module.css | 2602 | 77c15eacbcddf3738a85f187a5b140e3924088f6b5e98c00847ae74e9edb8b8b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/MobileDrawer/MobileDrawer.tsx` | TRACKED | CLEAN | .tsx | 4981 | 03f59359e28267300c62a8d667efd4dc591cc1065259bfdb481c2d3d9860bbf2 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/MobileHeader/MobileHeader.module.css` | TRACKED | CLEAN | .module.css | 3047 | b2dd9f26f2ca15e783dd0920c23ee0b9551d523afafd1922603357e813de7524 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/MobileHeader/MobileHeader.tsx` | TRACKED | CLEAN | .tsx | 4041 | 7c686514c4a5da712f6556960e7ad7349c344b10586dd705c867981712ebdc6a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/PlayerBadge/PlayerBadge.module.css` | TRACKED | CLEAN | .module.css | 407 | 2ebeb2bf581a1d27b751d89d8985e6a7f74088864c84753930b194450ba16e40 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/PlayerBadge/PlayerBadge.tsx` | TRACKED | CLEAN | .tsx | 892 | dd93af2667e41147ac244b02b1dd9723346a5621d60a8f39919036599a77167a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/PlayerTab/PlayerTab.module.css` | TRACKED | CLEAN | .module.css | 556 | d1ac1a122f241b81bc1424dba46348cf1c27d0c7b6e971d6a98100de3e8855fd | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/PlayerTab/PlayerTab.tsx` | TRACKED | CLEAN | .tsx | 742 | 6b8ce8822258ec7755ca747860b3755e0b5a061f0f87daf7a2f20db28caa93e7 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/Sidebar/Sidebar.module.css` | TRACKED | CLEAN | .module.css | 3192 | 30d4ba8a56dc839d1c5ba6ef7b41ae65bebbda965d55a561fe83e18bbf3046c9 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/Sidebar/Sidebar.tsx` | TRACKED | CLEAN | .tsx | 4978 | 353e51ac8ad47c3ad6bb97a370b47248d7ee4ba14f05a3f39b399630f7f51ad6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/StatCard/StatCard.module.css` | TRACKED | CLEAN | .module.css | 716 | a5bbb68ef4bb0b4ef19deb4d916ee280765e4628e03bfe92a58da27192134085 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/components/StatCard/StatCard.tsx` | TRACKED | CLEAN | .tsx | 744 | dedba6e57ea965682f464fba82fb352176089f440262a4ffd82b4e563ecb8c2c | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/constants/admin.constants.ts` | TRACKED | CLEAN | .ts | 2389 | 567ea61f4ace3635cef4a045ba3d73ec0d42659b018374ce8a5ed838c0118255 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/hooks/useAdminAuth.ts` | TRACKED | CLEAN | .ts | 812 | 59aed7a39233cbb55dc5e9f8578fefdc49952327a5f55e095cd451798d10efaf | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/hooks/useAdminData.ts` | TRACKED | CLEAN | .ts | 5128 | 39a65724bc51d34f3e058f9e3e94dcef7addba5ca872f588e987b47161d09069 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/hooks/useAdminToast.ts` | TRACKED | CLEAN | .ts | 87 | 3e96d2027ba3603ecb126cc645a04cb3092262a17d0a89114104089761f511f4 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/hooks/useCycle.ts` | TRACKED | CLEAN | .ts | 1155 | 414e11934d482415d14e9e7a44d606cb60918c1c22039fee367293e77ffc83bb | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/index.tsx` | TRACKED | CLEAN | .tsx | 1189 | faa4d0916c21d448b183e93a074aa3af9dc3f4da078589ad1de5946fe15a74db | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/types/admin.types.ts` | TRACKED | CLEAN | .ts | 2682 | fe67f8ffdf4455bd8ae7332dd2ba9c72f41dbb7557f8508d667749f9100f21db | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ChatView/ChatView.module.css` | TRACKED | CLEAN | .module.css | 217 | 6a268dc9a428d16f3f5ad2c87e67430b5238b6cbd46b61568511a8df51e8f947 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ChatView/ChatView.tsx` | TRACKED | CLEAN | .tsx | 819 | 5861527e2abdfbdd28bb735ccc8572e2e87664a91348e475f6fb692b1ed26508 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/ConfigView.module.css` | TRACKED | CLEAN | .module.css | 880 | 56654f23270cfbb72f33abdb5263857fc7766c180845bfc37dde6005f1673c83 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/ConfigView.tsx` | TRACKED | CLEAN | .tsx | 2102 | c5caa050011e826484d8933b306b81671cb4de8003f2db4df90e5aeb2b0bcd6f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/CheerSlotConfig.module.css` | TRACKED | CLEAN | .module.css | 1262 | 3a5b2d23ab1333c200085cef28060dd19974ab873364962455bad359807dfdfe | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/CheerSlotConfig.tsx` | TRACKED | CLEAN | .tsx | 2615 | 7dd1f8834433485294eede6134b864d070eed27ed81e0cf0ceb04589bccdae4f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/CycleConfig.module.css` | TRACKED | CLEAN | .module.css | 1256 | 1ccd704059fadc165ff77c63800e9e81f5f364703b57669ca84193deb5c48742 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/CycleConfig.tsx` | TRACKED | CLEAN | .tsx | 2630 | 5cd3735564e83dd26750711a0f051ee8e2ff7e75c8b9864b14ea04f2ef59ed30 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/LevelConfig.module.css` | TRACKED | CLEAN | .module.css | 800 | 9b8430632c1ddb1ccd3f13e46ef1675137a6be8b061e9f02bbc51b19482e0a76 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/LevelConfig.tsx` | TRACKED | CLEAN | .tsx | 1962 | c521c21f3b855d73abda97ae10fb6bffc2a3dea4be505298210d38361ae270c1 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/SystemConfig.module.css` | TRACKED | CLEAN | .module.css | 580 | 2b9b84abb9ef083fd94a8ff5e81ff8b73d688080afcb87b0d4ea064ed20fe97f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/components/SystemConfig.tsx` | TRACKED | CLEAN | .tsx | 665 | 0ddea8393195bad0b276ea42531191ce580cd259ed837c263c5937fd5ec05fa7 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/ConfigView/hooks/useConfigView.ts` | TRACKED | CLEAN | .ts | 4389 | 4e3c651c9b9cd8341e0752f5569c21e8e785eef267206d921c81fef52eab5654 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/DashboardView.module.css` | TRACKED | CLEAN | .module.css | 2470 | cdd816fb4d570cc768b61587d8ca3cf311939325bb6d30a9e68c0c7e3ef66101 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/DashboardView.tsx` | TRACKED | CLEAN | .tsx | 5180 | f431c38af904c00994afb633d04eacd00b37376632ab66f3f828a3526aa10d70 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/ActiveMissionDetailModal.tsx` | TRACKED | CLEAN | .tsx | 2966 | 5a9c8ef78f4837f8609f70dd93451a45d43aab1af0040c3d5525467b02842d92 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/BalanceSection.module.css` | TRACKED | CLEAN | .module.css | 4009 | 577c3a6613e8aab229d224e925bfab0de3a9180f689eabe2ca1eb17e3312bcbb | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/BalanceSection.tsx` | TRACKED | CLEAN | .tsx | 6934 | 7bfbf91091e22aa4a40a90643e29bfc7fc817779fbf68397e013e2174fbff391 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/CardDetailTable.module.css` | TRACKED | CLEAN | .module.css | 4018 | 6acf3424769862b77fc8fd50424ed0b9c1e12198a4ec7bfe93116121b5cd15e3 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/CardDetailTable.tsx` | TRACKED | CLEAN | .tsx | 8590 | 841fe0ddf91c63821e9b3f5e047c1161541a352475c2469dcf38233fbe119c19 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/CompletedMissionsModal.tsx` | TRACKED | CLEAN | .tsx | 3035 | 5c8e643eafddc3c94bdae8a3814675f18b83f938115dd31cb1fcb37bbfb216bb | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/DashboardModal.module.css` | TRACKED | CLEAN | .module.css | 3707 | c72612b6aa986b7998a33ffa8a3fdc283012bae143b2af8b3c0834b911ad14e6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/MissionRanking.module.css` | TRACKED | CLEAN | .module.css | 1505 | 6421e9f2a680fb872e36253f88e96baf409743daa805c29193126133fdc0fef1 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/MissionRanking.tsx` | TRACKED | CLEAN | .tsx | 2861 | 0a54c7a3e7132dfd400852584d4b171dfd1e35d44e064ad7115426497ae7b4e2 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/PendingApprovalModal.tsx` | TRACKED | CLEAN | .tsx | 3352 | 8766168640945f8fe7e2ddb16ddcbbe8697299eb0f9462bcc46f1cdb908ee6c2 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/PendingMissionCard.module.css` | TRACKED | CLEAN | .module.css | 1337 | 4c9e22a3bc14291c7eff489d8eea4ca7f785b783c7161c7a0756a1d695c2ba98 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/PendingMissionCard.tsx` | TRACKED | CLEAN | .tsx | 2247 | 7f42632213ae0c1fbbbfac11f3ea4a6eb6a93a8c22273712ec8d6881e048ef10 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/PlayerStatusCard.module.css` | TRACKED | CLEAN | .module.css | 1401 | ef3b361f8d6e108cc0a2d19dc7ffd6c9c2a7969baa933a86fa4bf7c18feef10c | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/PlayerStatusCard.tsx` | TRACKED | CLEAN | .tsx | 2633 | 15829574a3f42096d13e0d790dcf58e009f8f8bed64529b8f000dd70133a8760 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/PointHistoryModal.tsx` | TRACKED | CLEAN | .tsx | 2793 | b6af261288de8480db1a0950dae945e24b7154f71b94d76b2f6b307c40898758 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/RecentAlerts.module.css` | TRACKED | CLEAN | .module.css | 1589 | 571c3559e211e67e5923b5a2856d7124a9bed86e52136c47061cc0d9cc676e00 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/RecentAlerts.tsx` | TRACKED | CLEAN | .tsx | 2605 | 014fbc9c0f1cb9ebd8a23059c689f22ae095aa936a68ba6bea9ac553235c3f5f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/WeeklyActivityChart.module.css` | TRACKED | CLEAN | .module.css | 1620 | 6e647ba0eef04fe228ff20adea93e48daec456f4b5af88bd58426bdd940ca2d8 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/DashboardView/components/WeeklyActivityChart.tsx` | TRACKED | CLEAN | .tsx | 3444 | 371fa72d60d5e62a4c92d75d31b68818c07c1c0fe473f63ee1ac5d52291a3b1f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/FeedbackView/FeedbackView.module.css` | TRACKED | CLEAN | .module.css | 4346 | 5d49c61cd3e78ace3052b86c925619d42d926a12161d13cd557c2d8595a985e4 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/FeedbackView/FeedbackView.tsx` | TRACKED | CLEAN | .tsx | 9190 | 23262699000e2914228f7cc05447bdfd92971968849c81107338c867f7d2816b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/MissionView.module.css` | TRACKED | CLEAN | .module.css | 3167 | f3a5a01a098453fb015728a9fa4ec73660a350d464fdba6952d41b178bf1b710 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/MissionView.tsx` | TRACKED | CLEAN | .tsx | 7429 | f754bc2632c360d78c016f92400d0b617203aefec63507d7d05a84d6b6918bbc | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/BatchCopyModal.module.css` | TRACKED | CLEAN | .module.css | 3490 | b8beb77f5e8c506158d7e4fdd63109f81b8b611be2bd3993d3952c6b99acd955 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/BatchCopyModal.tsx` | TRACKED | CLEAN | .tsx | 9215 | 986a7b2c0fa130e3beb6cdebde8187f4027dd1257e98d545aaefe284efb905c6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/ImportMissionModal.module.css` | TRACKED | CLEAN | .module.css | 2564 | 216abb7e20517bceae2e4dbde08e08fc86f78b1e9ff8d0d541693db9ec45c8d0 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/ImportMissionModal.tsx` | TRACKED | CLEAN | .tsx | 5358 | a471723915e872bfbb47873b56236d4fa7c338c81b796a5f93a901fb189faeb6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/MissionCard.module.css` | TRACKED | CLEAN | .module.css | 3852 | 0609940da913ab5ce3c8aa79c9adec4cdce9bec13904cbbd062ca154e452ac8c | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/MissionCard.tsx` | TRACKED | CLEAN | .tsx | 4576 | 3b03668fea049a930a148d1b7186a62b8295817ab2db2f9df56794611d83291c | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/MissionCardEdit.module.css` | TRACKED | CLEAN | .module.css | 1627 | 42813c1529d8ca8cbaf9f38cd7733b350965c94d109391837b6e8ac11153b6f2 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/MissionCardEdit.tsx` | TRACKED | CLEAN | .tsx | 1682 | de5e66bfc6b9d123ccf9268fa2ae32b943c559be03ee5a2ef9eba5e13884ef5a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/NewMissionModal.module.css` | TRACKED | CLEAN | .module.css | 2260 | f1780ae2cdfc930fd5adb153a23b07ca411fcb971fda99823cf697c70a5ed50f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/NewMissionModal.tsx` | TRACKED | CLEAN | .tsx | 5012 | 69eb26f31757c5052e63285ca4b1a88be7bf22252533be7e3100f35e48488f4b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/ProposedMissionSection.module.css` | TRACKED | CLEAN | .module.css | 1877 | 9aa3881ebbc0e772198afb44b3248d9f50f02bd11fe0647c17ab8f71b9523d7d | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/ProposedMissionSection.tsx` | TRACKED | CLEAN | .tsx | 1593 | ca70a43f92b2251b986d1c9f181a8651dfcd6fd1b4ddef353041f6b43b8a5484 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/ScheduleManager.module.css` | TRACKED | CLEAN | .module.css | 3383 | ea6f0468afdc83e6384a74d4f4b34ed94ff7a265ffc63ad4b63ac8b2980f4b0d | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/ScheduleManager.tsx` | TRACKED | CLEAN | .tsx | 7109 | c1c29da529002af1f2419feb1c552dbb7e5aae533ca420e047cf1bc1d6240891 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/TemplateManager.module.css` | TRACKED | CLEAN | .module.css | 5414 | c8176bfa8ddcfab11f2dae459c7e2f8e35b0c249fdc4883851fd5869b8ad029e | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/TemplateManager.tsx` | TRACKED | CLEAN | .tsx | 10131 | f52ca3babfe9466685ed504d75204bee9ff4790052da40e67fae97501e724f3a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/TemplateModal.module.css` | TRACKED | CLEAN | .module.css | 2298 | 8ac855249f9d7d29b7ee730a754664b76234fcd7f8710ba54b55b3aeb65d730a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/TemplateModal.tsx` | TRACKED | CLEAN | .tsx | 5904 | caa12a4968a3f281b4c15d4ad9025759c5d06d90d94d68bd3cc9966dcbbb8919 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/WeeklyGrid.module.css` | TRACKED | CLEAN | .module.css | 5520 | 7600449b3d8f27ec01809926d14667e27b9a066097942e7c713e2591519ea90f | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/components/WeeklyGrid.tsx` | TRACKED | CLEAN | .tsx | 5467 | 800e6a788e5d5179b5cbf181253014dde5f32c1674f7ea9cf23ec0a198901ce9 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/MissionView/hooks/useMissionView.ts` | TRACKED | CLEAN | .ts | 6447 | eed92b3ab191657a49c52a13d516c99d527577fd4ee9e5104ba60df142fc27b7 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/NotificationView.module.css` | TRACKED | CLEAN | .module.css | 889 | a8cb5d07c445057349445d52313d1fa419f7ec496a975429826efc62e69b51a0 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/NotificationView.tsx` | TRACKED | CLEAN | .tsx | 1217 | cd7b2ce522d6376283bb1f184ac2e2df664b7e7ccbf1775c36621a765f7cb569 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/components/NotificationFilter.module.css` | TRACKED | CLEAN | .module.css | 717 | 3809ca456777a27a3f9e96c3fef5bf51ca8cdef8c3f7c8bc0017b82b2ae15200 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/components/NotificationFilter.tsx` | TRACKED | CLEAN | .tsx | 1046 | 94664b9a2d688c97b3137b03de231245947434a0d81407312ecab6c64ac6df6e | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/components/NotificationItem.module.css` | TRACKED | CLEAN | .module.css | 1871 | da8e19dc5b1afd6f206445c2321f4e89437b452a8b2ca005f40b2436b42dda8b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/components/NotificationItem.tsx` | TRACKED | CLEAN | .tsx | 2250 | d17dc342d1b7fe51b38c0f16649682fd68c9dd941a50b7b58b7b331a391fb06b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/NotificationView/hooks/useNotificationView.ts` | TRACKED | CLEAN | .ts | 2387 | cd2a5fe6b21ddf21a29a071da0b9a362502d70dfcbcaf1d59ce8f4c63e7e2d27 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/PlayerView.module.css` | TRACKED | CLEAN | .module.css | 816 | fb55752bac0c462fb43100addeed6fc6b4ba5adc0e43366d3b05b2d5e55e983a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/PlayerView.tsx` | TRACKED | CLEAN | .tsx | 3139 | 2899177930e18ca08f28e6b5793e9c23229408b597cd881c287f839336c84a1e | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/AddPlayerModal.module.css` | TRACKED | CLEAN | .module.css | 960 | f837bfa76733821369ebdc1ec9f9b7873e8d0a606a60fa014d7445bbd4f33e1b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/AddPlayerModal.tsx` | TRACKED | CLEAN | .tsx | 2801 | bfd19908a0d7aa77a45f444fa820fdc1842430eef78a7d9aea5249c16e6309f9 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/LoginLogTable.module.css` | TRACKED | CLEAN | .module.css | 2065 | b4d0986be5a032849bf3f56ff4c788f1abfb4090d2b6e58b5b4b2484fafc67d6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/LoginLogTable.tsx` | TRACKED | CLEAN | .tsx | 2941 | 55b3bffe7a4e421d02eaf8f9b2f2258b449ef65559ac7ad61716f5edb5b89190 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/PhotoUploadModal.module.css` | TRACKED | CLEAN | .module.css | 454 | 99b724d2ec923b0111b5410690bdcd64c1038f51f1d07c77e810e835260dec6c | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/PhotoUploadModal.tsx` | TRACKED | CLEAN | .tsx | 1383 | 055159ed87314ba3e28d9607efdf96022277bf86b667a744df7cd0516ca7cb52 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/PinChangeModal.module.css` | TRACKED | CLEAN | .module.css | 942 | e7b4fd46ed9e5516ebd79cb1ab6050dbc110a5da441187843f8d7b406177c5c2 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/PinChangeModal.tsx` | TRACKED | CLEAN | .tsx | 2369 | 6991844a91090df02d286d0d3cba29fdedf6697ede16876a9872a0a182bd3142 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/PlayerProfileCard.module.css` | TRACKED | CLEAN | .module.css | 2394 | bfd6f658bb2a0799783a29aefd5a197b57e890567859706957e069db4ac2d31a | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/components/PlayerProfileCard.tsx` | TRACKED | CLEAN | .tsx | 3015 | 321adfe8a9e0782c8a2e5cde7b478bbdf23792e0d0cbc6b1b134740a2b8255f3 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PlayerView/hooks/usePlayerView.ts` | TRACKED | CLEAN | .ts | 3146 | ea3102f4dd8a7b65ea2520b1f6874dc4cf517a9a90d7139fa82e75bde9501897 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/PointView.module.css` | TRACKED | CLEAN | .module.css | 1596 | f7ba18af98a3fc1a5d1b5312b7a2da29b2b3bc679c007e2705c60536cc6ce51d | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/PointView.tsx` | TRACKED | CLEAN | .tsx | 3068 | 8805e4316e258b7cb82f430d3176855ae60474ef4152293d4f04e9179d7313b6 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/AddDeductionModal.module.css` | TRACKED | CLEAN | .module.css | 1841 | 29dc412ea95c347b3f7be262c8c19f57ec76f77c6c2ef33954cef2fe15e363c8 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/AddDeductionModal.tsx` | TRACKED | CLEAN | .tsx | 4601 | 7e7a9225414d0dc207e259237feeff90613b8a4aba574aa32a3e26e79cb70186 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/DeductionList.module.css` | TRACKED | CLEAN | .module.css | 2094 | c9a757936a45c560842a57a26eef3e738d39e7f8eeb93734870232715c8bd05b | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/DeductionList.tsx` | TRACKED | CLEAN | .tsx | 3342 | 20c79e6d4e9123cc1c92934b4cb6ace87d0dd4edb9ccdb133c9570469457432d | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/EditDeductionModal.module.css` | TRACKED | CLEAN | .module.css | 1221 | 7a9804c26b4a5df9d7f9b74cce41257a624fbb5b7e772e47cb2ec104c64f20ae | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/EditDeductionModal.tsx` | TRACKED | CLEAN | .tsx | 2205 | 9bbf47ef45b68041db5f7eb3994469161922894feb720d8ba2ce13501bb9bc76 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/PlayerPointSummary.module.css` | TRACKED | CLEAN | .module.css | 930 | ad57b203538362b46f7802963678da373fc9d8aac0cbe03e5f5731c5c4b9d33d | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/components/PlayerPointSummary.tsx` | TRACKED | CLEAN | .tsx | 1515 | 2ca167c9fdd54be52378c67f7d5c7529ce7175c06094975857f503d483bd6684 | pages | legacy dashboard/auth |
| `frontend/src/pages/AdminDashboard/views/PointView/hooks/usePointView.ts` | TRACKED | CLEAN | .ts | 3659 | e02d5b27c6fed7ddc4f5791e4f0ae18771ff7c832ab72228cc32971a1c3b94f7 | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/Auth.module.css` | TRACKED | CLEAN | .module.css | 14188 | f6ce8b570669f84391f0ede5d5f212f45918027cc2e2766542eb127369791581 | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/api/authApi.ts` | TRACKED | CLEAN | .ts | 1448 | ec6b1aab7e47264389b9eec43dd42392aa04e69e9693cec769d05cd17634f6fe | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/components/AdminLoginView.tsx` | TRACKED | CLEAN | .tsx | 3358 | f92726713fa0e48d5b61eccd988384499055ed213e6fae8dcee52291f0a25678 | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/components/PinInput.tsx` | TRACKED | CLEAN | .tsx | 2230 | 155e122f2836c2696410c65037152e59acb919d9b4407ff0cd95edee69771f2b | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/components/PinInputView.tsx` | TRACKED | CLEAN | .tsx | 3837 | 1f750f7eef6c9861ab2c223510016a5e37940e994d5d23e4ab7bbca0fd946479 | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/components/PlayerCard.tsx` | TRACKED | CLEAN | .tsx | 1455 | 04901ea0e69804688799cad4c9da9ea07a9581e2959d4173c760bd2297c5a725 | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/components/PlayerSelectView.tsx` | TRACKED | CLEAN | .tsx | 3988 | 51104b1335ed56fa21434898f019cc86c7d8bdfdf9613e675b36ebbeee6e06ca | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/constants.ts` | TRACKED | CLEAN | .ts | 188 | f0ee3f4a3ec2a29c0ba33240cd2657bc2bca13376004b0874fc8bc3ac38ae228 | pages | legacy dashboard/auth |
| `frontend/src/pages/Auth/index.tsx` | TRACKED | CLEAN | .tsx | 2325 | 0a458479fc16c6a03f8d065ab6a9fb43ed5f7c20a4b6f23c4c6d9155ca304e32 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/UserDashboard.module.css` | TRACKED | CLEAN | .module.css | 34701 | f040b51f41c75af870e2143c1d4e60cd072b2f9b1e5293caac13a21493a7692b | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/api/dashboardApi.ts` | TRACKED | CLEAN | .ts | 5232 | 5d12de04cf27872a480a1adda91b91e6b1762f891c38b276663be4d70900fbd6 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/BottomNav.tsx` | TRACKED | CLEAN | .tsx | 1579 | 328a98537b956a17bafa0a0f21b78bd2cf1cc848fbbdb4fbf2ac4438701963e0 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/CheerModal.tsx` | TRACKED | CLEAN | .tsx | 716 | 6043fe37a17b2084a4daf450a583c013fb410ce0116fefebfbec521d9b2fa777 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/ConfettiEffect.tsx` | TRACKED | CLEAN | .tsx | 1488 | 816175b2fb8f9da95c87a7a44091d05472d0eaa54ece256c90c9bda6b3fd3e06 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/DateSelector.tsx` | TRACKED | CLEAN | .tsx | 1270 | 0d27414b10a26368a18ed523ea1566c8e8893877b00ea6fff4de400069e81daf | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/DeductionAccordion.tsx` | TRACKED | CLEAN | .tsx | 1372 | 0b06b57e5fd40ee2ae2e8a69b797debcefb06711ce8912ef00f83215b2600f51 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/ExpBar.tsx` | TRACKED | CLEAN | .tsx | 1750 | acb03dc1aac8ec53df118c1bcf4abf2bc7d18d98d29e5ad14f017648129ca65b | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/FeedbackSection.tsx` | TRACKED | CLEAN | .tsx | 6505 | 1ec964c97c511e9a569ceb4d360283c2b87f4f0f5d15acad95911e0a4826f51f | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/MissionList.module.css` | TRACKED | CLEAN | .module.css | 3828 | 110cb484cf2ca3047bc2391cf322ae67f0253ce48467163349be7c0fc0dffd16 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/MissionList.tsx` | TRACKED | CLEAN | .tsx | 5506 | 274ab656098e037f4ec1bb66ad233f30d9bbefec4921892d7d6ae22e1a093be9 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/MissionProgressBar.module.css` | TRACKED | CLEAN | .module.css | 1831 | eaeb52408af300ac1a9de350a11c074b9702024cec15b184c0135daea1cd4f8d | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/MissionProgressBar.tsx` | TRACKED | CLEAN | .tsx | 2766 | b45f6b915b934a6dd50f2b4483ecb942f2f6c87f3bdabb902019040a18f40339 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/MissionProposal.tsx` | TRACKED | CLEAN | .tsx | 2838 | 4b973072d97350e3fd5d070dd75895b08db2168576f01b0e55f0f44206b8e4c8 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/ProfileCard.tsx` | TRACKED | CLEAN | .tsx | 5231 | bc79030bea8ab834d4b5cbb2e0d0c148b8bfc76b52622a0837e1689ce8a4ceaa | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/RankingView.tsx` | TRACKED | CLEAN | .tsx | 2604 | 01c932a2f60fda76d53ca8376d1778effe0e6df030c21502f7c8af5101fd4e4a | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/StatDetailModal.tsx` | TRACKED | CLEAN | .tsx | 3170 | becbd5ea4be9d71a7feebb031e47918b49ce608398ae063058db809a53f4f10f | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/StoryCards.tsx` | TRACKED | CLEAN | .tsx | 1308 | bd8c80737605fca74e2b69bf9c0e349e7d1da856e37b18ea0dc084b52de2d56e | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/WeeklyDateBar.module.css` | TRACKED | CLEAN | .module.css | 2456 | 27545a315629df4c9000ba80af97b7a9721cd8b349f34da70877c2f4dee8be9e | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/WeeklyDateBar.tsx` | TRACKED | CLEAN | .tsx | 2954 | 79e503fa9139a77fd36acccc2143e9513a04480b15736e8a40d90fdb856e9990 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/WeeklyMissionModal.module.css` | TRACKED | CLEAN | .module.css | 2214 | c4bb69ec198d1bc7b6df76e75f8c614eb03d316b05749e52d60d203656567109 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/components/WeeklyMissionModal.tsx` | TRACKED | CLEAN | .tsx | 4289 | 13474c9bfe9db867b240d41b786ea7898e00adb324f7220d397ad39466ffc604 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/hooks/useDashboard.ts` | TRACKED | CLEAN | .ts | 9759 | c5b7062533c7a9ccfeed005d56bb7f24cb5b9016113d428d4c109f3568a71585 | pages | legacy dashboard/auth |
| `frontend/src/pages/UserDashboard/index.tsx` | TRACKED | CLEAN | .tsx | 7533 | 438ef61046b8d69c75505f7d7799d72ac86ccc2217b72f479a33dc865084f5a7 | pages | legacy dashboard/auth |
| `frontend/src/platform/access/AccessBoundary.tsx` | TRACKED |  M | .tsx | 1563 | d063ce19c20f5d215193d83069d8813154165d05d4f9cacb0d942fb713e42235 | platform | family/profile/access |
| `frontend/src/platform/markpoint/MarkpointAdmin.module.css` | UNTRACKED | ?? | .module.css | 3907 | 5c75e507308fc49577c9777d1fddfd77698729d6dfd496a846477b22591db712 | platform | Markpoint |
| `frontend/src/platform/markpoint/MarkpointAdmin.tsx` | UNTRACKED | ?? | .tsx | 20746 | ade0c4975261d9eddb81c7719c046a12050aefb5801b6961a894da9ec4114baf | platform | Markpoint |
| `frontend/src/platform/markpoint/MarkpointUser.module.css` | UNTRACKED | ?? | .module.css | 5488 | 60c266a549fb632828862a76f0b04c8859a064295bccb6c150f9aba53c1c8152 | platform | Markpoint |
| `frontend/src/platform/markpoint/MarkpointUser.tsx` | UNTRACKED | ?? | .tsx | 12956 | f36f6fda732a4ad0cbaee32b89e5adff01a4249b5c73884acbe0b82be3b24133 | platform | Markpoint |
| `frontend/src/platform/pages/FamilyLanding.module.css` | UNTRACKED | ?? | .module.css | 3419 | d96eea56d4d374d4dc099821f427257a3eccc136cbd0eaf621163d5041e897a1 | platform | family/profile/access |
| `frontend/src/platform/pages/FamilyLanding.tsx` | TRACKED |  M | .tsx | 8411 | 5224fac684a6b24b0fec44497f48ca09ebb93d70527635fbf58a5a03ac5d97ef | platform | family/profile/access |
| `frontend/src/platform/pages/PlatformPages.module.css` | TRACKED | CLEAN | .module.css | 365 | 79aeaf1b324a01e165373034fe1b686088bf71720ca95bdd2f8201e14fe0316b | platform | application/composition |
| `frontend/src/platform/pages/WagleLanding.module.css` | TRACKED | CLEAN | .module.css | 4974 | b22206de78726bd99aaaedb1ef19764b8f27d454642b492df8a1f4d4b99f30a1 | platform | application/composition |
| `frontend/src/platform/pages/WagleLanding.tsx` | TRACKED |  M | .tsx | 1466 | 13ad10cc0fdb6e2f0ad71641327d05d1fcb1b06bc2f0bb6193b0bf3e3b26db39 | platform | application/composition |
| `frontend/src/platform/preview/PointFestivalPreview.module.css` | UNTRACKED | ?? | .module.css | 7851 | 6c27382e026c3dc12b46d3c36ee90ed7243540e42f892e51a00b2129cb55f748 | platform | preview implementation |
| `frontend/src/platform/preview/PointFestivalPreview.tsx` | UNTRACKED | ?? | .tsx | 5691 | 0cc1fd9cba5df91769ca33a17d5e4f27133426b912d50ac8dffb58ffb5219402 | platform | preview implementation |
| `frontend/src/platform/shell/MongleAppShell.module.css` | TRACKED | CLEAN | .module.css | 5011 | c082d59a6161c1ca6fdcb2aa6216fac5a8f383101f573a2f940890504c18918d | platform | family platform shell |
| `frontend/src/platform/shell/MongleAppShell.tsx` | TRACKED |  M | .tsx | 9277 | ff98653fa67b16872b8d3d3f506c8ba2c26294c15824212903d2b10b542ecbc5 | platform | family platform shell |
| `frontend/src/platform/wagle/WagleRoomView.module.css` | UNTRACKED | ?? | .module.css | 5110 | 29ce138216d7c934fc6332427ceff53ab42f2e88cb13120118cf3bcfa1ece6d0 | platform | Wagle |
| `frontend/src/platform/wagle/WagleRoomView.tsx` | UNTRACKED | ?? | .tsx | 12981 | a82f53e1fe4fbaac98a70fc2364fa3ea82330f9770928493330ec9c34480e6d1 | platform | Wagle |
| `frontend/src/platform/wagle/components/ChatComposer/ChatComposer.module.css` | TRACKED | CLEAN | .module.css | 2271 | 099c18a791741ac1bba140a2af5b30cc5d3b790f46368cb604c370be8b658a9a | platform | Wagle |
| `frontend/src/platform/wagle/components/ChatComposer/ChatComposer.tsx` | TRACKED | CLEAN | .tsx | 3117 | 20f404bc2eea8d3791c3b2f9dadbc54f51d7b83d071857e648a518c91322e1ec | platform | Wagle |
| `frontend/src/platform/wagle/components/ChatComposer/index.ts` | TRACKED | CLEAN | .ts | 115 | 4a571502a31d2f929813a738a7e5640ef69098dc77cb98713005af11641a3a1c | platform | Wagle |
| `frontend/src/platform/wagle/components/ChatHeader/ChatHeader.module.css` | TRACKED | CLEAN | .module.css | 2133 | 9bac64ad7f3e79702c6f105b021093cbfdcddf71cfa904ba467b7655dc02589c | platform | Wagle |
| `frontend/src/platform/wagle/components/ChatHeader/ChatHeader.tsx` | TRACKED | CLEAN | .tsx | 2118 | bc2f4e3a734a5b07c65ef203dec893ef5faa2e3543353354275b46816498bf5a | platform | Wagle |
| `frontend/src/platform/wagle/components/ChatHeader/index.ts` | TRACKED | CLEAN | .ts | 130 | 4c550d47a44bf125eadc06d663796ced2e2190acc7ee4a9afba1d82bac3a8449 | platform | Wagle |
| `frontend/src/platform/wagle/components/DateDivider/DateDivider.module.css` | TRACKED | CLEAN | .module.css | 277 | 981846240b6f36a12c3444b9bb34392ed7d56ad7a2d94f368147408076c0622b | platform | Wagle |
| `frontend/src/platform/wagle/components/DateDivider/DateDivider.tsx` | TRACKED | CLEAN | .tsx | 300 | a3d6177d3b70ea4a1bab5e26179405b79f53da80b066333f6d4d8e5194773e79 | platform | Wagle |
| `frontend/src/platform/wagle/components/DateDivider/index.ts` | TRACKED | CLEAN | .ts | 111 | f4bd8f5b1f79b7af4c4584090686a40c503e2e1311b89860dd172efb97f90bc4 | platform | Wagle |
| `frontend/src/platform/wagle/components/EmptyState/EmptyState.module.css` | TRACKED | CLEAN | .module.css | 706 | 0c2fdf849ce337c746e1ff06c73586b516879ab135f6f2d0cc6856f90f1ac7a5 | platform | Wagle |
| `frontend/src/platform/wagle/components/EmptyState/EmptyState.tsx` | TRACKED | CLEAN | .tsx | 673 | 962b5d6251d8f69a653a744e57302cb779d4fea64bf15200539e15f37ceb5fb8 | platform | Wagle |
| `frontend/src/platform/wagle/components/EmptyState/index.ts` | TRACKED | CLEAN | .ts | 107 | 19e6ecacb8f820453d0ae65efccfc52c6ff01eeb247efb2cf0167243b4be5a77 | platform | Wagle |
| `frontend/src/platform/wagle/components/ErrorState/ErrorState.module.css` | TRACKED | CLEAN | .module.css | 828 | 65ff69c0b2052e6bb3a2ff3759c6d01b0f16c4d386e235ee4dca911571e4ed43 | platform | Wagle |
| `frontend/src/platform/wagle/components/ErrorState/ErrorState.tsx` | TRACKED | CLEAN | .tsx | 955 | 164b359906bb806cdd73055cfb0dc95943f25a76ea5e7a35b3644e25ef01a8f2 | platform | Wagle |
| `frontend/src/platform/wagle/components/ErrorState/index.ts` | TRACKED | CLEAN | .ts | 107 | 8a94d3685bc30e146121853e0ada4a0f5f6a40d07e04a84677c61712211889f1 | platform | Wagle |
| `frontend/src/platform/wagle/components/LoadingState/LoadingState.module.css` | TRACKED | CLEAN | .module.css | 769 | f0cbc90431fa1b44fe62a0a3c5ce244e1ae23222ad6d7d0f394a39dea500a502 | platform | Wagle |
| `frontend/src/platform/wagle/components/LoadingState/LoadingState.tsx` | TRACKED | CLEAN | .tsx | 557 | d6d6869a64086acf7657fe9370a89a1de4ef90c7f89ba4d8c8bf40065c70ace5 | platform | Wagle |
| `frontend/src/platform/wagle/components/LoadingState/index.ts` | TRACKED | CLEAN | .ts | 115 | 0406caaccfb7050a04fc8f68266311560a3ddd748122c5c9b8a89a12a34fc323 | platform | Wagle |
| `frontend/src/platform/wagle/components/MessageBubble/MessageBubble.module.css` | TRACKED | CLEAN | .module.css | 1708 | a88a8b32cad2c13b989c722b3ea0af7d910abec7b948b1bb57f5602a893ff6fc | platform | Wagle |
| `frontend/src/platform/wagle/components/MessageBubble/MessageBubble.tsx` | TRACKED | CLEAN | .tsx | 2362 | b08ae0c12535964062f5d1e489b0011e1e1b2f86de5a27c42528cd5c991465c3 | platform | Wagle |
| `frontend/src/platform/wagle/components/MessageBubble/index.ts` | TRACKED | CLEAN | .ts | 203 | 0a01055b7a22bd7d80d2dc9dc5534c0370c084a5f85e4d9c449900e097907b60 | platform | Wagle |
| `frontend/src/platform/wagle/components/RoomItem/RoomItem.module.css` | TRACKED | CLEAN | .module.css | 2255 | f79f29197181bb26fedf35832831e4160e142a641f482768ec6dea7ec3cdee72 | platform | Wagle |
| `frontend/src/platform/wagle/components/RoomItem/RoomItem.tsx` | TRACKED | CLEAN | .tsx | 1926 | 0fbfce50a14e65cd0641c6c92baa29b7a43bae437092e5d7b0af770a3a3b6304 | platform | Wagle |
| `frontend/src/platform/wagle/components/RoomItem/index.ts` | TRACKED | CLEAN | .ts | 109 | 1c28406f7e0241c90c43226220a95f4ec1a1e358f3f320638fa6e1598bd08336 | platform | Wagle |
| `frontend/src/platform/wagle/components/ServiceActionCard/ServiceActionCard.module.css` | TRACKED | CLEAN | .module.css | 1277 | 38ae097acd42bae4c3a524ee04dd37ff41dd592e12bc89a2223de107405cce6c | platform | Wagle |
| `frontend/src/platform/wagle/components/ServiceActionCard/ServiceActionCard.tsx` | TRACKED | CLEAN | .tsx | 1520 | 35365d5da96cd90e5b2f4d50114dd7b1ad78a6b4de802b29f76b731c6f345b19 | platform | Wagle |
| `frontend/src/platform/wagle/components/ServiceActionCard/index.ts` | TRACKED | CLEAN | .ts | 135 | e51b1d6cfbc04b784c4c9e1cd93630e9b9860e73935257608eaad188b02b0c47 | platform | Wagle |
| `frontend/src/platform/wagle/components/UnreadDivider/UnreadDivider.module.css` | TRACKED | CLEAN | .module.css | 714 | b76d99f38a24518a03225056d9d28918543dddaa743c31d5c9f456669003e7b8 | platform | Wagle |
| `frontend/src/platform/wagle/components/UnreadDivider/UnreadDivider.tsx` | TRACKED | CLEAN | .tsx | 477 | ffb7381cc098baba59ce81a3fe718c493b5c84536b520992000d79cc183580f8 | platform | Wagle |
| `frontend/src/platform/wagle/components/UnreadDivider/index.ts` | TRACKED | CLEAN | .ts | 119 | 2317ff3dfd2986c3870af43e83905a32c6fe0ddfd8f3f9d659a3942bbff25f8d | platform | Wagle |
| `frontend/src/platform/wagle/components/WaglePinLock/WaglePinLock.module.css` | TRACKED | CLEAN | .module.css | 2165 | 67c953c6c3438638faca92027f5a6d67a51e5032f2cf7d2d1f67e700f7a4ac47 | platform | Wagle |
| `frontend/src/platform/wagle/components/WaglePinLock/WaglePinLock.tsx` | TRACKED | CLEAN | .tsx | 6172 | e5104ea762f16839735bf84280de6baca21afd91d27e6f432d070bd6729b1575 | platform | Wagle |
| `frontend/src/platform/wagle/components/WaglePinLock/index.ts` | TRACKED | CLEAN | .ts | 47 | d3fb212e3ff2e141dc24f493a04e3b345ecfdedba0fe50df059a3122b2199a07 | platform | Wagle |
| `frontend/src/platform/wagle/components/index.ts` | TRACKED | CLEAN | .ts | 348 | 00a3815dcc85f436087ac0ad2d8f277805afda9ea72d60e830ec393e9110c7e1 | platform | Wagle |
| `frontend/src/platform/wagle/preview/index.ts` | TRACKED | CLEAN | .ts | 498 | 3c1b331bb953ad7ca0c775a5c737d4d5b944f2f1bb3b4134490fe701ba1ae5e0 | platform | preview implementation |
| `frontend/src/platform/wagle/preview/messages.ts` | TRACKED | CLEAN | .ts | 1954 | c99a5f5259d273fc55c56ac96f67a55cdaabe0032905a32ae2a0eca444b8a31d | platform | preview implementation |
| `frontend/src/platform/wagle/preview/pageState.ts` | TRACKED | CLEAN | .ts | 1336 | 63b9586223aeee7315bd34c151cd295248f7d199be5a9347c30ebd5442132d83 | platform | preview implementation |
| `frontend/src/platform/wagle/preview/rooms.ts` | TRACKED | CLEAN | .ts | 1052 | 4af2a1ffc6f78fda70101bf662f06f4d711b6a9a532bd7d14c83de6720f29414 | platform | preview implementation |
| `frontend/src/platform/wagle/preview/serviceEvents.ts` | TRACKED | CLEAN | .ts | 435 | fa3295144860bc22ec550f321ae052313ea903a7eaac9b7d4abbfb4949f28ccb | platform | preview implementation |
| `frontend/src/platform/wagle/preview/types.ts` | TRACKED | CLEAN | .ts | 1066 | 95d78a666d333d3adb01c76ef7035e59065b1597f9dcb10d05dc28fb347e7b16 | platform | preview implementation |
| `frontend/src/platform/wagle/realtime/useWagleRealtime.ts` | TRACKED | CLEAN | .ts | 3555 | ebc064c93fa2b9ef7f7ce7b6237cd9e35f1380ae4c90cdbd70784c848d3f3f63 | platform | Wagle |
| `frontend/src/platform/wagle/realtime/wagleDeviceApi.ts` | TRACKED | CLEAN | .ts | 4777 | 785934229101ea098d4525c71c3ae0c8f09ff273cea8dc13cf7ce78703892dbe | platform | Wagle |
| `frontend/src/platform/wagle/realtime/wagleRealtimeClient.ts` | TRACKED | CLEAN | .ts | 11806 | 30e2e818fcba1eb07120375190b02537b5d75a108217f6ddd81bc52d73970865 | platform | Wagle |
| `frontend/src/shared/api/accountAuthApi.ts` | UNTRACKED | ?? | .ts | 2548 | 8521003c5e59e5d526e4444b6a7ea35862a01f5f7167f2d1b4de380efd7484c7 | shared | shared technical utility |
| `frontend/src/shared/api/familyApi.ts` | TRACKED | CLEAN | .ts | 790 | 4866cc6b96c2461b69ef28795da5d6af36762f16f80d2834d3dba66cbd72ed25 | shared | shared technical utility |
| `frontend/src/shared/api/httpClient.ts` | TRACKED | CLEAN | .ts | 2371 | e60d6f2af2838838663f02e4c688645b3a0c896482d064c1a92b9286e3c41a90 | shared | shared technical utility |
| `frontend/src/shared/api/markpointApi.ts` | UNTRACKED | ?? | .ts | 11232 | 71d16bb93a5cac2a0de5f8c7bab30686f3cbf6ffe48d14ea4ae507f112d4e4c9 | shared | shared technical utility |
| `frontend/src/shared/api/openapiBoundary.ts` | TRACKED | CLEAN | .ts | 699 | c0560f2e261a5313945e881d857bcf688f4313f8821ad557a5e82d7792a00ba7 | shared | shared technical utility |
| `frontend/src/shared/api/wagleApi.ts` | UNTRACKED | ?? | .ts | 4768 | 532d736e2048587f056cf3191829cfc00f1c83036dd7cb0f530f95b74c09b5be | shared | shared technical utility |
| `frontend/src/shared/components/AppIcon/index.tsx` | TRACKED | CLEAN | .tsx | 1658 | a340f5ec7704bb8d2c438bac805c39a3263fee6f41c7b9f7be0d4cafefefa255 | shared | shared UI |
| `frontend/src/shared/components/Avatar/Avatar.module.css` | TRACKED | CLEAN | .module.css | 1470 | fc7e21f7721e9dc7662635f871f4c3415458330296a30d3f88f9aa1cb95feb09 | shared | shared UI |
| `frontend/src/shared/components/Avatar/Avatar.tsx` | TRACKED | CLEAN | .tsx | 2178 | 59c097046ace88ba9ad30abbced891ed9f2978b7f28655d357b06247d5ed1757 | shared | shared UI |
| `frontend/src/shared/components/Avatar/index.ts` | TRACKED | CLEAN | .ts | 117 | d29ddf5dc7de700cf2118a655b1ef05e653b800c6b74fdd2525536b68cd57958 | shared | shared UI |
| `frontend/src/shared/components/Button/Button.module.css` | TRACKED | CLEAN | .module.css | 2117 | 2baee9fa59d66ffa627c0ba2bb4d208830c0ca0ad27728d070667d0363d8793f | shared | shared UI |
| `frontend/src/shared/components/Button/Button.tsx` | TRACKED | CLEAN | .tsx | 686 | 09b7733278d25e7a27e93f3c0062d70f4f387b7c03897af9b1bfefc5a38d64b1 | shared | shared UI |
| `frontend/src/shared/components/Button/index.ts` | TRACKED | CLEAN | .ts | 46 | 3b2a57516bf5d15dc8a826312a2d28b6823f599f2688c3b01bb16759f330de07 | shared | shared UI |
| `frontend/src/shared/components/Card/Card.module.css` | TRACKED | CLEAN | .module.css | 992 | 98d66b0ee8036ae816017ba014323589140bbeda4ef65b801adec002465f4976 | shared | shared UI |
| `frontend/src/shared/components/Card/Card.tsx` | TRACKED | CLEAN | .tsx | 1211 | e581c5a484de81bef015dea253795522297b03655210d98e22ed5b1a22bd75e6 | shared | shared UI |
| `frontend/src/shared/components/Card/index.ts` | TRACKED | CLEAN | .ts | 127 | 54e7be4056a4593f98f522fcb8bf42874f31c294840fdba68740c332d18042b2 | shared | shared UI |
| `frontend/src/shared/components/ChatModal/ChatModal.module.css` | TRACKED | CLEAN | .module.css | 6941 | c208251ff84f52165fceac033d2ca5db8fd14ad62690c143974578dbf115f948 | shared | shared UI |
| `frontend/src/shared/components/ChatModal/ChatModal.tsx` | TRACKED | CLEAN | .tsx | 8743 | 07f4ac3a0825330f0364ef946ca065fd3aaee802e0eee80f2e7388db6bb0aca8 | shared | shared UI |
| `frontend/src/shared/components/ChatModal/index.ts` | TRACKED | CLEAN | .ts | 39 | 38179ba7e254cddfc9cc676dfc271b4ebb11e2edce0a4c59babbf3b8989d223a | shared | shared UI |
| `frontend/src/shared/components/IconButton/IconButton.module.css` | TRACKED | CLEAN | .module.css | 1198 | 9320d7d87398ebcb3f1646beda1ffe4f9fe1bc26b3f2972080621ddb6d763d3c | shared | shared UI |
| `frontend/src/shared/components/IconButton/IconButton.tsx` | TRACKED | CLEAN | .tsx | 1225 | 92f9f885b9ada3dd35303bca40b2a2c3a05a99ed9374efb1c253b6e0eb1a20b2 | shared | shared UI |
| `frontend/src/shared/components/IconButton/index.ts` | TRACKED | CLEAN | .ts | 123 | 937cc69f8ec2d4255afbb00aa1f3ed733d7b310f4195347c06e4808149b1c97b | shared | shared UI |
| `frontend/src/shared/components/MainLogo/MainLogo.module.css` | TRACKED | CLEAN | .module.css | 764 | ab30bd4317f7d1e84f853656f1b71008979f8529fa5994cea704518514c9bbf9 | shared | shared UI |
| `frontend/src/shared/components/MainLogo/MainLogo.tsx` | TRACKED | CLEAN | .tsx | 511 | 45a2f377173902c2613603313be9fae95875fe7b012163b723eda54a95ccb681 | shared | shared UI |
| `frontend/src/shared/components/MainLogo/index.ts` | TRACKED | CLEAN | .ts | 38 | 75a0c806ea118487d3a3fcf63d6b32ee672037fc41f32b0e6649a59a868cc298 | shared | shared UI |
| `frontend/src/shared/components/PhotoUpload/PhotoUpload.module.css` | TRACKED | CLEAN | .module.css | 849 | daa9ab9411a7c885a6cd4c8e4962921305b0fdaf5f7dd5d08ca0527080511333 | shared | shared UI |
| `frontend/src/shared/components/PhotoUpload/PhotoUpload.tsx` | TRACKED | CLEAN | .tsx | 1373 | 136595603617d7f2d1aafe954837b9d0145a5d0d92e8a1d09d7ba4628bcbbe4b | shared | shared UI |
| `frontend/src/shared/components/Toast/Toast.module.css` | TRACKED | CLEAN | .module.css | 683 | 4a6baa21ff68e55e8d861862a3a269191097bc5b17d1bdb9acf3077d887cd80b | shared | shared UI |
| `frontend/src/shared/components/Toast/Toast.tsx` | TRACKED | CLEAN | .tsx | 887 | 9fc5d4be3996a1795f8a572ec2df1585cdcff1be51acf7cc145d754e30321b20 | shared | shared UI |
| `frontend/src/shared/components/Toast/ToastContainer.module.css` | TRACKED | CLEAN | .module.css | 1038 | 665bfc1fe7faa16183699651a52e250ed0c3087ad3129227321be83b7291fcb4 | shared | shared UI |
| `frontend/src/shared/components/Toast/ToastContainer.tsx` | TRACKED | CLEAN | .tsx | 855 | 1529fd61cae6db2c7ab31fc2383cdab4141a5adcd1153689de477e2a3e619616 | shared | shared UI |
| `frontend/src/shared/components/Toast/index.ts` | TRACKED | CLEAN | .ts | 44 | 7060276651b924f32471c6d90747599a5b6b8cf756a9d3c7247d82c4f9fec302 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/AttachIcon.tsx` | TRACKED | CLEAN | .tsx | 332 | 45384de61b4db4f566cf3e888d208994a80212b9fdfa5dc7d5150c226878e524 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/BackIcon.tsx` | TRACKED | CLEAN | .tsx | 239 | 391fbfa05da83af8d1b9ab844a71d350117894226c1a4d23bbb1323eadde53d3 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/BellIcon.tsx` | TRACKED | CLEAN | .tsx | 322 | 043f9819dbd77bd9ad66edf28a6f5eeac08101bd1e081bf52ba2e78906adaf1c | shared | shared UI |
| `frontend/src/shared/components/icons/outline/CameraIcon.tsx` | TRACKED | CLEAN | .tsx | 379 | 4a68893911ac2bcc0e8c61877b32145a39fea4d2e147d955ed5dd60c61f8d992 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/DeleteIcon.tsx` | TRACKED | CLEAN | .tsx | 412 | d909a20842ec98586d51808e0361b63e5c71f625fb74b765c80a934337cb26a3 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/EditIcon.tsx` | TRACKED | CLEAN | .tsx | 290 | d018b04be80bcb27088792b4b68164b419a2e6fcce72467cf6a469294535634c | shared | shared UI |
| `frontend/src/shared/components/icons/outline/HomeIcon.tsx` | TRACKED | CLEAN | .tsx | 312 | 1ffd60a87c26d833028da76e17dcddef2bc93c572bb46438e85c534dbd698101 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/IconBase.tsx` | TRACKED | CLEAN | .tsx | 682 | df4506ac50ed56712deb340acf919b821517e007fee1ff8baee084bb128ea2be | shared | shared UI |
| `frontend/src/shared/components/icons/outline/SendIcon.tsx` | TRACKED | CLEAN | .tsx | 250 | 0da52bed7267323a312d13d015c29e8729e835048bbcda3b83377074770a978b | shared | shared UI |
| `frontend/src/shared/components/icons/outline/SettingsIcon.tsx` | TRACKED | CLEAN | .tsx | 459 | e8f862f15136e50aabde37054a4184d526c03e20f2576e0abd73baab88df4f5b | shared | shared UI |
| `frontend/src/shared/components/icons/outline/index.ts` | TRACKED | CLEAN | .ts | 519 | 9db4847987fe922e69936e4dc2f5dc5129ab8f2d636c6c13c7e5b65dc2d72f43 | shared | shared UI |
| `frontend/src/shared/components/icons/outline/types.ts` | TRACKED | CLEAN | .ts | 488 | e35833ee75070b788627196db25d7e96d05b4da698e453e90acd0e1863738d54 | shared | shared UI |
| `frontend/src/shared/family/FamilyContextLoader.tsx` | TRACKED | CLEAN | .tsx | 569 | c2060340797ef241c5c212068dfd75c88cb980e18a3c78e5a29c2ed8335f5380 | shared | shared technical utility |
| `frontend/src/shared/storage/activeFamilyStorageMigration.ts` | TRACKED | CLEAN | .ts | 3884 | f3be9d2e102bebf53c0dbefc380fa592d7480f350dd24d35f26832cf42296695 | shared | shared technical utility |
| `frontend/src/shared/stores/useAuthStore.ts` | TRACKED |  M | .ts | 3955 | 17d82fe82a34e73be2b08398dd22909cd26debd57cd714265db8783b17cda21c | shared | shared technical utility |
| `frontend/src/shared/stores/useFamilyContextStore.ts` | TRACKED | CLEAN | .ts | 4447 | e6726307879574af8f5f4b62e86b7e240cf5502868db461e5e2dc2598f191eb5 | shared | shared technical utility |
| `frontend/src/shared/stores/useToastStore.ts` | TRACKED | CLEAN | .ts | 1116 | 9ac471d2beee4ea4f731ee984c0424fa8a827816a8ff51dcf0e0a52c90cc9df3 | shared | shared technical utility |
| `frontend/src/shared/tokens/tokenContract.test.mjs` | TRACKED | CLEAN | .mjs | 8740 | ce00763418b30818a609732f84121d52a0a057d0c84db8dad7732fb6982e5945 | shared | shared technical utility |
| `frontend/src/shared/utils/compressImage.ts` | TRACKED | CLEAN | .ts | 913 | 1941a4bc1d16d25ac33f0f5da2fa6c2a8cbf080a0ef7a80047f034332a557dc8 | shared | shared technical utility |
| `frontend/src/shared/utils/dateUtils.ts` | TRACKED | CLEAN | .ts | 2566 | c1c760359c9171daaa9a6cfbd8f4c0c02c86307a0dce6ea95873c4b1635ef4cb | shared | shared technical utility |
| `frontend/src/shared/utils/favicon.ts` | TRACKED | CLEAN | .ts | 1137 | ad080a5626f365087640455a207ad07488cec04fe6433d0bd8c332126e48e499 | shared | shared technical utility |
| `frontend/src/styles/global.css` | TRACKED |  M | .css | 7016 | 42f70dfa37affd5d9f98b7c85963c55a1f80422e44e78494f795823e5d7394b4 | styles | application/composition |
| `frontend/src/styles/reset.css` | TRACKED | CLEAN | .css | 215 | 6fb0a0a0e416287f9613d4a716a672da5bb2ec03bd077a86e684c5fc027db804 | styles | application/composition |
| `frontend/src/vite-env.d.ts` | TRACKED | CLEAN | .ts | 38 | 65996936fbb042915f7b74a200fcdde7e410f32a669b1ab9597cfaa4b0faddb5 | vite-env.d.ts | application/composition |
| `frontend/tsconfig.app.json` | TRACKED | CLEAN | .json | 622 | 7c97e3731424bf98ac60aec58c4d439b117748cb21bd67d7887980a58e94790e | tsconfig.app.json | application/composition |
| `frontend/tsconfig.json` | TRACKED | CLEAN | .json | 119 | 770b4140bbb581e2dfd9ea9946ffc9c75a1d86ba7d2db5f77c83e37cbdf9d808 | tsconfig.json | application/composition |
| `frontend/tsconfig.node.json` | TRACKED | CLEAN | .json | 550 | d1dca3f992b2a8aee9f885dde1e8c4ba2750b4a84cbb506d9dc6d261b0038c3f | tsconfig.node.json | application/composition |
| `frontend/vite.config.ts` | TRACKED | CLEAN | .ts | 380 | 848d543280f81fa1627dd24d76ba6b458bdd98d34888f5523ffca7fa955ef8a5 | vite.config.ts | application/composition |

## Protection Accounting

- FRONTEND_SOURCE_CHANGE_COUNT: 0
- FRONTEND_DIRECTORY_CREATE_COUNT: 0
- ROUTE_CHANGE_COUNT: 0
- IMPORT_CHANGE_COUNT: 0
- PACKAGE_CHANGE_COUNT: 0
- RELAY_CHANGE_COUNT: 0
- 1C_SESSION_CHANGE_COUNT: 0

## Document SHA-256

| document | SHA-256 at closing verification | note |
| --- | --- | --- |
| MONGLE_FRONTEND_STRUCTURE_MEASUREMENT.md | `c9586c825b033594c093fe1892b153b02f5f6a0a9f2879bf82bee79649ea3d4e` | final content at the verification point |
| MONGLE_FRONTEND_ROUTE_IMPORT_MATRIX.md | `b1ac96651318e8b168a338a1d2369cfa02d15e6dcbfc05df58fa2e0606fd4a68` | final content at the verification point |
| MONGLE_FRONTEND_STRUCTURE_MEASUREMENT_MANIFEST.md | externally reported at final verification | embedding its own final hash would change the file |
