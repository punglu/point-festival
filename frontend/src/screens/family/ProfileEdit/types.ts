export type ProfileEditModel = {
  name: string;
  colors: { value: string; selected: boolean }[];
  bio: string;
  birthday: string;
  familyRole: string;
};
export type ProfileEditProps = { model: ProfileEditModel; onBack?: () => void; onSave?: () => void };
