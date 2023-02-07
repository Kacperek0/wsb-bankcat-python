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
async def test_categories():
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

        category_id = post_categories_response.json().get('id')

        post_budgets_response = await ac.post('/api/budget', json={
            'category_id': category_id,
            'value': 100
        }, headers={'Authorization' : f'Bearer {bearer}'})

        assert post_budgets_response.status_code == 200
        assert 'category_id' in post_budgets_response.json()
        assert 'value' in post_budgets_response.json()
        assert post_budgets_response.json()['category_id'] == category_id

        get_budgets_response = await ac.get('/api/budget', headers={'Authorization' : f'Bearer {bearer}'}, params={'limit': 100, 'skip': 0})
        assert get_budgets_response.status_code == 200
        assert len(get_budgets_response.json()) == 1
        assert get_budgets_response.json()[0]['category_id'] == category_id
        assert get_budgets_response.json()[0]['value'] == 100

        budget_id = get_budgets_response.json()[0]['id']

        put_budgets_response = await ac.put(f'/api/budget/{budget_id}', json={
            'category_id': category_id,
            'value': 200
        }, headers={'Authorization' : f'Bearer {bearer}'})
        assert put_budgets_response.status_code == 200
        assert 'category_id' in put_budgets_response.json()
        assert 'value' in put_budgets_response.json()
        assert put_budgets_response.json()['category_id'] == category_id
        assert put_budgets_response.json()['value'] == 200

        get_budgets_response = await ac.get('/api/budget', headers={'Authorization' : f'Bearer {bearer}'}, params={'limit': 100, 'skip': 0})
        assert get_budgets_response.status_code == 200
        assert len(get_budgets_response.json()) == 1
        assert get_budgets_response.json()[0]['category_id'] == category_id
        assert get_budgets_response.json()[0]['value'] == 200

        budget_id = get_budgets_response.json()[0]['id']

        delete_budgets_response = await ac.delete(f'/api/budget/{budget_id}', headers={'Authorization' : f'Bearer {bearer}'})
        assert delete_budgets_response.status_code == 200
        assert 'category_id' in delete_budgets_response.json()
        assert 'value' in delete_budgets_response.json()
        assert delete_budgets_response.json()['category_id'] == category_id
        assert delete_budgets_response.json()['value'] == 200

