import sqlalchemy as sql
import sqlalchemy.orm as orm

from db.models import (
    user,
    category
)

from db.database import Base


class FinancialRecord(Base):
    __tablename__ = 'financial_records'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    date = sql.Column(sql.Date, index=True)
    amount = sql.Column(sql.Float, index=True)
    description = sql.Column(sql.String, index=True)
    category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'), nullable=True)


    user = orm.relationship('User', foreign_keys=[user_id])
    category = orm.relationship('Category', foreign_keys=[category_id])
