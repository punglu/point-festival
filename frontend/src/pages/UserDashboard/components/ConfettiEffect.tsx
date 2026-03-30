import { useEffect, useState, useCallback } from 'react';
import styles from '../UserDashboard.module.css';

interface ConfettiEffectProps {
  trigger: boolean;
}

interface Particle {
  id: number;
  x: number;
  color: string;
  delay: number;
  duration: number;
}

const COLORS = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];

export default function ConfettiEffect({ trigger }: ConfettiEffectProps) {
  const [particles, setParticles] = useState<Particle[]>([]);

  const createParticles = useCallback(() => {
    const newParticles: Particle[] = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      delay: Math.random() * 0.5,
      duration: 1.5 + Math.random() * 1,
    }));
    setParticles(newParticles);
    // 애니메이션 종료 후 정리
    setTimeout(() => setParticles([]), 3000);
  }, []);

  useEffect(() => {
    if (trigger) createParticles();
  }, [trigger, createParticles]);

  if (particles.length === 0) return null;

  return (
    <div className={styles.confettiContainer}>
      {particles.map(p => (
        <div
          key={p.id}
          className={styles.confettiParticle}
          style={{
            left: `${p.x}%`,
            backgroundColor: p.color,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
          }}
        />
      ))}
    </div>
  );
}
