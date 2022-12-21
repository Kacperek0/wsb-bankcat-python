import pytest
import pdb as pdb

from httpx import AsyncClient

from tests.conf_test_db import app

test_user_email = 'test-user@example.com'
test_user_name = 'Test'
test_user_surname = 'User'
test_user_password = 'test-password'

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
        # TODO: Should not return password
        assert 'hashed_password' in response.json()

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
