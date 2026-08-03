import styles from './BrandCharacter.module.css';
import mongliCelebration from '../../../assets/logos/family-platform-mascot.png';

/**
 * 몽글이 캐릭터 자산. PM 승인 원본 PNG를 원본 비율 그대로 렌더링한다 — 크롭,
 * 재생성, CSS filter 금지 (MONGLE-BRAND-AUTH-HERO-CORRECTION-001).
 *
 * The source file is the repo's existing canonical mascot asset
 * (`assets/logos/family-platform-mascot.png`, SHA-256 dd5c48b3...) — it is
 * byte-identical to the PM-provided `mongli-character-celebration.png`, so
 * this component reuses it rather than registering a duplicate copy under a
 * second name/path.
 *
 * Deliberately separate from MainLogo (wordmark/smile SVG) — same hero
 * region, independent asset and DOM element, never merged into one lockup.
 */

export type BrandCharacterVariant = 'celebration';
export type BrandCharacterSize = number | 'profileHero' | 'loginHero';

const SIZE_PRESETS: Record<Exclude<BrandCharacterSize, number>, number> = {
  profileHero: 176,
  loginHero: 116,
};

interface BrandCharacterProps {
  variant?: BrandCharacterVariant;
  size?: BrandCharacterSize;
  /** True when an adjacent element (e.g. the MainLogo wordmark) already
   * carries the accessible brand name, so this image is redundant to
   * screen readers. */
  decorative?: boolean;
  className?: string;
}

export default function BrandCharacter({
  variant = 'celebration',
  size = 'profileHero',
  decorative = false,
  className,
}: BrandCharacterProps) {
  const width = typeof size === 'number' ? size : SIZE_PRESETS[size];
  const src = variant === 'celebration' ? mongliCelebration : mongliCelebration;

  return (
    <img
      src={src}
      style={{ width, height: 'auto' }}
      className={[styles.character, className].filter(Boolean).join(' ')}
      alt={decorative ? '' : '몽글이가 두 팔을 벌려 축하하는 모습'}
      aria-hidden={decorative || undefined}
    />
  );
}
