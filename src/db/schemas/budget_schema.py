import pydantic

"""
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    value = sql.Column(sql.Integer, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'))
"""


class _BudgetBase(pydantic.BaseModel):
    value: int
    category_id: int


class BudgetCreate(_BudgetBase):

    class Config:
        orm_mode = True


class Budget(_BudgetBase):
    id: int

    class Config:
        orm_mode = True
