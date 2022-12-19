import sys
import pytest
import pdb as pdb

sys.path.append('src')
from db.models.user import User


@pytest.fixture(autouse=True)
def create_dummy_user():

    from tests.conf_test_db import override_database_session
    database = next(override_database_session())
    new_user = User(
        email='test-user@example.com',
        name='Test',
        surname='User',
        hashed_password='test-password'
    )

    pdb.set_trace()
    database.add(new_user)
    database.commit()

    yield new_user

    database.query(User).filter(User.email == 'test-user@example.com').delete()
    database.commit()

