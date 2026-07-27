import IconBase from './IconBase';
import type { OutlineIconProps } from './types';

export default function SettingsIcon(props: OutlineIconProps) {
  return (
    <IconBase {...props}>
      <line x1="4" y1="7" x2="20" y2="7" />
      <circle cx="9" cy="7" r="2" />
      <line x1="4" y1="12" x2="20" y2="12" />
      <circle cx="15" cy="12" r="2" />
      <line x1="4" y1="17" x2="20" y2="17" />
      <circle cx="7" cy="17" r="2" />
    </IconBase>
  );
}
