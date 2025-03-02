
from typing import TYPE_CHECKING
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from pydantic import validator
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.carwash import Order
from .base import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
ROLES = {1: "admin", 2: "worker", 3: "client"}

class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=50), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(length=50), nullable=True)
    username: Mapped[str] = mapped_column(String(length=50), nullable=True)
    is_send_notify: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[int] = mapped_column(Integer, default=3)
    customer_cars = relationship("Customer_Car", back_populates="customer")
    orders_administrator = relationship("Order", back_populates="administrator", foreign_keys=[Order.administrator_id])
    orders_employee = relationship("Order", back_populates="employee", foreign_keys=[Order.employee_id])
    @validator("status")
    def validate_status(cls, value):
        if value not in ROLES.values():
            raise ValueError("Invalid role. Allowed values are 1 or 2 or 3.")
        return value
    # def get_role_name(self) -> str:
    #     """Получить имя роли на основе role_id."""
    #     return self.ROLES.get(self.role_id, "unknown")
    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXVkIjoiZmFzdGFwaS11c2Vyczp2ZXJpZnkiLCJleHAiOjE3MzUwMzU1MTZ9.Kgk5iDzfhwwyL9d-KLVeemJve8w7IguY8aJMVin4IOM

