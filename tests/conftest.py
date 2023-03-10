import sys
import pytest
import pdb as pdb

sys.path.append('src')
from db.models.user import User
from db.models.category import Category
from db.models.budget import Budget
from db.models.financial_record import FinancialRecord
from db.models.token import Token


@pytest.fixture(autouse=True)
def create_dummy_user():

    from tests.conf_test_db import override_database_session
    database = next(override_database_session())

    database.query(FinancialRecord).delete()
    database.query(Budget).delete()
    database.query(Category).delete()
    database.query(Token).delete()
    database.query(User).delete()
    # user = database.query(User).filter(User.email == 'test-user@example.com').first()
    # if user:
        # categories = database.query(Category).filter(Category.user_id == user.id).all()
        # if categories:
            # for category in categories:
                # database.delete(category)

        # Delete user
        # database.delete(user)
    database.commit()
    # Tu da się zrobi tak, ze na końcu się dropnie.

