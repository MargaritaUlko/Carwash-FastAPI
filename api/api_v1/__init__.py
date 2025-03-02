from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from core.config import settings
from .auth import router as auth_router
from .brand import brand_router
from .car import car_router
from .customer_car import customer_car_router
from .order import order_router
from .order_service import order_service_router
from .service import service_router
from .users import router as users_router
from .company import router as company_router
from .tasks import router as tasks_router
http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)

router.include_router(company_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(tasks_router)
router.include_router(brand_router)
router.include_router(service_router)
router.include_router(car_router)
router.include_router(order_service_router)
router.include_router(order_router)
router.include_router(customer_car_router)

