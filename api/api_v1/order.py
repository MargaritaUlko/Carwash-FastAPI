from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import current_user
import asyncio

from api.api_v1.fastapi_users import fastapi_users
from core.authentication.dependecy import check_access
# check_order_list_access, check_order_by_id
from core.config import settings
from core.models import db_helper, Order, User
from core.schemas.carwash import OrderCreate, OrderRead, OrderUpdate, OrderBase
from crud.carwash import order as order_crud
from crud.carwash.order import get_orders, get_order

order_router = APIRouter(
    prefix=settings.api.v1.orders,
    tags=["Orders"],
)
# Инъекция зависимостей

# Customer_car - в ней поиск по моделям машины

@order_router.get("/orders", response_model=List[OrderRead])
async def api_get_orders(
    session: AsyncSession = Depends(db_helper.session_getter),
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    sort_by: Optional[str] = Query("id", regex="^(id|start_date)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    status: Optional[int] = Query(None, ge=0, le=1),
    user: User = Depends(fastapi_users.current_user()),
):
    orders = await get_orders(
        user=user,
        session=session,
        limit=limit,
        page=page,
        sort_by=sort_by,
        order=order,
        status=status,
    )

    serialized_orders = [await OrderRead.from_orm(order) for order in orders]

    return serialized_orders

@order_router.get("/{order_id}", response_model=OrderRead)
async def get_order_by_id(
    order_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(fastapi_users.current_user())
):
    order = await get_order(session, order_id, user)
    serialized_orders = await OrderRead.from_orm(order)

    return serialized_orders


@order_router.post("", response_model=OrderBase, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_create: OrderCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    order = await order_crud.create_order(session=session, order_create=order_create)
    return order


@order_router.patch("/{order_id}", response_model=OrderBase)
async def update_order(
        order_update: OrderUpdate,
        order_id: int,
        session: AsyncSession = Depends(db_helper.session_getter),
        user: User = Depends(check_access([1]))
):
    order = await order_crud.update_order(
        session=session, order_id=order_id, order_update=order_update
    )
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return order
@order_router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    deleted = await order_crud.delete_order(session=session, order_id=order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return {"message": "Заказ не удален"}
