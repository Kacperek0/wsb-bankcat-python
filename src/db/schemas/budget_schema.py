import pydantic
from fastapi import Query

"""
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    value = sql.Column(sql.Integer, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'))
"""


class _BudgetBase(pydantic.BaseModel):
    category_id: int


class BudgetCreate(_BudgetBase):
    value: int = Query(..., gt=0)
    class Config:
        orm_mode = True


class BudgetUpdate(_BudgetBase):
    value: int = Query(..., gt=0)
    category_id: int

    class Config:
        orm_mode = True

class Budget(_BudgetBase):
    id: int
    value: int

    class Config:
        orm_mode = True
