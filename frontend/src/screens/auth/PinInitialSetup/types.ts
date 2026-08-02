export type PinInitialSetupModel={title:string;description:string;step:string};
export type PinInitialSetupProps={model:PinInitialSetupModel;onKeyPress?:(key:string)=>void;onBack?:()=>void};
