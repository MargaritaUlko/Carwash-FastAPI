from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Company
from core.schemas.company import CompanyCreate


async def get_all_company(
    session: AsyncSession,
) -> Sequence[Company]:
    stmt = select(Company).order_by(Company.id)
    result = await session.scalars(stmt)
    return result.all()


async def create_company(
    session: AsyncSession,
    company_create: CompanyCreate,
) -> Company:
    company = Company(**company_create.model_dump())
    session.add(company)
    await session.commit()
    # await session.refresh(company)
    return company
