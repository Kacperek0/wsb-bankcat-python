import jwt as jwt
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security

from dotenv import load_dotenv

import os

import random
import string

import db.database as db
from db.services.database_session import database_session
from db.models import user as user_model
from db.schemas import user_schema as user_schema
from db.models import token as token_model

load_dotenv()

oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/login')

JWT_SECRET = os.getenv("JWT_SECRET")

async def get_token_by_token(
    db: orm.Session,
    token: str,
    action: str
):
    """
    Get a token by token
    """
    return db.query(
        token_model.Token
    ).filter(
        token_model.Token.token == token
    ).filter(
        token_model.Token.action == action
    ).first()

async def create_new_token(
    db: orm.Session,
    user_id: int,
    action: str
):
    model = token_model.Token(
        user_id=user_id,
        token=''.join(random.choices(string.ascii_uppercase + string.digits, k=16)),
        action=action
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    return model