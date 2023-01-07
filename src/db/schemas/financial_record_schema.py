import pydantic
import datetime

from db.schemas.category_schema import Category

"""
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    date = sql.Column(sql.Date, index=True)
    amount = sql.Column(sql.Float, index=True)
    description = sql.Column(sql.String, index=True)
    category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'))
"""


class _FinancialRecordBase(pydantic.BaseModel):
    date: datetime.date
    amount: float
    description: str

class FinancialRecordCreate(_FinancialRecordBase):
    category_id: int | None # Category might be filled in later

    class Config:
        orm_mode = True

class FinancialRecordUpdate(_FinancialRecordBase):
    category_id: int | None

    class Config:
        orm_mode = True

class FinancialRecordMassCategoryAssignment(pydantic.BaseModel):
    category_id: int
    financial_record_ids: list[int]

    class Config:
        orm_mode = True

class FinancialRecord(_FinancialRecordBase):
    id: int
    category: Category | None

    class Config:
        orm_mode = True

class FinancialRecordDelete(pydantic.BaseModel):
    id: int

    class Config:
        orm_mode = True
