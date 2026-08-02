export type FamilyRuleItem = { title: string; description: string; tone: 'purple' | 'red' | 'blue' | 'green' | 'yellow' };
export type FamilyRuleGroup = { label: string; items: FamilyRuleItem[] };
export type FamilyRulesGuideModel = {
  title: string;
  heroTitle: string;
  heroBody: string;
  groups: FamilyRuleGroup[];
  notice: string;
  confirmLabel: string;
};
export type FamilyRulesGuideProps = { model: FamilyRulesGuideModel; onBack?: () => void; onConfirm?: () => void };
