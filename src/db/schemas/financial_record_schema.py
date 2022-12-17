import pydantic

"""
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    date = sql.Column(sql.Date, index=True)
    amount = sql.Column(sql.Float, index=True)
    description = sql.Column(sql.String, index=True)
    category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'))
"""


class _FinancialRecordBase(pydantic.BaseModel):
    date: str
    amount: float
    description: str


class FinancialRecordCreate(_FinancialRecordBase):

    class Config:
        orm_mode = True
        

class User(_FinancialRecordBase):
    id: int
    category_id: int

    class Config:
        orm_mode = True
