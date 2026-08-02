export type FamilyRuleEntry = { name: string; value: string };

export type FamilyRulesModel = {
  heroTitle: string;
  heroBody: string;
  lifeRulesLabel: string;
  lifeRules: FamilyRuleEntry[];
  pointRulesLabel: string;
  pointRules: FamilyRuleEntry[];
};

export type FamilyRulesProps = {
  model: FamilyRulesModel;
  onBack?: () => void;
  onSave?: () => void;
  onSelectRule?: (rule: FamilyRuleEntry) => void;
  onAddRule?: () => void;
};
