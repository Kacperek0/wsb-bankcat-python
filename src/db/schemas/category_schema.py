import pydantic

"""
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    name = sql.Column(sql.String, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    budget_id = sql.Column(sql.Integer, sql.ForeignKey('budgets.id'))
"""


class _CategoryBase(pydantic.BaseModel):
    name: str
    # user_id: int
    # budget_id: int


class CategoryCreate(_CategoryBase):

    class Config:
        orm_mode = True


class CategoryUpdate(_CategoryBase):

    class Config:
        orm_mode = True


class Category(_CategoryBase):
    id: int

    class Config:
        orm_mode = True
