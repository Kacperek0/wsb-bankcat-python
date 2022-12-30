import jwt as jwt
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security
from fastapi import UploadFile, File
import datetime
import csv
import re
from PyPDF2 import PdfReader
import pydantic

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

from db.services import (
    category_service as category_service
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

    if not does_category_exist and financial_record.category_id != None:
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


async def import_mbank_csv(
    db: orm.Session,
    user: user_schema.User,
    csv_file: UploadFile = File(...),
    header_row: int = 0,
):
    """
    Import a csv file
    """
    csv_file_content = await csv_file.read()

    csv_file_content = csv_file_content.decode('windows-1250')

    csv_file_content = csv_file_content.splitlines()

    csv_file_content = csv.reader(csv_file_content, delimiter=';')

    results = []

    for i in range(header_row):
        next(csv_file_content)

    for row in csv_file_content:
        try:
            date = row[0]
            description = row[1]
            category = row[3]
            amount = row[4]
            amount = amount.replace(',', '.').split(' ')[0]
            amount = float(amount) * 100
            if amount < 0:
                amount = abs(int(amount))

                check_category = await category_service.get_category_by_name(db, category, user.id)

                if check_category:
                    category_id = check_category.id
                else:
                    category_id = await category_service.create_category(db, user, category_schema.CategoryCreate(name=category))
                    category_id = category_id.id

                financial_record = financial_record_schema.FinancialRecordCreate(
                    date=date,
                    category_id=category_id,
                    description=description,
                    amount=amount,
                )
                results.append(financial_record)

                try:
                    status_code = await create_financial_record(db, user, financial_record)
                    print(status_code.id)
                except fastapi.HTTPException:
                    continue
            else:
                continue
        except IndexError:
            break

    return results


async def import_pkobp_pdf(
    db: orm.Session,
    user: user_schema.User,
    pdf_file: UploadFile = File(...),
):
    """
    Import a pdf file
    """
    reader = PdfReader(pdf_file.file)
    text = reader.pages[0].extract_text()
    text = text.splitlines()
    usable_data = []
    is_usable = False
    for line in text:
        if line == 'Data waluty Opis operacji':
            is_usable = True
            continue
        if is_usable:
            usable_data.append(line)


    process_data = []
    for line in usable_data:
        if re.match(r'[0-9]{2}\.[0-9]{2}\.[0-9]{4}', line):
            process_data.append(line)

    # Loop through data, group every 2 lines and create a list of tuples
    results = []
    for i in range(0, len(process_data), 2):
        results.append((process_data[i], process_data[i+1]))

    financial_records = []
    # Loop through tuples and split them into date, description and amount
    for i in range(len(results)):
        first_row = results[i][0].split(' ')
        second_row = results[i][1].split(' ')
        date = first_row[0]
        date = date.replace('.', '-')
        # Reverse date to YYYY-MM-DD
        date = date.split('-')
        date = date[2] + '-' + date[1] + '-' + date[0]
        description = ' '.join([x for x in second_row[1:] if x])
        for item in first_row:
            if re.match(r'-[0-9]{1,3},[0-9]{2}', item):
                amount = str(item)
                amount = amount.replace(',', '.')
                amount = float(amount) * 100
        if amount < 0:
            amount = abs(int(amount))
            financial_record = financial_record_schema.FinancialRecordCreate(
                date=date,
                category_id=None,
                description=description,
                amount=amount
            )
            financial_records.append(financial_record)
            try:
                status_code = await create_financial_record(db, user, financial_record)
                print(status_code.id)
            except fastapi.HTTPException:
                continue
        else:
            continue

    return financial_records


async def import_santander_csv(
    db: orm.Session,
    user: user_schema.User,
    csv_file: UploadFile = File(...),
):
    csv_file_content = await csv_file.read()

    csv_file_content = csv_file_content.decode('utf-8')

    csv_file_content = csv_file_content.splitlines()

    csv_file_content = csv.reader(csv_file_content, delimiter=',')

    next(csv_file_content)

    results = []

    for row in csv_file_content:
        date = row[0]
        date = date.split('-')
        date = date[2] + '-' + date[1] + '-' + date[0]
        description = row[2] + ' ' + row[3]
        amount = row[5]
        amount = amount.replace(',', '.')
        amount = float(amount) * 100
        if amount < 0:
            amount = abs(int(amount))
            financial_record = financial_record_schema.FinancialRecordCreate(
                date=date,
                category_id=None,
                description=description,
                amount=amount
            )
            results.append(financial_record)
            try:
                status_code = await create_financial_record(db, user, financial_record)
                print(status_code.id)
            except fastapi.HTTPException:
                continue

    return results


async def import_pekaosa_csv(
    db: orm.Session,
    user: user_schema.User,
    csv_file: UploadFile = File(...),
):
    csv_file_content = await csv_file.read()

    csv_file_content = csv_file_content.decode('utf-8')

    csv_file_content = csv_file_content.splitlines()

    csv_file_content = csv.reader(csv_file_content, delimiter=';')

    next(csv_file_content)

    results = []

    for row in csv_file_content:
        date = row[0]
        date = date.split('.')
        date = date[2] + '-' + date[1] + '-' + date[0]
        description = row[2] + ' ' + row[3] + ' ' + row[6]
        amount = row[7]
        amount = amount.replace(' ', '')
        amount = amount.replace(',', '.')
        amount = float(amount) * 100
        if amount < 0:
            amount = abs(int(amount))
            financial_record = financial_record_schema.FinancialRecordCreate(
                date=date,
                category_id=None,
                description=description,
                amount=amount
            )
            results.append(financial_record)
            try:
                status_code = await create_financial_record(db, user, financial_record)
                print(status_code.id)
            except fastapi.HTTPException:
                continue

    return results

