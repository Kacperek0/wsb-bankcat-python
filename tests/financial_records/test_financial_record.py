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
async def test_financial_records():
    async with AsyncClient(app=app, base_url='http://test') as ac:
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

        post_create_second_category_response = await ac.post('/api/categories', json={
            'name': 'Test Category 2',
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert post_create_second_category_response.status_code == 200
        assert 'name' in post_create_second_category_response.json()
        assert 'id' in post_create_second_category_response.json()

        get_categories_response = await ac.get('/api/categories', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100})
        assert get_categories_response.status_code == 200
        assert 'name' in get_categories_response.json()[0]
        assert 'id' in get_categories_response.json()[0]
        assert get_categories_response.json()[0]['name'] == 'Test Category'
        assert get_categories_response.json()[0]['id'] == post_categories_response.json()['id']

        category_id = get_categories_response.json()[0]['id']
        second_category_id = get_categories_response.json()[1]['id']

        post_financial_records_response = await ac.post('/api/financial-record', json={
            'date': '2023-01-01',
            'amount': 100,
            'category_id': category_id,
            'description': 'Test Financial Record',
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert post_financial_records_response.status_code == 200
        assert 'date' in post_financial_records_response.json()
        assert 'amount' in post_financial_records_response.json()
        assert 'category' in post_financial_records_response.json()
        assert 'description' in post_financial_records_response.json()
        assert 'id' in post_financial_records_response.json()

        get_financial_records_response = await ac.get('/api/financial-record', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100})
        assert get_financial_records_response.status_code == 200

        get_financial_record_response = await ac.get(f'/api/financial-record', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100, 'query': 'Test'})

        assert get_financial_record_response.status_code == 200
