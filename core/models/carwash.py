from datetime import timedelta, datetime
from typing import Optional

import pytz
from pydantic import validator, root_validator
from pytz import timezone
from sqlalchemy import String, Column, Integer, ForeignKey, DateTime, select, event, Boolean
from sqlalchemy.orm import relationship
from .base import Base

statuses = {0: "processing", 1: "completed"}

LOCAL_TIMEZONE = timezone("Asia/Krasnoyarsk")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    cars = relationship("Car", back_populates="brand")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    model = Column(String(100))

    brand = relationship("Brand", back_populates="cars")
    customer_cars = relationship("Customer_Car", back_populates="car")




class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    time = Column(Integer)
    order_services = relationship("OrderService",back_populates="service")

    def to_response(self):
        """
        Преобразует объект Service в словарь для ответа API.
        """

        price_rub = self.convert_price(self.price)
        time_min = self.convert_time(self.time)
        return {
            "id": self.id,
            "name": self.name,
            "price": {
                "minValue": self.price,
                "maxValue": price_rub,
                "format": f"{price_rub} руб."
            },
            "time": {
                "second": self.time,
                "minute": time_min
            },
        }

    def convert_price(self, price):
        return price // 100  # Конвертация цены

    def convert_time(self, time):
        return time // 60  # Конвертация времени


class OrderService(Base):
    __tablename__ = "order_service"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    service = relationship("Service",back_populates="order_services")
    order = relationship("Order", back_populates="order_services")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    administrator_id = Column(Integer, ForeignKey("user.id"))
    customer_car_id = Column(Integer, ForeignKey("customer_cars.id"))
    employee_id = Column(Integer, ForeignKey("user.id"))
    status = Column(Integer)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    notified = Column(Boolean, default=False)
    order_services = relationship("OrderService", back_populates="order")
    administrator = relationship("User", foreign_keys=[administrator_id], back_populates="orders_administrator")
    employee = relationship("User", foreign_keys=[employee_id], back_populates="orders_employee")
    customer_car = relationship("Customer_Car", foreign_keys=[customer_car_id], back_populates="orders")

    @validator("status")
    def validate_status(cls, value):
        if value not in statuses.values():
            raise ValueError("Invalid status. Allowed values are 0 (processing) or 1 (completed).")
        return value

    @validator("end_date")
    def validate_dates(cls, end_date, values):
        start_date = values.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("End date must be after start date.")
        return end_date


class Customer_Car(Base):
    __tablename__ = "customer_cars"
    id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    customer_id = Column(Integer, ForeignKey("user.id"))
    year = Column(Integer)
    number = Column(String(100))

    car = relationship("Car", back_populates="customer_cars")
    customer = relationship("User", back_populates="customer_cars")
    orders = relationship("Order", back_populates="customer_car")







