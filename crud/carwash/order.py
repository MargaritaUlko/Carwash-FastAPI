from datetime import datetime
from http.client import HTTPException
from typing import Optional, List, Awaitable, Callable

import pytz
from fastapi import Depends
from sqlalchemy import select, Sequence, or_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException

from api.api_v1.fastapi_users import fastapi_users
from core.models import Order, OrderService, Customer_Car
from core.models.users import  User
from core.schemas.carwash import OrderCreate, OrderUpdate, ServiceRead, OrderRead


async def create_order(session: AsyncSession, order_create: OrderCreate):
    order = Order(**order_create.dict())
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

async def get_order(session: AsyncSession, order_id: int, user: User) -> Order:

    base_query = select(Order).filter(Order.id == order_id)
    result = await session.execute(base_query)
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")


    if user.role_id == 1:
        query = base_query
    else:
        query = base_query.filter(
            or_(
                Order.employee_id == user.id,
                Order.administrator_id == user.id,
                Order.customer_car_id.in_(
                    select(Customer_Car.id).filter(Customer_Car.customer_id == user.id)
                ),
            )
        )

    query = query.options(
        joinedload(Order.order_services).joinedload(OrderService.service),
        joinedload(Order.customer_car).joinedload(Customer_Car.car),
        joinedload(Order.employee),
        joinedload(Order.administrator),
    )

    result = await session.execute(query)
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=403, detail="У вас недостаточно прав для просмотра")

    return order



async def get_orders(
        user: User,
        session: AsyncSession,
        limit: int = 10,
        page: int = 1,
        sort_by: Optional[str] = "id",
        order: Optional[str] = "asc",
        status: Optional[int] = None,

) -> List[Order]:


    if user.role_id == 1:
        query = select(Order)
    else:

        query = select(Order).filter(
            or_(
                Order.employee_id == user.id,
                Order.administrator_id == user.id,
                Order.customer_car_id.in_(
                    select(Customer_Car.id).filter(Customer_Car.customer_id == user.id)
                ),
            )
        )
    result = await session.execute(query)
    orders = result.scalars().all()

    if not orders:
        raise HTTPException(status_code=403, detail="Нет доступных закзаов для данного пользователя")

    query = select(Order).options(
        joinedload(Order.employee),
        joinedload(Order.administrator),
        joinedload(Order.customer_car).joinedload(Customer_Car.car),
        joinedload(Order.order_services).joinedload(OrderService.service),
    )

    if status is not None:
        query = query.filter(Order.status == status)

    query = query.filter(Order.id.in_([order.id for order in orders]))

    query = query.offset((page - 1) * limit).limit(limit)

    try:
        result = await session.execute(query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    orders = result.unique().scalars().all()


    if sort_by:
        if not hasattr(Order, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")

        reverse = order == "desc"
        orders = sorted(orders, key=lambda order: getattr(order, sort_by), reverse=reverse)

    return orders

async def update_order(session: AsyncSession, order_id: int, order_update: OrderUpdate) -> Order:

    stmt = select(Order).filter(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalars().first()
    krasnoyarsk_tz = pytz.timezone("Asia/Krasnoyarsk")
    now = datetime.now(krasnoyarsk_tz)
    if not order:
        raise ValueError("Order not found")
    if order.end_date < now:
        raise HTTPException(status_code=400, detail=f"Ты не можешь обновить выполненный заказ!")

    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(order, key, value)

    await session.commit()
    await session.refresh(order)
    return order


async def delete_order(session: AsyncSession, order_id: int) -> Order:
    stmt = select(Order).filter(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalars().first()
    if not order:
        raise ValueError("Заказ не найден")

    await session.delete(order)
    await session.commit()
    return order


































# async def get_order(session: AsyncSession, order_id: int):
#     stmt = select(Order).options(
#         joinedload(Order.order_services).joinedload(OrderService.service),
#         joinedload(Order.customer_car).joinedload(Customer_Car.car),
#         joinedload(Order.employee),
#         joinedload(Order.administrator),
#     ).filter(Order.id == order_id)
#
#     result = await session.execute(stmt)
#     order = result.scalars().first()
#
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#
#     services = [
#         ServiceRead.from_orm(service.service) for service in order.order_services
#     ]
#
#     car_model = order.customer_car.car.model if order.customer_car and order.customer_car.car else None
#     employee_name = f"{order.employee.first_name} {order.employee.last_name}" if order.employee else None
#     administrator_name = f"{order.administrator.first_name} {order.administrator.last_name}" if order.administrator else None
#     krasnoyarsk_tz = pytz.timezone("Asia/Krasnoyarsk")
#     order_read = OrderRead(
#         id=order.id,
#         administrator_id=order.administrator_id,
#         customer_car_id=order.customer_car_id,
#         employee_id=order.employee_id,
#         status=order.status,
#         start_date=order.start_date.astimezone(krasnoyarsk_tz),
#         end_date=order.end_date.astimezone(krasnoyarsk_tz),
#         services=services,
#         car=car_model,
#         employee_name=employee_name,
#         administrator_name=administrator_name,
#     )
#     return order_read
#
# async def get_orders(
#     session: AsyncSession,
#     limit: int = 10,
#     page: int = 1,
#     sort_by: Optional[str] = "id",
#     order: Optional[str] = "asc",
#     status: Optional[int] = None
# ) -> List[Order]:
#     query = select(Order).options(
#         joinedload(Order.employee),
#         joinedload(Order.administrator),
#         joinedload(Order.customer_car).joinedload(Customer_Car.car),
#         joinedload(Order.order_services).joinedload(OrderService.service),
#     )
#
#     # Apply filter based on order status
#     if status is not None:
#         query = query.filter(Order.status == status)
#
#     # Apply pagination: offset based on page and limit
#     query = query.offset((page - 1) * limit).limit(limit)
#
#     # Execute query and get the results
#     try:
#         result = await session.execute(query)
#     except InvalidRequestError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
#     # Extract all the orders from the result
#     orders = result.unique().scalars().all()
#
#     # Sort orders for the entire collection
#     if sort_by:
#         # Validate sort_by field exists
#         if not hasattr(Order, sort_by):
#             raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")
#
#         # Sort data for the entire collection
#         reverse = order == "desc"
#         orders = sorted(orders, key=lambda order: getattr(order, sort_by), reverse=reverse)
#
#     return orders


