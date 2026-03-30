/**
 * 마인크래프트 포인트 잔치 - 자체 호스팅 API 서버
 * Firebase Realtime Database를 SQLite + Socket.io로 대체
 *
 * 데이터 모델:
 *   SQLite collections 테이블에 Firebase 최상위 컬렉션을 JSON으로 저장
 *   예) mc_players, mc_mission_data, mc_cheer_msgs, ...
 *
 * API:
 *   GET  /api/data?path=mc_players/first     → 해당 경로 값 반환
 *   POST /api/set    { path, data }           → 값 덮어쓰기 (Firebase set)
 *   PATCH /api/update { path, data }          → 얕은 병합 (Firebase update)
 *   POST /api/push   { path, data }           → 자동키 추가 (Firebase push)
 *   DELETE /api/remove { path }               → 삭제 (Firebase remove)
 *
 * 실시간:
 *   데이터 변경 시 Socket.io로 'data_update' 이벤트 브로드캐스트
 */

const express = require('express');
const http    = require('http');
const { Server } = require('socket.io');
const Database = require('better-sqlite3');
const path    = require('path');
const { v4: uuidv4 } = require('uuid');

// ─── 초기화 ───────────────────────────────────────────────────────────────
const app    = express();
const server = http.createServer(app);
const io     = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

const DB_PATH = path.join(__dirname, 'data', 'app.db');
const db = new Database(DB_PATH);

// WAL 모드: 동시 읽기 성능 향상
db.pragma('journal_mode = WAL');

// 컬렉션 테이블 생성
db.exec(`
  CREATE TABLE IF NOT EXISTS collections (
    name       TEXT PRIMARY KEY,
    data       TEXT NOT NULL DEFAULT '{}',
    updated_at INTEGER DEFAULT (unixepoch())
  )
`);

app.use(express.json({ limit: '50mb' }));

// ─── 경로 파싱 유틸 ───────────────────────────────────────────────────────

/**
 * 전체 경로를 컬렉션명과 하위 키 경로로 분리
 * 'mc_players/first/name' → { collection: 'mc_players', keyPath: 'first/name' }
 */
function parsePath(fullPath) {
  const parts = (fullPath || '').replace(/^\/+|\/+$/g, '').split('/').filter(Boolean);
  const collection = parts[0] || '';
  const keyPath    = parts.slice(1).join('/');
  return { collection, keyPath };
}

/**
 * SQLite에서 컬렉션 전체 JSON 읽기
 */
function readCollection(collection) {
  const row = db.prepare('SELECT data FROM collections WHERE name = ?').get(collection);
  return row ? JSON.parse(row.data) : null;
}

/**
 * 중첩 객체에서 keyPath 경로의 값을 가져옴
 * keyPath = 'first/2025-01-01/missions'
 */
function getNestedValue(obj, keyPath) {
  if (!keyPath) return obj;
  const keys = keyPath.split('/').filter(Boolean);
  let current = obj;
  for (const key of keys) {
    if (current == null || typeof current !== 'object') return null;
    current = current[key];
  }
  return current ?? null;
}

/**
 * 중첩 객체에서 keyPath 경로에 값을 설정/삭제
 * value === null이면 해당 키 삭제
 */
function setNestedValue(obj, keyPath, value) {
  if (!keyPath) return value;  // 루트 교체
  const keys = keyPath.split('/').filter(Boolean);
  const result = obj && typeof obj === 'object' ? { ...obj } : {};
  let current = result;
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    current[key] = (current[key] && typeof current[key] === 'object')
      ? { ...current[key] }
      : {};
    current = current[key];
  }
  const lastKey = keys[keys.length - 1];
  if (value === null) {
    delete current[lastKey];
  } else {
    current[lastKey] = value;
  }
  return result;
}

/**
 * 컬렉션 전체를 SQLite에 저장
 */
function writeCollection(collection, data) {
  db.prepare(`
    INSERT INTO collections (name, data, updated_at)
    VALUES (?, ?, unixepoch())
    ON CONFLICT(name) DO UPDATE SET
      data       = excluded.data,
      updated_at = excluded.updated_at
  `).run(collection, JSON.stringify(data));
}

/**
 * 변경 후 Socket.io로 브로드캐스트
 * 연결된 모든 클라이언트에게 'data_update' 이벤트 전송
 */
