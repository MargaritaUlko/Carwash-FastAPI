from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import Customer_Car, Car
from core.schemas.carwash import CustomerCarCreate, CustomerCarUpdate


# CRUD Operations for Customer_Car
async def create_customer_car(session: AsyncSession, customer_car_create: CustomerCarCreate) -> Customer_Car:
    customer_car = Customer_Car(**customer_car_create.dict())
    session.add(customer_car)
    await session.commit()
    await session.refresh(customer_car)

    # Подгрузка связанных объектов car и customer
    result = await session.execute(
        select(Customer_Car)
        .options(
            joinedload(Customer_Car.car).joinedload(Car.brand),  # Подгрузка car с brand
            joinedload(Customer_Car.customer)  # Подгрузка customer
        )
        .where(Customer_Car.id == customer_car.id)
    )
    customer_car_with_details = result.scalars().first()
    return customer_car_with_details
# async def get_customer_car(session: AsyncSession, customer_car_id: int) -> Customer_Car:
#     stmt = select(Customer_Car).filter(Customer_Car.id == customer_car_id)
#     result = await session.execute(stmt)
#     customer_car = result.scalars().first()
#     if not customer_car:
#         raise ValueError("CustomerCar not found")
#     return customer_car

async def get_customer_cars(
    session: AsyncSession,
    user_id: int,
    car_model: Optional[str] = None,
    sort_by: Optional[str] = "id",
    order: Optional[str] = "asc"
) -> Sequence[Customer_Car]:
    query = select(Customer_Car).options(
        joinedload(Customer_Car.car).joinedload(Car.brand),
        joinedload(Customer_Car.customer)
    )


    query = query.filter(Customer_Car.customer_id == user_id)


    if car_model:
        query = query.join(Car).filter(Car.model.ilike(f"%{car_model}%"))

    result = await session.execute(query)
    customer_cars = result.scalars().all()

    if sort_by:
        if not hasattr(Customer_Car, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")

        reverse = order == "desc"
        customer_cars = sorted(customer_cars, key=lambda car: getattr(car, sort_by), reverse=reverse)

    return customer_cars



async def update_customer_car(session: AsyncSession, customer_car_id: int, customer_car_update: CustomerCarUpdate) -> Customer_Car:
    stmt = select(Customer_Car).filter(Customer_Car.id == customer_car_id)
    result = await session.execute(stmt)
    customer_car = result.scalars().first()
    if not customer_car:
        raise ValueError("CustomerCar not found")

    for key, value in customer_car_update.dict(exclude_unset=True).items():
        setattr(customer_car, key, value)

    await session.commit()
    await session.refresh(customer_car)
    return customer_car

async def delete_customer_car(session: AsyncSession, customer_car_id: int) -> Customer_Car:
    stmt = select(Customer_Car).filter(Customer_Car.id == customer_car_id)
    result = await session.execute(stmt)
    customer_car = result.scalars().first()
    if not customer_car:
        raise ValueError("CustomerCar not found")

    await session.delete(customer_car)
    await session.commit()
    return customer_car