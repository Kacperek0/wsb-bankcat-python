import sqlalchemy as sql
import sqlalchemy.orm as orm

from db.models import (
    user,
    budget
)

from db.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    name = sql.Column(sql.String, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    budget_id = sql.Column(sql.Integer, sql.ForeignKey('budgets.id'))

    user = orm.relationship('User', foreign_keys=[user_id])
    # financial_records = orm.relationship('FinancialRecord', back_populates='category', foreign_keys=[id], remote_side=id)
    budget = orm.relationship('Budget', foreign_keys=[budget_id])
