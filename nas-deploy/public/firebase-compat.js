/**
 * firebase-compat.js
 * ─────────────────────────────────────────────────────────────────────────
 * Firebase Realtime Database SDK의 완전한 드롭인 대체 라이브러리
 *
 * 기존 코드의 아래 두 줄을 한 줄로 교체하는 것만으로 마이그레이션 완료:
 *
 *   [변경 전]
 *   import { initializeApp } from "https://...firebase-app.js";
 *   import { getDatabase, ref, onValue, push, update, get, set, remove }
 *     from "https://...firebase-database.js";
 *
 *   [변경 후]
 *   import { initializeApp, getDatabase, ref, onValue, push, update, get, set, remove }
 *     from '/firebase-compat.js';
 *
 * 나머지 코드(initializeApp, getDatabase, ref, onValue 등)는 전혀 수정 불필요.
 * ─────────────────────────────────────────────────────────────────────────
 */

// ── Socket.io 클라이언트 동적 로드 ────────────────────────────────────────
let _socket = null;

/** Socket.io 연결을 초기화하고 캐싱 */
async function _initSocket() {
  if (_socket) return _socket;

  // Socket.io 클라이언트 스크립트가 없으면 동적으로 로드
  if (typeof window.io === 'undefined') {
    await new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = '/socket.io/socket.io.js';
      s.onload = resolve;
      s.onerror = () => reject(new Error('Socket.io 클라이언트 로드 실패'));
      document.head.appendChild(s);
    });
  }

  _socket = window.io({ transports: ['websocket', 'polling'] });

  _socket.on('connect', () => {
    console.log('[firebase-compat] Socket.io 연결됨:', _socket.id);
  });

  _socket.on('disconnect', () => {
    console.log('[firebase-compat] Socket.io 연결 끊김');
  });

  // 서버에서 데이터 변경 시 수신 → 해당 경로의 리스너들에게 전달
  _socket.on('data_update', ({ path: updatedPath, value }) => {
    const normUpdated = _normPath(updatedPath);

    for (const [listenPath, callbacks] of _listeners.entries()) {
      const normListen = _normPath(listenPath);

      // 변경된 경로가 구독 경로의 상위이거나 같거나 하위일 때 콜백 실행
      if (normUpdated === normListen ||
          normListen.startsWith(normUpdated + '/') ||
          normUpdated.startsWith(normListen + '/')) {

        // 최신 데이터를 서버에서 재조회해서 콜백 실행
        _fetchPath(listenPath).then(val => {
          callbacks.forEach(cb => cb(_createSnapshot(val)));
        }).catch(console.error);
      }
    }
  });

  return _socket;
}

// ── 구독 리스너 저장소 ────────────────────────────────────────────────────
// Map<경로 문자열, Set<콜백함수>>
const _listeners = new Map();

// ── 유틸 함수 ─────────────────────────────────────────────────────────────

/** 경로 앞뒤 슬래시 정규화 */
function _normPath(p) {
  return (p || '').replace(/^\/+|\/+$/g, '');
}

/** 서버에서 경로 데이터 조회 */
async function _fetchPath(fullPath) {
  const res = await fetch(`/api/data?path=${encodeURIComponent(_normPath(fullPath))}`);
  if (!res.ok) throw new Error(`API 오류: ${res.status}`);
  return res.json();
}

/**
 * Firebase DataSnapshot 호환 객체 생성
 * .val(), .exists(), .forEach(cb) 지원
 */
function _createSnapshot(val) {
  return {
    val:    () => val,
    exists: () => val !== null && val !== undefined,
    key:    null,  // 상위 컨텍스트에서 설정됨
    forEach: (cb) => {
      if (val && typeof val === 'object') {
        for (const [key, value] of Object.entries(val)) {
          const childSnap = {
            key,
            val:    () => value,
            exists: () => value !== null && value !== undefined,
            forEach: (cb2) => {
              if (value && typeof value === 'object') {
                for (const [k2, v2] of Object.entries(value)) {
                  const shouldStop = cb2({ key: k2, val: () => v2, exists: () => true, forEach: () => {} });
                  if (shouldStop === true) break;
                }
              }
            }
          };
          const shouldStop = cb(childSnap);
          if (shouldStop === true) break;
        }
      }
    }
  };
}

