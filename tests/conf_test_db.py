import os
import sys

import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm

sys.path.append('src')
from main import (
    app,
    database_session
)

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("TEST_POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("TEST_POSTGRES_PASSWORD")
POSTGRES_SERVER = os.getenv("TEST_POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("TEST_POSTGRES_PORT")
DATABASE_NAME = os.getenv("TEST_DATABASE_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{DATABASE_NAME}"

engine = sql.create_engine(
    SQLALCHEMY_DATABASE_URL
)

TestingSessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_database_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[database_session.database_session] = override_database_session
