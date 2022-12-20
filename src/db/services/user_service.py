import jwt as jwt
import passlib.hash as hash
import sqlalchemy.orm as orm
import fastapi as fastapi
import fastapi.security as security

from dotenv import load_dotenv

import os

import db.database as db
from db.services.database_session import database_session
from db.models import user as user_model
from db.schemas import user_schema as user_schema

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
