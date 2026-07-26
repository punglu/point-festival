/**
 * Compile-time boundary checks for generated OpenAPI wire types.
 * Generated definitions live in src/generated and must never be hand-edited.
 */
import type { components } from '../../generated/openapi';

type Assert<T extends true> = T;

type ExistingAdminLoginResponse = {
  access_token: string;
  token_type: string;
  display_name: string;
  player_id: number | null;
  is_admin: boolean;
};

type GeneratedAdminLoginResponse = components['schemas']['AdminLoginResponse'];

/** Existing page API mapping narrows the generated wire shape, never widens it. */
export type AdminLoginBoundaryCheck = Assert<
  ExistingAdminLoginResponse extends GeneratedAdminLoginResponse ? true : false
>;
