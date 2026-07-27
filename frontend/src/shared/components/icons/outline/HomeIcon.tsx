import IconBase from './IconBase';
import type { OutlineIconProps } from './types';

export default function HomeIcon(props: OutlineIconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 11.5 12 4l8 7.5" />
      <path d="M6 10v9a1 1 0 0 0 1 1h4v-5h2v5h4a1 1 0 0 0 1-1v-9" />
    </IconBase>
  );
}
