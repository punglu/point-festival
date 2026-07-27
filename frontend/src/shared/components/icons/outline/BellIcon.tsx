import IconBase from './IconBase';
import type { OutlineIconProps } from './types';

export default function BellIcon(props: OutlineIconProps) {
  return (
    <IconBase {...props}>
      <path d="M6 8a6 6 0 1 1 12 0c0 4 1.5 5.5 2 6H4c.5-.5 2-2 2-6Z" />
      <path d="M9.5 19a2.5 2.5 0 0 0 5 0" />
    </IconBase>
  );
}
