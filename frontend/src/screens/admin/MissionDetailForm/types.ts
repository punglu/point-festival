export type MissionDetailFormModel={title:string;description:string;assignees:string;points:number;history:{name:string;time:string;status:'승인'|'반려'}[]};
export type MissionDetailFormProps={
  model:MissionDetailFormModel;
  /** Product embeds this Screen inside its own modal/overlay (AdminLayout
   *  already owns the real Sidebar) -- suppresses the frozen preview's own
   *  decorative sidebar so Product doesn't render it twice. Detached Preview
   *  omits this prop, so its own visual baseline is unchanged. */
  embedded?:boolean;
  onClose?:()=>void;
  onSave?:()=>void;
  onDelete?:()=>void;
};
