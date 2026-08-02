export type AlbumShareSettingsModel={album:string;photoCount:number;members:{name:string;enabled:boolean}[]};
export type AlbumShareSettingsProps={model:AlbumShareSettingsModel;onBack?:()=>void;onSave?:()=>void};
