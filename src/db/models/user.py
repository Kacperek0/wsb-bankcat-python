import sqlalchemy as sql
import sqlalchemy.orm as orm
import passlib.hash as hash

from db.database import Base

from db.models import (
    financial_record,
    category,
    budget
)


class User(Base):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    name = sql.Column(sql.String, index=True)
    surname = sql.Column(sql.String, index=True)
    email = sql.Column(sql.String, unique=True, index=True)
    hashed_password = sql.Column(sql.String)
    verified_at = sql.Column(sql.DateTime, default=None)

    def verify_password(self, password):
        return hash.bcrypt.verify(password, self.hashed_password)
