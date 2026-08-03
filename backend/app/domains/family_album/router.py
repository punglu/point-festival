from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_family_membership
from app.domains.family.models import FamilyMembership
from . import service
from .models import FamilyAlbum
from .schemas import AlbumCreate, AlbumOut, AlbumUpdate, PhotoCreate, PhotoOut

router = APIRouter(tags=["family-album"])


def _album_out(album: FamilyAlbum, photo_count: int) -> AlbumOut:
    return AlbumOut(
        id=album.id, family_group_id=album.family_group_id, created_by_membership_id=album.created_by_membership_id,
        title=album.title, shared_with_membership_ids=album.shared_with_membership_ids, photo_count=photo_count,
    )


@router.get("/api/families/{family_id}/albums", response_model=list[AlbumOut])
async def list_albums(family_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return [_album_out(a, count) for a, count in await service.list_albums(db, family_id, actor.id)]


@router.post("/api/families/{family_id}/albums", response_model=AlbumOut, status_code=status.HTTP_201_CREATED)
async def create_album(family_id: int, body: AlbumCreate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    album, count = await service.create_album(db, family_id, actor, body.title)
    return _album_out(album, count)


# Declared before /albums/{album_id} -- a static path segment ("search")
# must be routed before a dynamic int segment, or FastAPI tries to parse
# "search" as album_id and 422s before this route is ever reached.
@router.get("/api/families/{family_id}/albums/search", response_model=list[PhotoOut])
async def search_photos(family_id: int, q: str = Query(min_length=1, max_length=100), actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return [photo for photo, _album in await service.search_photos(db, family_id, actor.id, q)]


@router.get("/api/families/{family_id}/albums/{album_id}", response_model=AlbumOut)
async def get_album(family_id: int, album_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    album, count = await service.get_album(db, family_id, album_id, actor.id)
    return _album_out(album, count)


@router.patch("/api/families/{family_id}/albums/{album_id}", response_model=AlbumOut)
async def update_album(family_id: int, album_id: int, body: AlbumUpdate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    album, count = await service.update_album(db, family_id, album_id, title=body.title, shared_with_membership_ids=body.shared_with_membership_ids)
    return _album_out(album, count)


@router.get("/api/families/{family_id}/albums/{album_id}/photos", response_model=list[PhotoOut])
async def list_photos(family_id: int, album_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.list_photos(db, family_id, album_id, actor.id)


@router.post("/api/families/{family_id}/albums/{album_id}/photos", response_model=PhotoOut, status_code=status.HTTP_201_CREATED)
async def add_photo(family_id: int, album_id: int, body: PhotoCreate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.add_photo(db, family_id, album_id, actor, caption=body.caption, taken_at=body.taken_at)
