# import sqlalchemy as sql
# import sqlalchemy.orm as orm

# from db.models import (
#     user,
#     category
# )

# from db.database import Base


# class FinancialRecord(Base):
#     __tablename__ = 'financial_records'

#     id = sql.Column(sql.Integer, primary_key=True, index=True)
#     user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
#     date = sql.Column(sql.Date, index=True)
#     amount = sql.Column(sql.Float, index=True)
#     description = sql.Column(sql.String, index=True)
#     category_id = sql.Column(sql.Integer, sql.ForeignKey('categories.id'))


#     user = orm.relationship('User', back_populates='financial_records' ,foreign_keys=[user_id], remote_side=id)
#     category = orm.relationship('Category', back_populates='financial_records', foreign_keys=[category_id], remote_side=id)
