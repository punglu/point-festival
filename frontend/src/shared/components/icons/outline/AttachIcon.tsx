import IconBase from './IconBase';
import type { OutlineIconProps } from './types';

export default function AttachIcon(props: OutlineIconProps) {
  return (
    <IconBase {...props}>
      <path d="M17.5 7.5 9 16a3 3 0 0 1-4.24-4.24l8.5-8.5a4.5 4.5 0 1 1 6.36 6.36l-8.5 8.5a2.12 2.12 0 0 1-3-3l7.07-7.07" />
    </IconBase>
  );
}
