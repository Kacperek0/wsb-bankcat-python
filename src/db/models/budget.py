import sqlalchemy as sql
import sqlalchemy.orm as orm

from db.models import (
    user,
    category
)

from db.database import Base


class Budget(Base):
    __tablename__ = 'budgets'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    value = sql.Column(sql.Integer, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'))

    user = orm.relationship('User', foreign_keys=[user_id])
    categories = orm.relationship('Category', foreign_keys=[category_id])
