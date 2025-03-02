from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.api_v1.fastapi_users import fastapi_users
from core.authentication.dependecy import check_access
from core.config import settings
from core.models import db_helper, Customer_Car, User, Car
from core.schemas.carwash import CustomerCarCreate, CustomerCarRead, CustomerCarUpdate, CustomerCarBase
from crud.carwash import customer_car as customer_car_crud
from crud.carwash.customer_car import get_customer_cars, get_customer_cars

customer_car_router = APIRouter(
    prefix=settings.api.v1.customer_cars,
    tags=["Customer_cars"],
)

# Получение списка всех автомобилей клиентов
@customer_car_router.get("", response_model=list[CustomerCarRead])
async def api_get_customer_cars(
    session: AsyncSession = Depends(db_helper.session_getter),  # Получаем сессию для работы с БД
    limit: int = Query(10, ge=1),  # Параметр для ограничения количества элементов
    page: int = Query(1, ge=1),  # Параметр для текущей страницы
    sort_by: Optional[str] = Query("id", regex="^(id|car_model|customer_name)$"),  # Поле для сортировки
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),  # Направление сортировки
    car_model: Optional[str] = None,  # Новый параметр для фильтрации по модели машины
    user: User = Depends(check_access([1]))  # Получаем текущего пользователя
):

    customer_cars = await get_customer_cars(
        session=session,
        user_id=user.id,
        car_model=car_model,
        sort_by=sort_by,
        order=order
    )

    offset = (page - 1) * limit
    customer_cars_paginated = customer_cars[offset:offset + limit]

    return customer_cars_paginated


# Получение информации о автомобиле клиента по id
@customer_car_router.get("/{customer_car_id}", response_model=CustomerCarBase)
async def get_customer_car(
    customer_car_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(fastapi_users.current_user())
):

    customer_car = await customer_car_crud.get_customer_car(session=session, customer_car_id=customer_car_id)

    if not customer_car:
        raise HTTPException(status_code=404, detail="CustomerCar not found")


    if customer_car.customer_id != user.id:
        raise HTTPException(status_code=403, detail="Access forbidden: Customer car does not belong to the user")

    return customer_car


# Создание нового автомобиля клиента
@customer_car_router.post("", response_model=CustomerCarBase, status_code=status.HTTP_201_CREATED)
async def create_customer_car(
    customer_car_create: CustomerCarCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    customer_car = await customer_car_crud.create_customer_car(session=session, customer_car_create=customer_car_create)
    return customer_car


# Обновление существующего автомобиля клиента
@customer_car_router.put("/{customer_car_id}", response_model=CustomerCarUpdate)
async def update_customer_car(
    customer_car_update: CustomerCarUpdate,  # Параметр с телом запроса
    customer_car_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    customer_car = await customer_car_crud.update_customer_car(
        session=session, customer_car_id=customer_car_id, customer_car_update=customer_car_update  # Передаем объект
    )
    if not customer_car:
        raise HTTPException(status_code=404, detail="CustomerCar not found")
    return customer_car



# Удаление автомобиля клиента
@customer_car_router.delete("/{customer_car_id}")
async def delete_customer_car(
    customer_car_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    deleted = await customer_car_crud.delete_customer_car(session=session, customer_car_id=customer_car_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CustomerCar not found")
    return {"message": "CustomerCar deleted"}
