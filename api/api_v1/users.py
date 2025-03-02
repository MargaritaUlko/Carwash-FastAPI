from fastapi import APIRouter, Depends

from api.api_v1.fastapi_users import fastapi_users
from core.config import settings
from core.schemas.user import (
    UserRead,
    UserUpdate, UserCreate,
)

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)

# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)
