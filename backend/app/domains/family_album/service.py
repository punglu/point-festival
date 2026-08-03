"""Family Album metadata service. Any active Family member may create an
album and add photo metadata -- collaborative, same shape as SLICE-TODO/
SLICE-SCHEDULE. Visibility (`shared_with_membership_ids`) only restricts
who an album is *shown to*; it is enforced by the caller-side filter in
`list_albums`/`get_album`, not a separate permission code."""
from __future__ import annotations
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family.models import FamilyMembership
from .models import FamilyAlbum, FamilyAlbumPhoto


def _visible_to(album: FamilyAlbum, membership_id: int) -> bool:
    if album.shared_with_membership_ids is None:
        return True
    return membership_id in album.shared_with_membership_ids


async def _photo_count(db: AsyncSession, album_id: int) -> int:
    return (
        await db.execute(select(func.count()).select_from(FamilyAlbumPhoto).where(FamilyAlbumPhoto.album_id == album_id))
    ).scalar_one()


async def list_albums(db: AsyncSession, family_id: int, viewer_membership_id: int) -> list[tuple[FamilyAlbum, int]]:
    stmt = select(FamilyAlbum).where(FamilyAlbum.family_group_id == family_id).order_by(FamilyAlbum.created_at.desc())
    albums = list((await db.execute(stmt)).scalars())
    visible = [a for a in albums if _visible_to(a, viewer_membership_id)]
    return [(a, await _photo_count(db, a.id)) for a in visible]


async def create_album(db: AsyncSession, family_id: int, actor: FamilyMembership, title: str) -> tuple[FamilyAlbum, int]:
    album = FamilyAlbum(family_group_id=family_id, created_by_membership_id=actor.id, title=title)
    db.add(album)
    await db.commit()
    await db.refresh(album)
    return album, 0


async def _get_album(db: AsyncSession, family_id: int, album_id: int) -> FamilyAlbum:
    album = await db.get(FamilyAlbum, album_id)
    if album is None or album.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="앨범을 찾을 수 없습니다")
    return album


async def get_album(db: AsyncSession, family_id: int, album_id: int, viewer_membership_id: int) -> tuple[FamilyAlbum, int]:
    album = await _get_album(db, family_id, album_id)
    if not _visible_to(album, viewer_membership_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="앨범을 찾을 수 없습니다")
    return album, await _photo_count(db, album.id)


async def update_album(db: AsyncSession, family_id: int, album_id: int, *, title: str | None, shared_with_membership_ids: list[int] | None) -> tuple[FamilyAlbum, int]:
    album = await _get_album(db, family_id, album_id)
    if title is not None:
        album.title = title
    if shared_with_membership_ids is not None:
        album.shared_with_membership_ids = shared_with_membership_ids
    await db.commit()
    await db.refresh(album)
    return album, await _photo_count(db, album.id)


async def list_photos(db: AsyncSession, family_id: int, album_id: int, viewer_membership_id: int) -> list[FamilyAlbumPhoto]:
    album = await _get_album(db, family_id, album_id)
    if not _visible_to(album, viewer_membership_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="앨범을 찾을 수 없습니다")
    stmt = select(FamilyAlbumPhoto).where(FamilyAlbumPhoto.album_id == album_id).order_by(FamilyAlbumPhoto.taken_at.is_(None), FamilyAlbumPhoto.taken_at.desc(), FamilyAlbumPhoto.id)
    return list((await db.execute(stmt)).scalars())


async def add_photo(db: AsyncSession, family_id: int, album_id: int, actor: FamilyMembership, *, caption: str | None, taken_at) -> FamilyAlbumPhoto:
    await _get_album(db, family_id, album_id)
    photo = FamilyAlbumPhoto(album_id=album_id, family_group_id=family_id, uploaded_by_membership_id=actor.id, caption=caption, taken_at=taken_at)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def search_photos(db: AsyncSession, family_id: int, viewer_membership_id: int, query: str) -> list[tuple[FamilyAlbumPhoto, FamilyAlbum]]:
    """1w -- caption search across every album the viewer can see."""
    stmt = (
        select(FamilyAlbumPhoto, FamilyAlbum)
        .join(FamilyAlbum, FamilyAlbum.id == FamilyAlbumPhoto.album_id)
        .where(FamilyAlbumPhoto.family_group_id == family_id, FamilyAlbumPhoto.caption.ilike(f"%{query}%"))
        .order_by(FamilyAlbumPhoto.taken_at.is_(None), FamilyAlbumPhoto.taken_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return [(photo, album) for photo, album in rows if _visible_to(album, viewer_membership_id)]
