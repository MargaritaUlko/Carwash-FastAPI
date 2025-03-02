from datetime import timedelta, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, Sequence
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from sqlalchemy.orm import joinedload

from core.models import OrderService, Order, Service
from core.schemas.carwash import OrderServiceCreate, OrderServiceUpdate
import pytz
logger = logging.getLogger(__name__)



from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import OrderService, Order, Service
from core.schemas.carwash import OrderServiceCreate
import pytz
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


LOCAL_TIMEZONE = pytz.timezone("Asia/Krasnoyarsk")



KRASNOYARSK_TZ = pytz.timezone("Asia/Krasnoyarsk")

async def create_order_services(session: AsyncSession, order_service_create: OrderServiceCreate):
    # Шаг 1: Проверка заказа
    stmt_order = select(Order).filter(Order.id == order_service_create.order_id)
    result_order = await session.execute(stmt_order)
    order = result_order.scalars().first()

    if not order:
        return [{"error": "order_not_found", "message": "Order not found"}]

    results = []

    for service_id in order_service_create.service_ids:
        # Шаг 2: Проверка услуги
        stmt_service = select(Service).filter(Service.id == service_id)
        result_service = await session.execute(stmt_service)
        service = result_service.scalars().first()

        if not service:
            results.append({"error": "service_not_found", "service_id": service_id, "message": "Service not found"})
            continue

        # Шаг 3: Проверка статуса заказа
        if order.status == 0:
            results.append({
                "error": "Статус == 0",
                "service_id": service_id,
                "message": "Нельзя добавить услугу к выполненному заказу"
            })
            continue

        # Шаг 4: Проверка на дублирование услуги
        stmt_existing_service = select(OrderService).filter(
            OrderService.order_id == order_service_create.order_id,
            OrderService.service_id == service_id
        )
        result_existing_service = await session.execute(stmt_existing_service)
        existing_service = result_existing_service.scalars().first()

        if existing_service:
            results.append({
                "error": "Повтороное добавление услуги",
                "service_id": service_id,
                "message": f"Услуга '{existing_service.service.name}' уже есть в заказе"
            })
            continue

        # Шаг 5: Добавление услуги в OrderService
        order_service = OrderService(service_id=service_id, order_id=order_service_create.order_id)
        session.add(order_service)

        # Шаг 6: Обновление даты окончания заказа
        if order.end_date:
            order.end_date += timedelta(seconds=service.time)
        else:
            order.end_date = order.start_date + timedelta(seconds=service.time)

        session.add(order)
        await session.flush()  # Обновляем объект, чтобы получить id

        results.append({"success": True, "data": order_service})

    await session.commit()

    # Обновляем состояние заказа и услуг
    await session.refresh(order)

    for result in results:
        if "data" in result:
            await session.refresh(result["data"])

    return results

async def get_order_service(session: AsyncSession, order_service_id: int) -> OrderService:
    stmt = select(OrderService).filter(OrderService.id == order_service_id)
    result = await session.execute(stmt)
    order_service = result.scalars().first()
    if not order_service:
        raise ValueError("OrderService not found")
    return order_service

async def get_order_services(
    session: AsyncSession,
    orders: list[OrderService],
    order_id: Optional[int] = None,
    sort_by: Optional[str] = "id",
    order: Optional[str] = "asc"
) -> Sequence[OrderService]:
    order_services = orders

    if order_id is not None:
        order_services = [service for service in order_services if service.order_id == order_id]

    if sort_by:

        if not hasattr(OrderService, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")

        reverse = order == "desc"
        order_services = sorted(order_services, key=lambda service: getattr(service, sort_by), reverse=reverse)

    return order_services

async def update_order_service(session: AsyncSession, order_service_id: int, order_service_update: OrderServiceUpdate) -> OrderService:
    stmt = select(OrderService).filter(OrderService.id == order_service_id)
    result = await session.execute(stmt)
    order_service = result.scalars().first()
    if not order_service:
        raise ValueError("OrderService not found")

    for key, value in order_service_update.dict(exclude_unset=True).items():
        setattr(order_service, key, value)

    await session.commit()
    await session.refresh(order_service)
    return order_service

async def delete_order_service(session: AsyncSession, order_service_id: int) -> OrderService:
    stmt = select(OrderService).filter(OrderService.id == order_service_id)
    result = await session.execute(stmt)
    order_service = result.scalars().first()
    if not order_service:
        raise ValueError("Запись в OrderService не найдена")

    await session.delete(order_service)
    await session.commit()
    return order_service

# async def create_order_service(session: AsyncSession, order_service_create: OrderServiceCreate) -> OrderService:
#     # Step 1: Extract order by order_id
#     stmt_order = select(Order).filter(Order.id == order_service_create.order_id)
#     result_order = await session.execute(stmt_order)
#     order = result_order.scalars().first()
#
#     if not order:
#         logger.error(f"Order with id {order_service_create.order_id} not found.")
#         raise HTTPException(status_code=404, detail="Order not found")
#
#     # Step 2: Extract service by service_id
#     stmt_service = select(Service).filter(Service.id == order_service_create.service_id)
#     result_service = await session.execute(stmt_service)
#     service = result_service.scalars().first()
#
#     if not service:
#         logger.error(f"Service with id {order_service_create.service_id} not found.")
#         raise HTTPException(status_code=404, detail="Service not found")
#
#     # Step 3: Check if the order is in progress (status != 0)
#     if order.status == 0:
#         # Check if the order already has services
#         stmt_existing_order_service = select(OrderService).filter(OrderService.order_id == order_service_create.order_id)
#         result_existing_order_service = await session.execute(stmt_existing_order_service)
#         existing_order_service = result_existing_order_service.scalars().first()
#
#         if existing_order_service:
#             logger.error(f"Cannot add service to order with status 0. Order ID: {order_service_create.order_id}")
#             raise HTTPException(status_code=400, detail="Cannot add service to order with status 0")
#         else:
#             logger.info(f"Order with ID {order_service_create.order_id} has no services yet. Proceeding to add new service.")
#
#     # Step 4: Check if the service already exists in the order
#     stmt_existing_service = select(OrderService).filter(
#         OrderService.order_id == order_service_create.order_id,
#         OrderService.service_id == order_service_create.service_id
#     )
#     result_existing_service = await session.execute(stmt_existing_service)
#     existing_service = result_existing_service.scalars().first()
#
#     if existing_service:
#         service_name = existing_service.service.name
#         logger.error(f"Service '{service_name}' already exists in this order.")
#         raise HTTPException(status_code=400, detail=f"This service '{service_name}' already exists in the order.")
#
#     # Step 5: Create the new OrderService
#     order_service = OrderService(**order_service_create.dict())
#     session.add(order_service)
#
#     # Step 6: Update the order's end_date based on the service's time
#     if order.end_date:
#         order.end_date += timedelta(seconds=service.time)
#         logger.info(f"Order end_date updated to {order.end_date} after adding service.")
#     else:
#         order.end_date = order.start_date + timedelta(seconds=service.time)
#         logger.info(f"Order end_date set to {order.end_date} after adding service.")
#
#     # Step 7: Commit the changes to the session
#     session.add(order)
#
#     # Step 8: Perform the commit and refresh the order and order_service objects
#     await session.commit()
#
#     # Refresh the objects after commit to get the latest data
#     await session.refresh(order)
#     await session.refresh(order_service)
#
#     logger.info(f"Order with ID {order_service_create.order_id} updated successfully.")
#     logger.info(f"New order_service created with ID {order_service.id}.")
#
#     return order_service