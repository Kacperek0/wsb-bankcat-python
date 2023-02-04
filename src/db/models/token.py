import sqlalchemy as sql
import sqlalchemy.orm as orm

from db.models import (
    user,
)

from db.database import Base


class Token(Base):
    __tablename__ = 'tokens'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    token = sql.Column(sql.String, unique=True, index=True)
    action = sql.Column(sql.String, index=True)
    created_at = sql.Column(sql.DateTime, default=sql.func.now())


    user = orm.relationship('User', foreign_keys=[user_id])
