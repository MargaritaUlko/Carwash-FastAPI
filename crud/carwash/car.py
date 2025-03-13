from fastapi import Depends, HTTPException
from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import Car, db_helper
from core.schemas.carwash import CarUpdate, CarCreate, CarRead


# CRUD Operations for Car

async def create_car(session: AsyncSession, car_create: CarCreate) -> Car:
    car = Car(**car_create.dict())
    session.add(car)
    await session.commit()
    await session.refresh(car)

    result = await session.execute(
        select(Car)
        .options(joinedload(Car.brand)) 
        .filter(Car.id == car.id)       
    )
    car_with_brand = result.scalars().first()

    return car_with_brand

# async def get_car(session: AsyncSession, car_id: int) -> Car:
#     stmt = select(Car).filter(Car.id == car_id)
#     result = await session.execute(stmt)
#     car = result.scalars().first()
#     if not car:
#         raise ValueError("Car not found")
#     return car
#
# async def get_cars(session: AsyncSession, limit: int) -> Sequence[Car]:
#     stmt = select(Car).limit(limit)
#     result = await session.execute(stmt)
#     return result.scalars().all()
async def get_cars(session: AsyncSession):
    result = await session.execute(
        select(Car).options(joinedload(Car.brand))
    )
    cars = result.scalars().all()
    return cars


async def get_car(session: AsyncSession, car_id: int):
    result = await session.execute(
        select(Car)
        .options(joinedload(Car.brand))
        .where(Car.id == car_id)
    )
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


async def update_car(session: AsyncSession, car_id: int, car_update: CarUpdate) -> Car:
    stmt = select(Car).options(joinedload(Car.brand)).filter(Car.id == car_id)
    result = await session.execute(stmt)
    car = result.scalars().first()

    if not car:
        raise ValueError("Car not found")

    for key, value in car_update.dict(exclude_unset=True).items():
        setattr(car, key, value)

    await session.commit()
    await session.refresh(car)
    return car

async def delete_car(session: AsyncSession, car_id: int) -> Car:
    stmt = select(Car).filter(Car.id == car_id)
    result = await session.execute(stmt)
    car = result.scalars().first()
    if not car:
        raise ValueError("Car not found")

    await session.delete(car)
    await session.commit()
    return car








# async def get_car(session: AsyncSession, car_id: int):
#     result = await session.execute(
#         select(Car)
#         .options(selectinload(Car.brand))  # Ленивое подгрузка бренда, но с подгрузкой через второй запрос
#         .where(Car.id == car_id)
#     )
#     car = result.scalar_one_or_none()
#     return car