// ── Firebase SDK 호환 내보내기 ─────────────────────────────────────────────

/**
 * initializeApp(config) → 기존 코드 호환을 위한 no-op
 * config에 있는 값들은 더 이상 사용되지 않음
 */
export function initializeApp(config) {
  console.log('[firebase-compat] initializeApp (no-op) - 자체 호스팅 서버 사용');
  return { _compat: true };
}

/**
 * getDatabase(app) → 기존 코드 호환을 위한 no-op
 */
export function getDatabase(app) {
  return { _compat: true };
}

/**
 * ref(db, 'mc_players/first') 또는 ref('mc_players/first')
 * → { _path: 'mc_players/first' } 반환
 *
 * db 파라미터(첫 번째)는 무시됨 - 기존 코드 호환
 */
export function ref(dbOrPath, pathStr) {
  let resolvedPath;
  if (typeof dbOrPath === 'string') {
    // ref('mc_players') 형태
    resolvedPath = dbOrPath;
  } else if (pathStr !== undefined) {
    // ref(db, 'mc_players') 형태 (일반적인 Firebase 패턴)
    resolvedPath = pathStr;
  } else {
    resolvedPath = '';
  }
  return { _path: _normPath(resolvedPath) };
}

/**
 * onValue(ref(db, 'mc_players'), callback)
 * → 초기 데이터 로드 후 실시간 업데이트 구독
 *
 * Firebase: 데이터 변경 시마다 콜백 자동 호출
 */
export async function onValue(refObj, callback) {
  const path = refObj._path;
  await _initSocket();

  // 리스너 등록
  if (!_listeners.has(path)) _listeners.set(path, new Set());
  _listeners.get(path).add(callback);

  // 초기 데이터 즉시 로드
  try {
    const val = await _fetchPath(path);
    callback(_createSnapshot(val));
  } catch (err) {
    console.error('[firebase-compat] onValue 초기 로드 실패:', err);
    callback(_createSnapshot(null));
  }
}

/**
 * get(ref(db, 'mc_players/first'))
 * → 일회성 데이터 조회 (Promise<DataSnapshot>)
 */
export async function get(refObj) {
  const val = await _fetchPath(refObj._path);
  return _createSnapshot(val);
}

/**
 * set(ref(db, 'mc_players/first'), data)
 * → 경로의 값을 완전히 덮어씀
 */
export async function set(refObj, data) {
  const res = await fetch('/api/set', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ path: refObj._path, data })
  });
  if (!res.ok) throw new Error(`set 실패: ${res.status}`);
}

/**
 * update(ref(db, 'mc_players/first'), { name: '새이름' })
 * → 지정된 필드만 얕은 병합 업데이트
 */
export async function update(refObj, data) {
  const res = await fetch('/api/update', {
    method:  'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ path: refObj._path, data })
  });
  if (!res.ok) throw new Error(`update 실패: ${res.status}`);
}

/**
 * push(ref(db, 'mc_notifications'), data)
 * → 자동 생성 키로 새 항목 추가
 * 반환: { key: '-abc123...' }
 */
export async function push(refObj, data) {
  const res = await fetch('/api/push', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ path: refObj._path, data })
  });
  if (!res.ok) throw new Error(`push 실패: ${res.status}`);
  return res.json();  // { key: '-...' }
}

/**
 * remove(ref(db, 'mc_notifications/-abc123'))
 * → 해당 경로의 데이터 삭제
 */
export async function remove(refObj) {
  const res = await fetch('/api/remove', {
    method:  'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ path: refObj._path })
  });
  if (!res.ok) throw new Error(`remove 실패: ${res.status}`);
}
