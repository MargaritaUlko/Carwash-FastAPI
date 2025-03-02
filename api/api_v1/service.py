from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.authentication.dependecy import check_access
from core.config import settings
from core.models import db_helper, Service, User
from core.schemas.carwash import ServiceCreate, ServiceRead, ServiceUpdate, Price, Time
from crud.carwash import service as service_crud

service_router = APIRouter(
    prefix=settings.api.v1.services,
    tags=["Services"],
)

@service_router.get("", response_model=list[ServiceRead])
async def api_get_services(
    session: AsyncSession = Depends(db_helper.session_getter),
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    sort_by: Optional[str] = Query("id", regex="^(id|name|price)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    services = await service_crud.get_services(session=session)

    if sort_by:
        if not hasattr(Service, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {sort_by}")

        reverse = order == "desc"
        services = sorted(services, key=lambda service: getattr(service, sort_by), reverse=reverse)

    offset = (page - 1) * limit
    services_paginated = services[offset:offset + limit]

    return [ServiceRead.from_orm(service) for service in services_paginated]




@service_router.get("/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    service = await service_crud.get_service(session=session, service_id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service.to_response()


@service_router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_create: ServiceCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    print(service_create)
    print(service_create.price)
    print(service_create.time)
    service = await service_crud.create_service(session=session, service_create=service_create)
    return service.to_response()



@service_router.put("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_update: ServiceUpdate,
    service_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    service = await service_crud.update_service(
        session=session, service_id=service_id, service_update=service_update
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@service_router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(check_access([1]))
):
    deleted = await service_crud.delete_service(session=session, service_id=service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted"}
