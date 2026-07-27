import IconBase from './IconBase';
import type { OutlineIconProps } from './types';

export default function EditIcon(props: OutlineIconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 20 5 15.5 15.5 5 19 8.5 8.5 19Z" />
      <path d="M13 7 17 11" />
    </IconBase>
  );
}
