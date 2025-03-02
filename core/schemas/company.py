from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    foo: int
    bar: int


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int
