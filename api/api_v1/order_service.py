from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.authentication.dependecy import check_access, check_order_list_access22
from core.config import settings
from core.models import db_helper, OrderService, User
from crud.carwash import order_service as order_service_crud
from core.schemas.carwash import OrderServiceCreate, OrderServiceRead, OrderServiceUpdate
from crud.carwash.order_service import get_order_services

order_service_router = APIRouter(
    prefix=settings.api.v1.order_services,
    tags=["Order_services"],
)

@order_service_router.get("", response_model=list[OrderServiceRead])
async def api_get_order_services(
    session: AsyncSession = Depends(db_helper.session_getter),
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    sort_by: Optional[str] = Query("id", regex="^(id|service_name|order_id)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    order_id: Optional[int] = Query(None),
    orders: list[OrderService] = Depends(check_order_list_access22()),
):

    order_services = await get_order_services(
        session=session,
        orders=orders,
        order_id=order_id,
        sort_by=sort_by,
        order=order
    )

    # Пагинация
    offset = (page - 1) * limit
    order_services_paginated = order_services[offset:offset + limit]

    return order_services_paginated




# Получение информации о заказе с сервисом по id
@order_service_router.get("/{order_service_id}", response_model=OrderServiceRead)
async def get_order_service(
    order_service_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    orders: list[OrderService] = Depends(check_order_list_access22()),  # Проверяем доступные заказы пользователя
):
    # Ищем заказ среди доступных для пользователя
    order_service = next((service for service in orders if service.id == order_service_id), None)

    # Если заказ не найден, выбрасываем ошибку 404
    if not order_service:
        raise HTTPException(status_code=404, detail="OrderService not found")

    return order_service


# Создание нового заказа с сервисом
# @order_service_router.post("", response_model=OrderServiceCreate, status_code=status.HTTP_201_CREATED)
# async def create_order_service(
#     order_service_create: OrderServiceCreate,
#     session: AsyncSession = Depends(db_helper.session_getter),
#     user: User = Depends(check_access([1]))
# ):
#     try:
#         order_service = await order_service_crud.create_order_service(
#             session=session,
#             order_service_create=order_service_create
#         )
#         return order_service
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))  # Логическая ошибка
#     except Exception as e:
#         # Логирование ошибки
#         print(f"Unexpected error in create_order_service: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")


@order_service_router.post("", status_code=status.HTTP_201_CREATED)
async def create_order_services(
    order_service_create: OrderServiceCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    results = await order_service_crud.create_order_services(
        session=session,
        order_service_create=order_service_create
    )

    errors = [result for result in results if "error" in result]
    if errors:
        raise HTTPException(status_code=400, detail=errors)

    return [result["data"] for result in results if "data" in result]

@order_service_router.put("/{order_service_id}", response_model=OrderServiceRead)
async def update_order_service(
    order_service_update: OrderServiceUpdate,
    order_service_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    order_service = await order_service_crud.update_order_service(
        session=session, order_service_id=order_service_id, order_service_update=order_service_update
    )
    if not order_service:
        raise HTTPException(status_code=404, detail="OrderService not found")
    return order_service


# Удаление заказа с сервисом
@order_service_router.delete("/{order_service_id}")
async def delete_order_service(
    order_service_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    deleted = await order_service_crud.delete_order_service(session=session, order_service_id=order_service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="OrderService not found")
    return {"message": "OrderService deleted"}
