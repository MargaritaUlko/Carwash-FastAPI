from http.client import HTTPException
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.authentication.dependecy import check_access
from core.config import settings
from core.models import db_helper, Car, Brand, User
from core.schemas.carwash import (
    CarRead,
    CarCreate,
    CarUpdate,
)
from crud.carwash import car as car_crud
from crud.carwash.car import get_cars

car_router = APIRouter(
    prefix=settings.api.v1.cars,
    tags=["Cars"],
)

# @car_router.get("", response_model=list[CarRead])
# async def get_cars(
#     session: AsyncSession = Depends(db_helper.session_getter),
#     limit: int = 10,
# ):
#     cars = await car_crud.get_cars(session=session, limit=limit)
#     return cars
@car_router.get("/car/{car_id}", response_model=CarRead)
async def get_car(
    car_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))

):
    car = await car_crud.get_car(session=session, car_id=car_id)
    return car


# Получение автомобиля по id

# @car_router.get("", response_model=list[CarRead])
# async def get_cars(
#     session: AsyncSession = Depends(db_helper.session_getter),
#     limit: int = Query(10, ge=1),  # Параметр для ограничения количества элементов
#     page: int = Query(1, ge=1),  # Параметр для текущей страницы
#     brand: Optional[str] = None,  # Фильтрация по бренду
#     sort_by: Optional[str] = Query("id", regex="^(id|model)$"),  # Поле для сортировки
#     order: Optional[str] = Query("asc", regex="^(asc|desc)$"),  # Направление сортировки
# ):
#     # Рассчитываем offset на основе страницы
#     offset = (page - 1) * limit
#
#     # Базовый запрос
#     stmt = select(Car).options(joinedload(Car.brand)).offset(offset).limit(limit)
#
#     # Фильтрация по бренду
#     if brand:
#         stmt = stmt.join(Brand).filter(Brand.name.ilike(f"%{brand}%"))  # Фильтр по имени бренда
#
#     # Сортировка
#     if sort_by:
#         column = getattr(Car, sort_by)
#         stmt = stmt.order_by(column.asc() if order == "asc" else column.desc())
#
#     # Выполнение запроса
#     result = await session.execute(stmt)
#     cars = result.scalars().all()
#
#     return cars
@car_router.get("", response_model=list[CarRead])
async def get_cars_api(
        session: AsyncSession = Depends(db_helper.session_getter),  # Получаем сессию для работы с БД
        limit: int = Query(10, ge=1),  # Параметр для ограничения количества элементов
        page: int = Query(1, ge=1),  # Параметр для текущей страницы
        brand: Optional[str] = None,  # Фильтрация по бренду
        sort_by: Optional[str] = Query("id", regex="^(id|model)$"),  # Поле для сортировки
        order: Optional[str] = Query("asc", regex="^(asc|desc)$"),  # Направление сортировки
        user:   User = Depends(check_access([1]))
):

    cars = await get_cars(session)


    if brand:
        cars = [car for car in cars if brand.lower() in car.brand.name.lower()]


    if sort_by:
        if not hasattr(Car, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")

        # Сортируем данные для всей коллекции
        reverse = order == "desc"
        cars = sorted(cars, key=lambda car: getattr(car, sort_by), reverse=reverse)

    # Пагинация
    offset = (page - 1) * limit
    cars_paginated = cars[offset:offset + limit]

    return cars_paginated
# Создание нового автомобиля
@car_router.post("", response_model=CarRead, status_code=status.HTTP_201_CREATED)
async def create_car(
    car_create: CarCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    car = await car_crud.create_car(session=session, car_create=car_create)
    return car

# Обновление информации об автомобиле
@car_router.put("/{car_id}", response_model=CarRead)
async def update_car(
    car_update: CarUpdate,
    car_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    car = await car_crud.update_car(
        session=session, car_id=car_id, car_update=car_update
    )
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

# Удаление автомобиля
@car_router.delete("/{car_id}")
async def delete_car(
    car_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    deleted = await car_crud.delete_car(session=session, car_id=car_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Car deleted"}
