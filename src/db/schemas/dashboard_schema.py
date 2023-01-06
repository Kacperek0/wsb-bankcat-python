import datetime
import pydantic

from db.schemas.budget_schema import Budget
from db.schemas.category_schema import Category
from db.schemas.financial_record_schema import FinancialRecord


class _DashboardBase(pydantic.BaseModel):
    user_id: int


class Dashboard(_DashboardBase):
    budgets: list[Budget]
    categories: list[Category]

    class Config:
        orm_mode = True


class DashboardWithFinancialRecords(_DashboardBase):
    categories: list[Category]
    financial_records: list[FinancialRecord]


    class Config:
        orm_mode = True


class DashboardWithSpendings(_DashboardBase):
    categories_enriched: list

    class Config:
        orm_mode = True

class DashboardCategories(pydantic.BaseModel):
    categories: list
    start_date: datetime.date

    class Config:
        orm_mode = True

class DashboardBudget(pydantic.BaseModel):
    budget: list
    start_date: datetime.date

    class Config:
        orm_mode = True
