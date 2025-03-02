from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Service
from core.schemas.carwash import ServiceUpdate, ServiceCreate


async def create_service(session: AsyncSession, service_create: ServiceCreate) -> Service:
    service = Service(
        name=service_create.name,
        price=service_create.price,
        time=service_create.time,
    )
    session.add(service)
    await session.commit()
    await session.refresh(service)
    return service

async def get_service(session: AsyncSession, service_id: int) -> Service:
    stmt = select(Service).filter(Service.id == service_id)
    result = await session.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise ValueError("Service not found")
    return service

async def get_services(session: AsyncSession) -> Sequence[Service]:
    stmt = select(Service)
    result = await session.execute(stmt)
    return result.scalars().all()

async def update_service(session: AsyncSession, service_id: int, service_update: ServiceUpdate) -> Service:
    stmt = select(Service).filter(Service.id == service_id)
    result = await session.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise ValueError("Service not found")

    for key, value in service_update.dict(exclude_unset=True).items():
        setattr(service, key, value)

    await session.commit()
    await session.refresh(service)
    return service

async def delete_service(session: AsyncSession, service_id: int) -> Service:
    stmt = select(Service).filter(Service.id == service_id)
    result = await session.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise ValueError("Service not found")

    await session.delete(service)
    await session.commit()
    return service