import jwt as jwt
import random
import string
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security
import datetime

from dotenv import load_dotenv

import os

import db.database as db
from db.services.database_session import database_session
from db.models import user as user_model
from db.models import token as token_model
from db.schemas import user_schema as user_schema
from db.services.token_service import get_token_by_token

load_dotenv()

oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/login')

JWT_SECRET = os.getenv("JWT_SECRET")

async def get_user_by_email(
    db: orm.Session,
    email: str
):
    """
    Get a user by email
    """
    return db.query(user_model.User).filter(user_model.User.email == email).first()


async def create_user(
    db: orm.Session,
    user: user_schema.UserCreate
):
    """
    Create a user
    """
    user_object = user_model.User(
        email=user.email,
        name=user.name,
        surname=user.surname,
        hashed_password=hash.bcrypt.hash(user.hashed_password),
    )
    db.add(user_object)
    db.commit()
    db.refresh(user_object)

    token_object = token_model.Token(
        token=''.join(random.choices(string.ascii_uppercase + string.digits, k=16)),
        user_id=user_object.id,
        action='register'
    )
    db.add(token_object)
    db.commit()
    db.refresh(token_object)

    return user_object


async def authenticate_user(
    db: orm.Session,
    email: str,
    password: str
):
    """
    Authenticate a user
    """
    user = await get_user_by_email(db, email)
    if not user:
        return False

    if not user.verify_password(password):
        return False

    if user.verified_at is None:
        return False

    return user


async def create_token(
    user: user_model.User,
):
    """
    Create a token
    """
    user_object = user_schema.User.from_orm(user)

    token = jwt.encode(
        user_object.dict(),
        JWT_SECRET
    )

    return dict(access_token=token, token_type='bearer')


async def get_current_user(
    db: orm.Session = fastapi.Depends(database_session),
    token: str = fastapi.Depends(oauth2_schema)
):
    """
    Get current user
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = db.query(user_model.User).filter(user_model.User.id == payload['id']).first()
    except:
        raise fastapi.HTTPException(
            status_code=403,
            detail='Invalid token'
        )

    return user_schema.User.from_orm(user)


async def verify_user(
    db: orm.Session,
    email: str,
    token: str
):
    """
    """
    user = await get_user_by_email(db, email)
    if not user:
        return False

    if user.verified_at is not None:
        return False

    token = await get_token_by_token(db, token, 'register')
    if not token:
        return False

    if token.user_id != user.id:
        return False

    db.delete(token)
    db.commit()

    user.verified_at = datetime.datetime.now()
    db.commit()
    db.refresh(user)

    return True
