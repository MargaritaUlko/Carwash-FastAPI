# Pydantic Schemas
from datetime import datetime
from http.client import HTTPException
from typing import Optional, Any, Literal, List

import pytz
from pydantic import BaseModel, root_validator, Field, field_validator
from sqlalchemy.future import select

from core.models import Order
# Подсчет общего времени и цены, правильное создание услуги, в order service услуги должны добваляться массивом, scheduler
"""BRANDS"""
class BrandBase(BaseModel):
    name: str

    class Config:
        orm_mode = True
        from_attributes = True
class BrandCreate(BrandBase):
    pass

class BrandRead(BrandBase):
    id: int
class BrandUpdate(BaseModel):
    name: Optional[str] = None



"""CARS"""

class CarBase(BaseModel):
    model: str
    brand_id: int

class CarCreate(CarBase):
    pass
class CarUpdate(CarBase):
    pass
class CarRead(BaseModel):
    id: int
    model: str
    brand: BrandBase


    class Config:
        orm_mode = True
        from_attributes = True


class CarsResponse(BaseModel):
    cars: list[CarRead]
    pagination: dict




""""SERVICES"""
class ServiceBase(BaseModel):
    pass

class Price(BaseModel):
    minValue: int
    maxValue: int = Field(0)
    format: str = Field("")

class Time(BaseModel):
    second: int
    minute: int = Field(0)

class ServiceCreate(BaseModel):
    name: str
    price: int
    time: int

class ServiceRead(BaseModel):
    id: int
    name: str
    price: Price
    time: Time

    @classmethod
    def from_orm(cls, obj: Any) -> "ServiceRead":
        price = Price(
            minValue=obj.price,
            maxValue=obj.convert_price(obj.price),
            format=f"{obj.convert_price(obj.price)} руб."
        )
        time = Time(
            second=obj.time,
            minute=obj.convert_time(obj.time)
        )

        return cls(id=obj.id, name=obj.name, price=price, time=time)

    class Config:
        orm_mode = True
        from_attributes = True
class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    time: Optional[int] = None




"""ORDER_SERVICES"""

class OrderServiceBase(BaseModel):
    service_id: int
    order_id: int

class OrderServiceCreate(BaseModel):
    service_ids: List[int]
    order_id: int

class OrderServiceRead(OrderServiceBase):
    id: int
class OrderServiceUpdate(BaseModel):

    service_id: Optional[int] = None
    order_id: Optional[int] = None





""""ORDERS"""
utc_now = datetime.now(pytz.utc)
krasnoyarsk_tz = pytz.timezone("Asia/Krasnoyarsk")

class OrderBase(BaseModel):
    id: int
    administrator_id: int
    customer_car_id: int
    employee_id: int
    status: int
    start_date: datetime = utc_now.astimezone(krasnoyarsk_tz)
    end_date: datetime = utc_now.astimezone(krasnoyarsk_tz)

class OrderCreate(BaseModel):
    administrator_id: int
    customer_car_id: int
    employee_id: int
    status: int
    start_date: datetime = utc_now.astimezone(krasnoyarsk_tz)
    end_date: datetime = utc_now.astimezone(krasnoyarsk_tz)
    status: Literal[1] = 1

class OrderRead(BaseModel):
    id: int
    status: int
    start_date: datetime
    end_date: datetime
    administrator_id: int
    customer_car_id: int
    employee_id: int
    services: list[ServiceRead]
    car: Optional[str]
    employee_name: Optional[str]
    administrator_name: Optional[str]
    total_price: int  # Итоговая сумма в рублях
    total_time_minutes: int
    @classmethod
    async def from_orm(cls, obj: Order) -> "OrderRead":
        services = [
            ServiceRead.from_orm(service.service)
            for service in obj.order_services
        ]
        car_model = obj.customer_car.car.model if obj.customer_car and obj.customer_car.car else None
        employee_name = (
            f"{obj.employee.first_name} {obj.employee.last_name}"
            if obj.employee else None
        )
        administrator_name = (
            f"{obj.administrator.first_name} {obj.administrator.last_name}"
            if obj.administrator else None
        )

        start_date = obj.start_date
        end_date = obj.end_date

        total_price = sum(service.service.convert_price(service.service.price) for service in obj.order_services)
        total_time_minutes = sum(service.service.convert_time(service.service.time) for service in obj.order_services)

        if start_date.tzinfo is None:
            start_date = pytz.utc.localize(start_date)
        if end_date.tzinfo is None:
            end_date = pytz.utc.localize(end_date)

        start_date_krasnoyarsk = start_date.astimezone(krasnoyarsk_tz)
        end_date_krasnoyarsk = end_date.astimezone(krasnoyarsk_tz)

        return cls(
            id=obj.id,
            status=obj.status,
            start_date=start_date_krasnoyarsk,
            end_date=end_date_krasnoyarsk,
            administrator_id=obj.administrator_id,
            customer_car_id=obj.customer_car_id,
            employee_id=obj.employee_id,
            services=services,
            car=car_model,
            employee_name=employee_name,
            administrator_name=administrator_name,
            total_price=total_price,
            total_time_minutes=total_time_minutes,
        )
class OrderUpdate(BaseModel):
    administrator_id: Optional[int] = None
    customer_car_id: Optional[int] = None
    employee_id: Optional[int] = None

# class CustomerCarRead(CustomerCarBase):
#     id: int


"""USERS"""
class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        orm_mode = True


"""CUSTOMER_CARS"""
class CustomerCarBase(BaseModel):
    car_id: int
    customer_id: int
    year: int
    number: str

class CustomerCarCreate(CustomerCarBase):
    pass

class CustomerCarRead(BaseModel):
    id: int
    year: int
    number: str
    car: CarRead
    customer: UserRead

    class Config:
        orm_mode = True

class CustomerCarUpdate(BaseModel):
    customer_id: int
    year: int
    number: str











