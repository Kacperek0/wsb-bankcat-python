import pytest
import pdb as pdb

from httpx import AsyncClient

from tests.conf_test_db import app

test_user_email = 'test-user@example.com'
test_user_name = 'Test'
test_user_surname = 'User'
test_user_password = 'Test-Passw0rd!'

@pytest.mark.asyncio
async def test_categories():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        await ac.post('/api/register', json={
            'email': test_user_email,
            'name': test_user_name,
            'surname': test_user_surname,
            'hashed_password': test_user_password,
        })

        login_response = await ac.post('/api/login', data={
            'username': test_user_email,
            'password': test_user_password
        }, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'})

        bearer = login_response.json()['access_token']

        for i in range(0, 10):
            post_categories_response = await ac.post('/api/categories', json={
                'name': f'Test Category {i}',
            }, headers={'Authorization': f'Bearer {bearer}'})
            assert post_categories_response.status_code == 200
            assert 'name' in post_categories_response.json()
            assert 'id' in post_categories_response.json()

        get_categories_response = await ac.get('/api/categories', headers={'Authorization': f'Bearer {bearer}'}, params={'skip': 5, 'limit': 5})
        assert get_categories_response.status_code == 200
        assert len(get_categories_response.json()) == 5
        assert get_categories_response.json()[0]['name'] == 'Test Category 5'
        assert get_categories_response.json()[4]['name'] == 'Test Category 9'
