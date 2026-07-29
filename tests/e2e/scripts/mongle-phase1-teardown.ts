// MONGLE-FE-E2E-HARNESS-RESTORE-001: Playwright globalTeardown — stops the
// isolated mc_phase1 stack started by scripts/start-mongle-phase1.sh so no
// container or volume is left running after the suite finishes.
import { execFileSync } from 'node:child_process';
import path from 'node:path';

export default function globalTeardown() {
  const script = path.join(__dirname, 'stop-mongle-phase1.sh');
  execFileSync(script, { stdio: 'inherit' });
}
