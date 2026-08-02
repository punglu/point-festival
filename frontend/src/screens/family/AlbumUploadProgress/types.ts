export type AlbumUploadProgressModel={title:string;total:number;uploaded:number;items:{name:string;status:string}[]};
export type AlbumUploadProgressProps={model:AlbumUploadProgressModel;onClose?:()=>void};
