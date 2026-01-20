from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.session import get_db
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.models.item import Item as ItemModel
from app.models.user import User
from app.dependencies.auth import get_current_active_user


router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new item"""
    db_item = ItemModel(**item.dict(), owner_id=current_user.id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[Item])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all items for current user"""
    stmt = select(ItemModel).filter(ItemModel.owner_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items


@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific item"""
    stmt = select(ItemModel).filter(ItemModel.id == item_id, ItemModel.owner_id == current_user.id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
