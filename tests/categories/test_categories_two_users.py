import pytest
import pdb as pdb

from httpx import AsyncClient

from tests.conf_test_db import app
from tests.conf_test_db import override_database_session

from src.db.services.user_service import get_user_by_email, create_new_token, verify_user

users = ('test-user@example.com', 'test-user2@example.com')
test_user_name = 'Test'
test_user_surname = 'User'
test_user_password = 'Test-Passw0rd!'

@pytest.mark.asyncio
async def test_categories():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        for test_user_email in users:
            await ac.post('/api/register', json={
                'email': test_user_email,
                'name': test_user_name,
                'surname': test_user_surname,
                'hashed_password': test_user_password,
            })

            db_session = next(override_database_session())
            # Activate user
            user = await get_user_by_email(db_session, test_user_email)
            token = await create_new_token(db_session, user.id, 'register')
            await verify_user(db_session, user.email, token.token)

            login_response = await ac.post('/api/login', data={
                'username': test_user_email,
                'password': test_user_password
            }, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'})

            bearer = login_response.json()['access_token']

            post_categories_response = await ac.post('/api/categories', json={
                'name': 'Test Category',
            }, headers={'Authorization': f'Bearer {bearer}'})
            assert post_categories_response.status_code == 200
            assert 'name' in post_categories_response.json()
            assert 'id' in post_categories_response.json()
