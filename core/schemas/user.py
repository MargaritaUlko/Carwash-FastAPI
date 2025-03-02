from typing import Optional

from fastapi_users import schemas
from pydantic import validator

ROLES = {1: "admin", 2: "worker", 3: "client"}

class UserRead(schemas.BaseUser[int]):
    username: str

    first_name: str
    last_name: str
    patronymic: Optional[str]
    is_send_notify: bool
    role_id: int

class UserCreate(schemas.BaseUserCreate):
    username: str
    first_name: str
    last_name: str
    patronymic: Optional[str]
    is_send_notify: bool = False
    role_id: int = 3

    @validator("role_id")
    def validate_role(cls, value):
        if value not in ROLES:
            raise ValueError(f"Некорректная роль: {value}. Допустимые значения: {list(ROLES.keys())}")
        if value in [1, 2]:
            raise ValueError(f"Некорректная роль: {value}. Недостаточно прав")
        return value


class UserUpdate(schemas.BaseUserUpdate):
    username: str

    first_name: str
    last_name: str
    patronymic: Optional[str]
    is_send_notify: bool
    role_id: int