function broadcastUpdate(fullPath, value) {
  io.emit('data_update', { path: fullPath, value });
  console.log(`[broadcast] ${fullPath}`);
}

// ─── REST API ─────────────────────────────────────────────────────────────

/**
 * GET /api/data?path=mc_players/first
 * Firebase: get(ref(db, 'mc_players/first'))
 */
app.get('/api/data', (req, res) => {
  const fullPath = req.query.path || '';
  const { collection, keyPath } = parsePath(fullPath);
  if (!collection) return res.json(null);

  const collData = readCollection(collection);
  const value = getNestedValue(collData, keyPath);
  res.json(value);
});

/**
 * POST /api/set
 * Body: { path: 'mc_players/first', data: { ... } }
 * Firebase: set(ref(db, 'mc_players/first'), data)
 */
app.post('/api/set', (req, res) => {
  const { path: fullPath, data } = req.body;
  const { collection, keyPath } = parsePath(fullPath);
  if (!collection) return res.status(400).json({ error: 'path required' });

  const collData = readCollection(collection) || {};
  const updated  = setNestedValue(collData, keyPath, data);
  writeCollection(collection, updated);
  broadcastUpdate(fullPath, data);
  res.json({ ok: true });
});

/**
 * PATCH /api/update
 * Body: { path: 'mc_players/first', data: { name: '새이름' } }
 * Firebase: update(ref(db, 'mc_players/first'), data)  ← 얕은 병합
 */
app.patch('/api/update', (req, res) => {
  const { path: fullPath, data } = req.body;
  const { collection, keyPath } = parsePath(fullPath);
  if (!collection) return res.status(400).json({ error: 'path required' });

  const collData = readCollection(collection) || {};
  const existing = getNestedValue(collData, keyPath);
  const merged   = (existing && typeof existing === 'object')
    ? { ...existing, ...data }
    : data;
  const updated = setNestedValue(collData, keyPath, merged);
  writeCollection(collection, updated);
  broadcastUpdate(fullPath, merged);
  res.json({ ok: true });
});

/**
 * POST /api/push
 * Body: { path: 'mc_notifications', data: { ... } }
 * Firebase: push(ref(db, 'mc_notifications'), data)  ← 자동키 생성
 * 반환: { key: '-abc123...' }
 */
app.post('/api/push', (req, res) => {
  const { path: fullPath, data } = req.body;
  const { collection, keyPath } = parsePath(fullPath);
  if (!collection) return res.status(400).json({ error: 'path required' });

  // Firebase 스타일 push key: '-' + 19자리
  const newKey     = '-' + uuidv4().replace(/-/g, '').substring(0, 19);
  const newKeyPath = keyPath ? `${keyPath}/${newKey}` : newKey;

  const collData = readCollection(collection) || {};
  const updated  = setNestedValue(collData, newKeyPath, data);
  writeCollection(collection, updated);

  // push된 부모 경로 전체를 브로드캐스트
  const parentValue = getNestedValue(updated, keyPath);
  broadcastUpdate(fullPath, parentValue);

  res.json({ key: newKey });
});

/**
 * DELETE /api/remove
 * Body: { path: 'mc_notifications/-abc123' }
 * Firebase: remove(ref(db, 'mc_notifications/-abc123'))
 */
app.delete('/api/remove', (req, res) => {
  const { path: fullPath } = req.body;
  const { collection, keyPath } = parsePath(fullPath);
  if (!collection) return res.status(400).json({ error: 'path required' });

  const collData = readCollection(collection) || {};
  const updated  = setNestedValue(collData, keyPath, null);
  writeCollection(collection, updated);
  broadcastUpdate(fullPath, null);
  res.json({ ok: true });
});

// ─── Socket.io ────────────────────────────────────────────────────────────

io.on('connection', (socket) => {
  const ip = socket.handshake.address;
  console.log(`[socket] connected: ${socket.id} (${ip})`);

  socket.on('disconnect', () => {
    console.log(`[socket] disconnected: ${socket.id}`);
  });
});

// ─── 서버 시작 ────────────────────────────────────────────────────────────

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`✅ MC Points API server running on port ${PORT}`);
  console.log(`📁 DB path: ${DB_PATH}`);
});

// 종료 시 DB 연결 닫기
process.on('SIGTERM', () => { db.close(); process.exit(0); });
process.on('SIGINT',  () => { db.close(); process.exit(0); });
