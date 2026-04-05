/**
 * 공통 아이콘 컴포넌트.
 * src/assets/icons/ 에서 에셋 로드. 없으면 이모지 폴백.
 *
 * 사용 가능한 아이콘명 (에셋 시트에서 추출):
 *   gem, coin, trophy, medal-gold, medal-silver,
 *   star, checklist, flag, levelup, lightbulb
 */

// 이모지 폴백 맵 (에셋 로드 실패 시)
const EMOJI_MAP: Record<string, string> = {
  gem: '💎',
  coin: '🪙',
  trophy: '🏆',
  'medal-gold': '🏅',
  'medal-silver': '🥈',
  star: '⭐',
  flag: '🚩',
  checklist: '📋',
  levelup: '⬆️',
  lightbulb: '💡',
  home: '🏠',
};

// Vite의 import.meta.glob으로 에셋 이미지 동적 로드
const iconModules = import.meta.glob<{ default: string }>(
  '../../../assets/icons/*.{png,svg}',
  { eager: true }
);

const iconMap: Record<string, string> = {};
for (const [path, mod] of Object.entries(iconModules)) {
  const name = path.split('/').pop()?.replace(/\.(png|svg)$/, '') ?? '';
  iconMap[name] = mod.default;
}

interface AppIconProps {
  name: string;
  size?: number;
  className?: string;
}

export default function AppIcon({ name, size = 24, className }: AppIconProps) {
  const src = iconMap[name];

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        width={size}
        height={size}
        className={className}
        style={{ display: 'inline-block', verticalAlign: 'middle' }}
      />
    );
  }

  // 이모지 폴백
  return (
    <span
      role="img"
      aria-label={name}
      className={className}
      style={{ fontSize: size * 0.75, lineHeight: 1, verticalAlign: 'middle' }}
    >
      {EMOJI_MAP[name] ?? '❓'}
    </span>
  );
}
