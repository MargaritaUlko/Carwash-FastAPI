from http.client import HTTPException
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession



from core.authentication.dependecy import check_access
from core.config import settings
from core.models import db_helper, User, Brand
from core.schemas.carwash import (
    BrandRead,
    BrandCreate,
    BrandUpdate,
)
from crud.carwash import brand as brand_crud
from crud.carwash.brand import get_filtered_brands

brand_router = APIRouter(
    prefix=settings.api.v1.brands,
    tags=["Brands"],
)


@brand_router.get("", response_model=list[BrandRead])
async def get_brands_api(
    session: AsyncSession = Depends(db_helper.session_getter),
    limit: int = Query(10, ge=1),  # Ограничение количества элементов на странице
    page: int = Query(1, ge=1),  # Номер страницы
    name: Optional[str] = None,  # Фильтрация по имени бренда
    sort_by: Optional[str] = Query("id", regex="^(id|name)$"),  # Поле для сортировки
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),  # Направление сортировки
    user: User = Depends(check_access([1]))
):
    # Получаем отфильтрованные бренды через функцию
    brands = await get_filtered_brands(
        session=session,
        name=name,
        sort_by=sort_by,
        order=order
    )

    # Пагинация
    offset = (page - 1) * limit
    paginated_brands = brands[offset:offset + limit]

    return paginated_brands


@brand_router.get("/{brand_id}", response_model=BrandRead)
async def get_brand(
    brand_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    brand = await brand_crud.get_brand(session=session, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@brand_router.post("", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_create: BrandCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    brand = await brand_crud.create_brand(session=session, brand_create=brand_create)
    return brand


@brand_router.put("/{brand_id}", response_model=BrandRead)
async def update_brand(
    brand_update: BrandUpdate,
    brand_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    brand = await brand_crud.update_brand(
        session=session, brand_id=brand_id, brand_update=brand_update
    )
    if not brand:
        
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@brand_router.delete("/{brand_id}")
async def delete_brand(
    brand_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    deleted = await brand_crud.delete_brand(session=session, brand_id=brand_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"message": "Brand deleted"}


