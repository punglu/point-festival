import type { SVGProps } from 'react';

/**
 * §6 스펙: stroke 1.75-2, round cap/join, currentColor.
 * navigation 24px / inline 20px / status 16px는 소비처에서 size prop으로 지정한다.
 */
export interface OutlineIconProps extends Omit<SVGProps<SVGSVGElement>, 'children'> {
  size?: number;
  /** 제공 시 아이콘이 의미 전달 주체가 되어 role="img"+title로 렌더링된다. 미제공 시 장식용(aria-hidden)으로 렌더링된다. */
  title?: string;
}
