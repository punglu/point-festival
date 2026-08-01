/**
 * `/wagle` route entry.
 *
 * MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001: this file previously rendered
 * ~290 lines of preview fixtures — sample rooms, sample messages, a
 * `previewState` query parameter. All of it is gone. The screen now renders
 * `WagleRoomView`, which reads real rooms and messages from the Target API.
 *
 * The fixture modules under `../wagle/preview/` are left in the tree as the
 * design reference they always were, but **nothing in the production path
 * imports them any more**. A conversation screen that silently falls back to
 * sample data when the API fails is worse than one that reports the failure.
 *
 * The two wrappers are deliberate and ordered:
 *   WaglePinLock — gates this screen's content on this device only. The Account
 *                  Session, Markpoint and the Family screens stay reachable
 *                  behind it, which is contract, not incidental.
 *   WagleRoomView — owns the API, the realtime client and every screen state.
 */
import { useNavigate } from 'react-router-dom';

import { WaglePinLock } from '../wagle/components';
import { WagleRoomView } from '../wagle/WagleRoomView';

export function WagleLanding() {
  const navigate = useNavigate();

  return (
    // Leaving Wagle is always available while locked — the lock covers this
    // screen, not the platform.
    <WaglePinLock onLeave={() => navigate('/markpoint')}>
      <WagleRoomView />
    </WaglePinLock>
  );
}
