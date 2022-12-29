import jwt as jwt
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security

from dotenv import load_dotenv

import os

import db.database as db
from db.services.database_session import database_session
from db.models import category as category_model
from db.models import budget as budget_model
from db.models import user as user_model
from db.models import financial_record as financial_record_model
from db.schemas import dashboard_schema as dashboard_schema
from db.schemas import user_schema as user_schema

load_dotenv()

oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/login')

JWT_SECRET = os.getenv("JWT_SECRET")

async def get_dashboard(
    db: orm.Session,
    user: user_model.User
):
    """
    Get a dashboard
    """
    user_categories = db.query(category_model.Category).filter(category_model.Category.user_id == user.id).all()

    user_budgets = db.query(budget_model.Budget).filter(budget_model.Budget.user_id == user.id).all()

    return dashboard_schema.Dashboard(
        user_id=user.id,
        categories=user_categories,
        budgets=user_budgets
    )


async def get_dashboard_with_spendings(
    db: orm.Session,
    user: user_model.User
):
    """
    Get a dashboard with financial records
    """
    user_categories = db.query(category_model.Category).filter(category_model.Category.user_id == user.id).all()

    results = []

    for category in user_categories:
        budget = db.query(budget_model.Budget).filter(budget_model.Budget.category_id == category.id).first()
        financial_records = db.query(financial_record_model.FinancialRecord).filter(financial_record_model.FinancialRecord.category_id == category.id).all()
        spendings = lambda financial_records: sum([financial_record.amount for financial_record in financial_records])

        results.append({
            "category": category,
            "budget": budget,
            "financial_records": financial_records,
            "spendings": spendings(financial_records)
        })

    return dashboard_schema.DashboardWithSpendings(
        user_id=user.id,
        categories_enriched=results
    )
