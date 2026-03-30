#!/usr/bin/env node
/**
 * Firebase Realtime Database 내보내기 JSON → SQLite 마이그레이션
 *
 * 사용법:
 *   node scripts/import-db.js [firebase-export.json 경로]
 *
 * 기본값:
 *   - 입력: ./db_backup/mark-point-festivals-default-rtdb-export.json
 *   - 출력: ./data/app.db
 *
 * 예시:
 *   node scripts/import-db.js
 *   node scripts/import-db.js ./db_backup/my-export.json
 */

const Database = require('better-sqlite3');
const fs       = require('fs');
const path     = require('path');

// ── 경로 설정 ────────────────────────────────────────────────────────────
const EXPORT_PATH = process.argv[2]
  || path.join(__dirname, '..', 'db_backup', 'mark-point-festivals-default-rtdb-export.json');

const DB_PATH = path.join(__dirname, '..', 'data', 'app.db');

// ── 검증 ─────────────────────────────────────────────────────────────────
if (!fs.existsSync(EXPORT_PATH)) {
  console.error(`❌ Firebase 내보내기 파일을 찾을 수 없음: ${EXPORT_PATH}`);
  console.error('   사용법: node scripts/import-db.js [json파일경로]');
  process.exit(1);
}

// data 디렉토리 생성
const dataDir = path.dirname(DB_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
  console.log(`📁 데이터 디렉토리 생성: ${dataDir}`);
}

// ── 기존 DB 백업 ──────────────────────────────────────────────────────────
if (fs.existsSync(DB_PATH)) {
  const backupPath = DB_PATH + '.bak.' + Date.now();
  fs.copyFileSync(DB_PATH, backupPath);
  console.log(`💾 기존 DB 백업: ${backupPath}`);
}

// ── SQLite 초기화 ─────────────────────────────────────────────────────────
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS collections (
    name       TEXT PRIMARY KEY,
    data       TEXT NOT NULL DEFAULT '{}',
    updated_at INTEGER DEFAULT (unixepoch())
  )
`);

// ── Firebase JSON 읽기 ────────────────────────────────────────────────────
console.log(`\n📂 Firebase 내보내기 파일 읽는 중...`);
console.log(`   경로: ${EXPORT_PATH}`);

const raw = fs.readFileSync(EXPORT_PATH, 'utf8');
let firebaseData;

try {
  firebaseData = JSON.parse(raw);
} catch (e) {
  console.error('❌ JSON 파싱 실패:', e.message);
  process.exit(1);
}

// ── 데이터 삽입 ───────────────────────────────────────────────────────────
const stmt = db.prepare(`
  INSERT INTO collections (name, data, updated_at)
  VALUES (?, ?, unixepoch())
  ON CONFLICT(name) DO UPDATE SET
    data       = excluded.data,
    updated_at = excluded.updated_at
`);

const insertAll = db.transaction((data) => {
  let count = 0;
  for (const [collectionName, collectionData] of Object.entries(data)) {
    if (collectionData === null || collectionData === undefined) continue;

    const json = JSON.stringify(collectionData);
    const sizeKB = (Buffer.byteLength(json) / 1024).toFixed(1);

    stmt.run(collectionName, json);
    count++;

    // 데이터 크기 표시 (base64 이미지 등 대용량 경고)
    const sizeStr = parseFloat(sizeKB) > 500
      ? `⚠️  ${sizeKB} KB (대용량)`
      : `${sizeKB} KB`;

    console.log(`   ✅ ${collectionName.padEnd(30)} ${sizeStr}`);
  }
  return count;
});

console.log('\n📥 컬렉션 가져오는 중:\n');
const count = insertAll(firebaseData);

// ── 검증 ─────────────────────────────────────────────────────────────────
const savedCollections = db.prepare('SELECT name, length(data) as size FROM collections ORDER BY name').all();

console.log(`\n✅ 마이그레이션 완료!`);
console.log(`   총 ${count}개 컬렉션 가져옴`);
console.log(`   DB 파일: ${DB_PATH}`);

const dbSizeKB = (fs.statSync(DB_PATH).size / 1024).toFixed(0);
console.log(`   DB 크기: ${dbSizeKB} KB`);

console.log('\n📋 저장된 컬렉션:');
savedCollections.forEach(row => {
  const kb = (row.size / 1024).toFixed(1);
  console.log(`   - ${row.name.padEnd(30)} ${kb} KB`);
});

db.close();
console.log('\n🚀 이제 docker-compose up --build 로 서버를 시작하세요!\n');
