// MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001
// Preview-only mount for the A2 standalone Vite entry
// (frontend/a2-family-home-preview.html). This exists because App.tsx is owned
// by the parallel 1e lane this round, so /__wave6/1b is deliberately NOT
// registered — route integration is deferred to the Integration Relay.
//
// This is not a product entry point. It intentionally omits main.tsx's service
// worker registration so the preview performs no storage write, no navigation
// and no background registration. The two global stylesheets are imported
// read-only so the preview inherits exactly the same reset and font delivery
// (Noto Sans KR 400/500/700/900) the routed app would give it.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '../../styles/reset.css';
import '../../styles/global.css';
import { FamilyHomePreview } from './index';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <FamilyHomePreview />
  </StrictMode>,
);
