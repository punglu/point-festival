import styles from './MainLogo.module.css';

/**
 * 몽글 공식 브랜드 워드마크/캐릭터 시스템.
 * Source: 몽글 브랜드 가이드 v1.0 (Claude Design "PWA 메인 화면 로고 디자인",
 * 2026-08-03). SVG path data is copied verbatim from that guide — do not edit
 * the path values by hand.
 *
 * - variant "wordmark" (19c, default): 기본 워드마크. 앱 헤더·내비게이션·
 *   로그인·서비스 소개에 사용.
 * - variant "smile" (19b): 스마일 워드마크. 스플래시·온보딩·환영·브랜드 소개
 *   등 감성 화면에서만 선택적으로 사용. descriptor와 결합하지 않는다.
 *
 * Colors (tone) are the guide's own literal "배경 사용 예시" values — a
 * brand-asset-only palette, intentionally NOT the app UI's frozen
 * --color-brand-600 / --color-ink-900 tokens (see MainLogo.module.css).
 *
 * DRAFT: the guide leaves protective space and minimum usable size
 * unconfirmed ("실측 및 PM 승인 전까지 DRAFT"). Several existing call sites
 * below preserve a pre-existing layout footprint smaller than the guide's
 * "권장" (recommended) size band (19c ≥64px, 19b ≥128px) — see the `size`
 * prop passed at each usage. Not a blocker per PM decision; flagged here for
 * whenever the guide's sizing gate is finalized.
 */

export type MongleLogoVariant = 'wordmark' | 'smile';
export type MongleLogoTone = 'default' | 'onBrand' | 'onDark';

const TONE_STROKE: Record<MongleLogoTone, string> = {
  default: '#4B3591', // light/neutral background
  onBrand: '#FFFFFF', // brand-purple background
  onDark: '#B8A9EF', // dark background
};

interface MainLogoProps {
  variant?: MongleLogoVariant;
  tone?: MongleLogoTone;
  /** Pixel size (square), or the "welcome" preset (110px, 140px at >=700px). */
  size?: number | 'welcome';
  /** Optional "for family" descriptor text below the wordmark. wordmark only. */
  descriptor?: boolean;
  /** Supplementary effects only (filter, margin) — do not set width/height here. */
  className?: string;
  'aria-hidden'?: boolean;
}

export default function MainLogo({
  variant = 'wordmark',
  tone = 'default',
  size = 96,
  descriptor = false,
  className,
  'aria-hidden': ariaHidden = false,
}: MainLogoProps) {
  const stroke = TONE_STROKE[tone];
  const showDescriptor = descriptor && variant === 'wordmark';
  const sizeStyle = size === 'welcome' ? undefined : { width: size, height: size };
  const markClassName = [styles.mark, size === 'welcome' ? styles.welcomeSize : null, className]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={styles.logo}>
      {variant === 'wordmark' ? (
        <svg
          className={markClassName}
          style={sizeStyle}
          viewBox="0 0 480 260"
          role={ariaHidden ? undefined : 'img'}
          aria-hidden={ariaHidden || undefined}
          aria-label={ariaHidden ? undefined : '몽글'}
        >
          <g stroke={stroke} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth={20}>
            <path d="M80 28 Q120 24 158 27 Q174 29 175 48 Q176 74 171 92 Q130 99 80 95 Q64 93 63 74 Q62 48 67 37 Q71 29 80 28 Z" />
            <path d="M120 100 Q121 116 119 132" />
            <path strokeWidth={19} d="M64 142 Q120 135.5 176 141" />
            <circle cx={119} cy={200} r={33} />
            <g transform="translate(-41,0)">
              <path strokeWidth={19} d="M272 139 Q326 132.5 380 138" />
              <path d="M272 32 Q316 27 344 30 Q364 32 365 54 Q366 80 362 102" />
              <path d="M280 168 Q322 164 352 167 Q370 169 370 183 Q370 197 352 199 Q322 202 296 200 Q278 199 277 213 Q276 227 294 229 Q330 233 366 229" />
            </g>
          </g>
        </svg>
      ) : (
        <svg
          className={markClassName}
          style={sizeStyle}
          viewBox="0 0 450 260"
          role={ariaHidden ? undefined : 'img'}
          aria-hidden={ariaHidden || undefined}
          aria-label={ariaHidden ? undefined : '몽글'}
        >
          <g stroke={stroke} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth={19}>
            <path strokeWidth={19} d="M78 127 Q212 149 343 126" />
            <path d="M80 28 Q120 24 158 27 Q174 29 175 48 Q176 74 171 92 Q130 99 80 95 Q64 93 63 74 Q62 48 67 37 Q71 29 80 28 Z" />
            <path d="M120 100 Q121 111 120 121" />
            <circle cx={119} cy={198} r={33} />
            <g transform="translate(-45,0)">
              <path d="M276 33 Q314 28 336 30 Q354 32 358 46 Q361 60 360 80 Q360 95 358.5 110" />
              <path d="M280 166 Q322 162 352 165 Q370 167 370 181 Q370 195 352 197 Q322 200 296 198 Q278 197 277 211 Q276 225 294 227 Q330 231 366 227" />
            </g>
          </g>
        </svg>
      )}
      {showDescriptor && (
        <span className={styles.descriptor} style={{ color: stroke }}>
          for family
        </span>
      )}
    </span>
  );
}
