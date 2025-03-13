from typing import Optional

from fastapi import HTTPException, Query
from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Brand
from core.schemas.carwash import BrandCreate, BrandUpdate


async def create_brand(session: AsyncSession, brand_create: BrandCreate) -> Brand:
    brand = Brand(**brand_create.dict())
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand

async def get_brand(session: AsyncSession, brand_id: int) -> Brand:
    stmt = select(Brand).filter(Brand.id == brand_id)
    result = await session.execute(stmt)
    brand = result.scalars().first()
    if not brand:
        raise ValueError("Brand not found")
    return brand
async def get_filtered_brands(
    session: AsyncSession,
    name: Optional[str] = None,
    sort_by: Optional[str] = Query("id", regex="^(id|name)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
) -> list[Brand]:
    stmt = select(Brand)
    result = await session.execute(stmt)
    brands = result.scalars().all()

    if name:
        brands = [brand for brand in brands if name.lower() in brand.name.lower()]

    if sort_by:
        if not hasattr(Brand, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")
        reverse = order == "desc"
        brands = sorted(brands, key=lambda brand: getattr(brand, sort_by), reverse=reverse)

    return brands

async def update_brand(session: AsyncSession, brand_id: int, brand_update: BrandUpdate) -> Brand:
    stmt = select(Brand).filter(Brand.id == brand_id)
    result = await session.execute(stmt)
    brand = result.scalars().first()
    if not brand:
        raise ValueError("Brand not found")

    for key, value in brand_update.dict(exclude_unset=True).items():
        setattr(brand, key, value)

    await session.commit()
    await session.refresh(brand)
    return brand

async def delete_brand(session: AsyncSession, brand_id: int) -> Brand:
    stmt = select(Brand).filter(Brand.id == brand_id)
    result = await session.execute(stmt)
    brand = result.scalars().first()
    if not brand:
        raise ValueError("Brand not found")

    await session.delete(brand)
    await session.commit()
    return brand