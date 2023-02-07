import pytest
import pdb as pdb

from httpx import AsyncClient

from tests.conf_test_db import app
from tests.conf_test_db import override_database_session

from src.db.services.user_service import get_user_by_email, create_new_token, verify_user

test_user_email = 'test-user@example.com'
test_user_name = 'Test'
test_user_surname = 'User'
test_user_password = 'Test-Passw0rd!'

@pytest.mark.asyncio
async def test_all_users():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.post('/api/register', json={
            'email': test_user_email,
            'name': test_user_name,
            'surname': test_user_surname,
            'hashed_password': test_user_password,
        })
        assert response.status_code == 200
        assert 'email' in response.json()
        assert 'name' in response.json()
        assert 'surname' in response.json()
        assert 'hashed_password' in response.json()

        too_short_password = '123'
        too_short_password_response = await ac.post('/api/register', json={
            'email': test_user_email,
            'name': test_user_name,
            'surname': test_user_surname,
            'hashed_password': too_short_password,
        })
        assert too_short_password_response.status_code == 422
        assert 'detail' in too_short_password_response.json()
        assert 'hashed_password' in too_short_password_response.json()['detail'][0]['loc']
        assert 'ensure this value has at least 8 characters' in too_short_password_response.json()['detail'][0]['msg']
        assert 'value_error.any_str.min_length' in too_short_password_response.json()['detail'][0]['type']

        login_unauthorized_response = await ac.post('/api/login', data={
            'username': test_user_email,
            'password': test_user_password,
        }, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'})
        assert login_unauthorized_response.status_code == 401
        assert 'detail' in login_unauthorized_response.json()

        db_session = next(override_database_session())
        # Activate user
        user = await get_user_by_email(db_session, test_user_email)
        token = await create_new_token(db_session, user.id, 'register')
        await verify_user(db_session, user.email, token.token)

        login_response = await ac.post('/api/login', data={
            'username': test_user_email,
            'password': test_user_password
        }, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'})
        assert login_response.status_code == 200
        assert 'access_token' in login_response.json()
        assert 'token_type' in login_response.json()


        me_response = await ac.get('/api/users/me',
        headers={'Authorization': f'Bearer {login_response.json()["access_token"]}'})
        assert me_response.status_code == 200
        assert 'email' in me_response.json()
        assert 'name' in me_response.json()
        assert 'surname' in me_response.json()
        assert 'id' in me_response.json()
