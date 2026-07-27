import IconBase from './IconBase';
import type { OutlineIconProps } from './types';

export default function BackIcon(props: OutlineIconProps) {
  return (
    <IconBase {...props}>
      <path d="M15 5 8 12l7 7" />
    </IconBase>
  );
}
