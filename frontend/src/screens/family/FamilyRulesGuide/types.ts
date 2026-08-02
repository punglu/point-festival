export type FamilyRule={title:string;description:string};
export type FamilyRulesGuideModel={title:string;rules:FamilyRule[]};
export type FamilyRulesGuideProps={model:FamilyRulesGuideModel;onBack?:()=>void};
