from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from core.models import db_helper
from core.schemas.company import (
    CompanyRead,
    CompanyCreate,
)
from crud import company as company_crud

router = APIRouter(
    prefix=settings.api.v1.company,
    tags=["Company"],
)


@router.get("", response_model=list[CompanyRead])
async def get_company(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    companies = await company_crud.get_all_company(session=session)
    return companies


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    company_create: CompanyCreate,
):
    company = await company_crud.create_company(
        session=session,
        company_create=company_create,
    )
    return company
