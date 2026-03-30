// firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";

// ===========================================================
// 1. 환경별 설정 값 (Config)
// ===========================================================

// [운영계] mark-point-festivals
const prodConfig = {
    apiKey: "AIzaSyCuvaYFkKVQLFXZXtum8o7kD1XUyw_MQvE", // (기존 운영 Key 유지)
    authDomain: "mark-point-festivals.firebaseapp.com",
    databaseURL: "https://mark-point-festivals-default-rtdb.firebaseio.com",
    projectId: "mark-point-festivals",
    storageBucket: "mark-point-festivals.firebasestorage.app",
    messagingSenderId: "87999590531",
    appId: "1:87999590531:web:418d4fc2a7f175ea56ebb6"
};

// [개발계] mark-point-dev (새로 만든 프로젝트 정보 입력 필수!)
const devConfig = {
    apiKey: "AIzaSyBVfTiYEHTeon2zdbXEZsaDzkV0",
    authDomain: "mark-point-festivals-dev.firebaseapp.com",
    databaseURL: "https://mark-point-festivals-dev-default-rtdb.firebaseio.com",
    projectId: "mark-point-festivals-dev",
    storageBucket: "mark-point-festivals-dev.firebasestorage.app",
    messagingSenderId: "876196518434",
    appId: "1:876196518434:web:e60a09f47a910a9b79887b"
};

// ===========================================================
// 2. 환경 감지 및 초기화 로직
// ===========================================================

const hostname = window.location.hostname;
const isLocal = hostname === "localhost" || hostname === "127.0.0.1";

const config = isLocal ? devConfig : prodConfig;

// 콘솔에 현재 환경 출력 (디버깅용)
console.log(
    `%c 🚀 Firebase Mode: ${isLocal ? "[개발/로컬]" : "[운영/배포]"} `,
    `background: ${isLocal ? "#4ade80" : "#ef4444"}; color: #000; font-weight: bold; padding: 4px; border-radius: 4px;`
);

// Firebase 초기화
const app = initializeApp(config);
const db = getDatabase(app);

// 다른 파일에서 쓸 수 있도록 내보내기
export { app, db };