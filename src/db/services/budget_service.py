import jwt as jwt
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security

from dotenv import load_dotenv

import os

import db.database as db
from db.services.database_session import database_session
from db.models import (
    user as user_model,
    category as category_model,
    budget as budget_model,
)
from db.schemas import (
    user_schema as user_schema,
    category_schema as category_schema,
    budget_schema as budget_schema,
)

load_dotenv()

oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/login')

JWT_SECRET = os.getenv("JWT_SECRET")


async def get_budget_by_category_id(
    db: orm.Session,
    category_id: str,
    user_id: int,
):
    """
    Get a category by name
    """
    return db.query(budget_model.Budget).filter(
        budget_model.Budget.category_id == category_id,
        budget_model.Budget.user_id == user_id,
    ).first()


async def create_budget(
    db: orm.Session,
    user: user_schema.User,
    budget: budget_schema.BudgetCreate,
):
    """
    Create a new category if doesn't exist
    """
    db_budget = await get_budget_by_category_id(db, budget.category_id, user.id)
    if db_budget:
        raise fastapi.HTTPException(
            status_code=400,
            detail='Budget already registered'
        )

    budget_object = budget_model.Budget(
        category_id=budget.category_id,
        user_id=user.id,
        value=budget.value,
    )
    db.add(budget_object)
    db.commit()
    db.refresh(budget_object)
    return budget_object


async def get_budget(
    db: orm.Session,
    user: user_schema.User,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all categories
    """

    budgets = db.query(budget_model.Budget).filter(
        budget_model.Budget.user_id == user.id,
    ).offset(skip).limit(limit).all()
    return budgets


async def update_budget(
    db: orm.Session,
    user: user_schema.User,
    budget_id: int,
    budget: budget_schema.BudgetUpdate,
):
    """
    Update a category
    """
    db_budget = db.query(budget_model.Budget).filter(
        budget_model.Budget.id == budget_id,
        budget_model.Budget.user_id == user.id,
    ).first()
    db_budget_in_current_category = db.query(budget_model.Budget).filter(
        budget_model.Budget.category_id == budget.category_id,
        budget_model.Budget.user_id == user.id,
    ).first()

    if db_budget_in_current_category and db_budget_in_current_category.id != budget_id:
        raise fastapi.HTTPException(
            status_code=400,
            detail='Budget already registered in this category'
        )
    if not db_budget:
        raise fastapi.HTTPException(
            status_code=404,
            detail='Budget not found'
        )
    if db_budget.user_id != user.id:
        raise fastapi.HTTPException(
            status_code=403,
            detail='Not enough permissions'
        )

    db_budget.value = budget.value
    db_budget.category_id = budget.category_id
    db.commit()
    db.refresh(db_budget)
    return db_budget


async def delete_budget(
    db: orm.Session,
    user: user_schema.User,
    budget_id: int,
):
    """
    Delete a category
    """
    db_budget = db.query(budget_model.Budget).filter(
        budget_model.Budget.id == budget_id,
        budget_model.Budget.user_id == user.id,
    ).first()
    if not db_budget:
        raise fastapi.HTTPException(
            status_code=404,
            detail='Budget not found'
        )
    if db_budget.user_id != user.id:
        raise fastapi.HTTPException(
            status_code=403,
            detail='Not enough permissions'
        )

    db.delete(db_budget)
    db.commit()
    return db_budget
