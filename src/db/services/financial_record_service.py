import jwt as jwt
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security
import datetime

from dotenv import load_dotenv

import os

import db.database as db
from db.services.database_session import database_session
from db.models import (
    user as user_model,
    category as category_model,
    budget as budget_model,
    financial_record as financial_record_model,
)
from db.schemas import (
    user_schema as user_schema,
    category_schema as category_schema,
    budget_schema as budget_schema,
    financial_record_schema as financial_record_schema,
)

load_dotenv()

oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/login')

JWT_SECRET = os.getenv("JWT_SECRET")


async def get_financial_record_by_id(
    db: orm.Session,
    financial_record_id: str,
    user_id: int,
):
    """
    Get a category by name
    """
    return db.query(financial_record_model.FinancialRecord).filter(
        financial_record_model.FinancialRecord.id == financial_record_id,
        financial_record_model.FinancialRecord.user_id == user_id,
    ).first()


async def check_uniqueness(
    db: orm.Session,
    user: user_schema.User,
    financial_record: financial_record_schema.FinancialRecordCreate,
) -> bool:
    """
    Check if the financial record is unique
    """
    db_financial_record = db.query(financial_record_model.FinancialRecord).filter(
        financial_record_model.FinancialRecord.user_id == user.id,
        financial_record_model.FinancialRecord.category_id == financial_record.category_id,
        financial_record_model.FinancialRecord.date == financial_record.date,
        financial_record_model.FinancialRecord.description == financial_record.description,
        financial_record_model.FinancialRecord.amount == financial_record.amount,
    ).first()

    if db_financial_record:
        return False
    else:
        return True


async def check_category(
    db: orm.Session,
    user: user_schema.User,
    financial_record: financial_record_schema.FinancialRecordCreate,
) -> bool:
    """
    Check if the category exists
    """
    db_category = db.query(category_model.Category).filter(
        category_model.Category.id == financial_record.category_id,
        category_model.Category.user_id == user.id,
    ).first()

    if db_category:
        return True
    else:
        return False


async def create_financial_record(
    db: orm.Session,
    user: user_schema.User,
    financial_record: financial_record_schema.FinancialRecordCreate,
):
    """
    Create a new financial record
    """

    is_unique = await check_uniqueness(db, user, financial_record)

    does_category_exist = await check_category(db, user, financial_record)

    if not does_category_exist:
        raise fastapi.HTTPException(
            status_code=400,
            detail='Category does not exist, please create it first or assign null.'
        )

    if is_unique:
        financial_record_object = financial_record_model.FinancialRecord(
            user_id=user.id,
            category_id=financial_record.category_id,
            date=financial_record.date,
            description=financial_record.description,
            amount=financial_record.amount,
        )

        db.add(financial_record_object)
        db.commit()
        db.refresh(financial_record_object)

        return financial_record_object

    else:
        raise fastapi.HTTPException(
            status_code=400,
            detail='Financial record already registered'
        )


async def get_financial_records(
    db: orm.Session,
    user: user_schema.User,
    skip: int = 0,
    limit: int = 100,
    query: str = None,
):
    """
    Get all financial records
    """
    if query:
        return db.query(financial_record_model.FinancialRecord).filter(
            financial_record_model.FinancialRecord.user_id == user.id,
            financial_record_model.FinancialRecord.description.like(f'%{query}%'),
        ).offset(skip).limit(limit).all()
    else:
        return db.query(financial_record_model.FinancialRecord).filter(
            financial_record_model.FinancialRecord.user_id == user.id,
        ).offset(skip).limit(limit).all()


async def get_financial_records_by_category(
    db: orm.Session,
    user: user_schema.User,
    category_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all financial records by category
    """
    if category_id == 0:
        return db.query(financial_record_model.FinancialRecord).filter(
            financial_record_model.FinancialRecord.user_id == user.id
        ).offset(skip).limit(limit).all()
    else:
        return db.query(financial_record_model.FinancialRecord).filter(
            financial_record_model.FinancialRecord.user_id == user.id,
            financial_record_model.FinancialRecord.category_id == category_id,
        ).offset(skip).limit(limit).all()


async def get_financial_records_by_date(
    db: orm.Session,
    user: user_schema.User,
    date: datetime.date,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all financial records by date
    """
    if date == None:
        return db.query(financial_record_model.FinancialRecord).filter(
            financial_record_model.FinancialRecord.user_id == user.id,
        ).offset(skip).limit(limit).all()
    else:
        return db.query(financial_record_model.FinancialRecord).filter(
            financial_record_model.FinancialRecord.user_id == user.id,
            financial_record_model.FinancialRecord.date == date,
        ).offset(skip).limit(limit).all()


async def put_financial_record(
    db: orm.Session,
    user: user_schema.User,
    financial_record_id: str,
    financial_record: financial_record_schema.FinancialRecordUpdate,
):
    """
    Update a financial record
    """
    db_financial_record = await get_financial_record_by_id(
        db,
        financial_record_id,
        user.id,
    )

    if db_financial_record:
        db_financial_record.category_id = financial_record.category_id
        db_financial_record.date = financial_record.date
        db_financial_record.description = financial_record.description
        db_financial_record.amount = financial_record.amount

        db.commit()
        db.refresh(db_financial_record)

        return db_financial_record

    else:
        raise fastapi.HTTPException(
            status_code=404,
            detail='Financial record not found'
        )


async def delete_financial_record(
    db: orm.Session,
    user: user_schema.User,
    financial_record_id: str,
):
    """
    Delete a financial record
    """
    db_financial_record = await get_financial_record_by_id(
        db,
        financial_record_id,
        user.id,
    )

    if db_financial_record:
        db.delete(db_financial_record)
        db.commit()

        return db_financial_record

    else:
        raise fastapi.HTTPException(
            status_code=404,
            detail='Financial record not found'
        )
