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
)
from db.schemas import (
    user_schema as user_schema,
    category_schema as category_schema,
)

load_dotenv()

oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/login')

JWT_SECRET = os.getenv("JWT_SECRET")


async def get_budget_by_name(
    db: orm.Session,
    name: str
):
    """
    Get a category by name
    """
    return db.query(category_model.Category).filter(category_model.Category.name == name).first()


async def create_budget(
    db: orm.Session,
    user: user_schema.User,
    budget: category_schema.CategoryCreate,
):
    """
    Create a new category if doesn't exist
    """
    db_budget = await get_budget_by_name(db, budget.name)
    if db_budget:
        raise fastapi.HTTPException(
            status_code=400,
            detail='Category already registered'
        )

    budget_object = category_model.Category(
        name=budget.name,
        user_id=user.id,
    )
    db.add(budget_object)
    db.commit()
    db.refresh(budget_object)
    return budget_object


# async def get_categories(
#     db: orm.Session,
#     user: user_schema.User,
#     skip: int = 0,
#     limit: int = 100,
# ):
#     """
#     Get all categories
#     """
#     return db.query(category_model.Category).filter(category_model.Category.user_id == user.id).offset(skip).limit(limit).all()


# async def update_category(
#     db: orm.Session,
#     user: user_schema.User,
#     category_id: int,
#     category: category_schema.CategoryUpdate,
# ):
#     """
#     Update a category
#     """
#     db_category = db.query(category_model.Category).filter(category_model.Category.id == category_id).first()
#     if not db_category:
#         raise fastapi.HTTPException(
#             status_code=404,
#             detail='Category not found'
#         )
#     if db_category.user_id != user.id:
#         raise fastapi.HTTPException(
#             status_code=403,
#             detail='Not enough permissions'
#         )

#     db_category.name = category.name
#     db.commit()
#     db.refresh(db_category)
#     return db_category


# async def delete_category(
#     db: orm.Session,
#     user: user_schema.User,
#     category_id: int,
# ):
#     """
#     Delete a category
#     """
#     db_category = db.query(category_model.Category).filter(category_model.Category.id == category_id).first()
#     if not db_category:
#         raise fastapi.HTTPException(
#             status_code=404,
#             detail='Category not found'
#         )
#     if db_category.user_id != user.id:
#         raise fastapi.HTTPException(
#             status_code=403,
#             detail='Not enough permissions'
#         )

#     db.delete(db_category)
#     db.commit()
#     return db_category
