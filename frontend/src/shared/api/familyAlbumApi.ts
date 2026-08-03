/**
 * Family Album API client (W7.5 Phase D, SLICE-ALBUM-METADATA, canonical
 * `1h`/`1p`/`1w`/`2y`). Metadata only — no photo upload endpoint exists.
 * No storage abstraction exists anywhere in the backend (same gate as
 * avatar upload); a real `Photo` here has a caption/date, never an image.
 */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type FamilyAlbum = Schemas['AlbumOut'];
export type FamilyAlbumPhoto = Schemas['PhotoOut'];

export async function listAlbums(familyId: number, signal?: AbortSignal): Promise<FamilyAlbum[]> {
  const { data } = await httpClient.get<FamilyAlbum[]>(`/api/families/${familyId}/albums`, { signal });
  return data;
}

export async function listAlbumPhotos(familyId: number, albumId: number, signal?: AbortSignal): Promise<FamilyAlbumPhoto[]> {
  const { data } = await httpClient.get<FamilyAlbumPhoto[]>(`/api/families/${familyId}/albums/${albumId}/photos`, { signal });
  return data;
}

export async function searchAlbumPhotos(familyId: number, query: string, signal?: AbortSignal): Promise<FamilyAlbumPhoto[]> {
  const { data } = await httpClient.get<FamilyAlbumPhoto[]>(`/api/families/${familyId}/albums/search`, { params: { q: query }, signal });
  return data;
}

export async function updateAlbumSharing(familyId: number, albumId: number, sharedWithMembershipIds: number[] | null): Promise<FamilyAlbum> {
  const { data } = await httpClient.patch<FamilyAlbum>(`/api/families/${familyId}/albums/${albumId}`, { shared_with_membership_ids: sharedWithMembershipIds });
  return data;
}
