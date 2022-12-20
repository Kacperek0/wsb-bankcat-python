import sys
import pytest
import pdb as pdb

sys.path.append('src')
from db.models.user import User


@pytest.fixture(autouse=True)
def create_dummy_user():

    from tests.conf_test_db import override_database_session
    database = next(override_database_session())

    database.query(User).filter(User.email == 'test-user@example.com').delete()
    database.commit()
    # Tu da się zrobi tak, ze na końcu się dropnie.

