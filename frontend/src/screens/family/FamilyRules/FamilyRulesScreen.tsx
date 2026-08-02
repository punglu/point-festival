import styles from './FamilyRulesScreen.module.css';
import type { FamilyRulesProps } from './types';

export function FamilyRulesScreen({ model, onBack, onSave, onSelectRule, onAddRule }: FamilyRulesProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1v">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div><h1>가족 규칙</h1><span>우리 가족의 약속을 정해요</span></div>
        <button type="button" onClick={onSave}>저장</button>
      </header>
      <section>
        <article>
          <b>{model.heroTitle}</b>
          <p>{model.heroBody}</p>
        </article>
        <h2>{model.lifeRulesLabel}</h2>
        <div className={styles.list}>
          {model.lifeRules.map((rule) => (
            <button type="button" key={rule.name} onClick={() => onSelectRule?.(rule)}>
              <span>{rule.name}</span><b>{rule.value}</b><em>›</em>
            </button>
          ))}
        </div>
        <h2>{model.pointRulesLabel}</h2>
        <div className={styles.list}>
          {model.pointRules.map((rule) => (
            <button type="button" key={rule.name} onClick={() => onSelectRule?.(rule)}>
              <span>{rule.name}</span><b>{rule.value}</b><em>›</em>
            </button>
          ))}
        </div>
        <button type="button" className={styles.add} onClick={onAddRule}>＋ 규칙 추가하기</button>
      </section>
    </main>
  );
}
