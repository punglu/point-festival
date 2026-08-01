import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/reset.css';
import './styles/global.css';

// MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001: register the Wagle Push
// service worker. Deliberately non-blocking and failure-tolerant — Push is a
// background convenience, and every message stays recoverable from the durable
// history whether or not this succeeds. A browser without service-worker
// support simply gets no background notifications.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      /* no Push on this browser; the app is unaffected */
    });
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
