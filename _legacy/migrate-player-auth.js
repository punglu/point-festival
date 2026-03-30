/**
 * mc_players → mc_player_auth 데이터 분리 마이그레이션 스크립트
 * ─────────────────────────────────────────────────────────────────────────
 *
 * 배경:
 *   보안 강화로 아이들의 PIN, loginAttempts, lockUntil을
 *   mc_players(공개) → mc_player_auth(분리)로 이동합니다.
 *
 * 실행 방법:
 *   1. 이 파일을 프로젝트 루트에 두고 실행합니다.
 *   2. npm install firebase-admin  (처음 한 번만)
 *   3. Firebase Console → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성
 *      → serviceAccountKey.json 으로 저장 (이 스크립트와 같은 폴더)
 *   4. node migrate-player-auth.js
 *
 * 주의:
 *   - 실행 전 Firebase 콘솔에서 데이터를 백업해두세요!
 *   - mc_player_auth가 이미 존재하면 덮어쓰지 않고 스킵합니다.
 *   - 마이그레이션 후 mc_players의 pin/loginAttempts/lockUntil 은
 *     직접 삭제하지 않아도 됩니다 (규칙으로 쓰기만 막힘).
 *     원하면 Firebase Console에서 수동으로 필드를 삭제하세요.
 */

const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  // 운영: https://mark-point-festivals-default-rtdb.firebaseio.com
  // 개발: https://mark-point-festivals-dev-default-rtdb.asia-southeast1.firebasedatabase.app
  databaseURL: 'https://mark-point-festivals-dev-default-rtdb.asia-southeast1.firebasedatabase.app'
});

const db = admin.database();

async function migrate() {
  console.log('\n🔄 mc_players → mc_player_auth 마이그레이션 시작\n');

  // 1. mc_players 전체 읽기
  const playersSnap = await db.ref('mc_players').once('value');
  const players = playersSnap.val();

  if (!players) {
    console.log('❌ mc_players 데이터가 없습니다.');
    process.exit(1);
  }

  // 2. mc_player_auth 기존 데이터 확인
  const authSnap = await db.ref('mc_player_auth').once('value');
  const existingAuth = authSnap.val() || {};

  const results = { migrated: 0, skipped: 0, cleaned: 0 };

  for (const [pId, player] of Object.entries(players)) {
    const name = player.name || pId;

    // 이미 mc_player_auth에 데이터가 있으면 스킵
    if (existingAuth[pId]) {
      console.log(`  ⏭️  ${name} (${pId}) — 이미 mc_player_auth 존재, 스킵`);
      results.skipped++;
      continue;
    }

    // mc_player_auth에 분리할 필드 쓰기
    const authData = {
      pin:           player.pin           ?? '',
      loginAttempts: player.loginAttempts ?? 0,
      lockUntil:     player.lockUntil     ?? null
    };

    await db.ref(`mc_player_auth/${pId}`).set(authData);
    console.log(`  ✅  ${name} (${pId}) — 마이그레이션 완료`);
    console.log(`       pin: ${authData.pin ? '설정됨' : '미설정'}, loginAttempts: ${authData.loginAttempts}`);
    results.migrated++;

    // mc_players에서 민감 필드 제거
    await db.ref(`mc_players/${pId}/pin`).remove();
    await db.ref(`mc_players/${pId}/loginAttempts`).remove();
    await db.ref(`mc_players/${pId}/lockUntil`).remove();
    results.cleaned++;
  }

  console.log(`\n📊 결과:`);
  console.log(`   마이그레이션 완료: ${results.migrated}명`);
  console.log(`   스킵 (이미 존재): ${results.skipped}명`);
  console.log(`   mc_players 정리:  ${results.cleaned}명`);
  console.log(`\n✅ 완료! 이제 Firebase Console에서 보안 규칙을 업데이트하세요.\n`);

  process.exit(0);
}

migrate().catch(err => {
  console.error('❌ 오류:', err.message);
  process.exit(1);
});
