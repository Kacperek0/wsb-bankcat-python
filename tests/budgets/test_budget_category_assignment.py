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

        for i in range(0, 3):
            await ac.post('/api/categories', json={
                'name': f'Test Category {i}',
            }, headers={'Authorization': f'Bearer {bearer}'})

        get_filled_categories_response = await ac.get('/api/categories', headers={'Authorization': f'Bearer {bearer}'}, params={'skip': 0, 'limit': 100})

        filled_category_ids = [category['id'] for category in get_filled_categories_response.json()]

        assert len(filled_category_ids) == 3

        create_first_budget_response = await ac.post('/api/budget', json={
            'category_id': filled_category_ids[0],
            'value': 100
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert create_first_budget_response.status_code == 200
        assert 'category_id' in create_first_budget_response.json()
        assert 'value' in create_first_budget_response.json()
        assert create_first_budget_response.json()['category_id'] == filled_category_ids[0]

        reassign_first_budget_response = await ac.put(f'/api/budget/{create_first_budget_response.json()["id"]}', json={
            'category_id': filled_category_ids[1],
            'value': 100
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert reassign_first_budget_response.status_code == 200
        assert 'category_id' in reassign_first_budget_response.json()
        assert 'value' in reassign_first_budget_response.json()
        assert reassign_first_budget_response.json()['category_id'] == filled_category_ids[1]

        create_second_budget_response = await ac.post('/api/budget', json={
            'category_id': filled_category_ids[0],
            'value': 100
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert create_second_budget_response.status_code == 200
        assert 'category_id' in create_second_budget_response.json()
        assert 'value' in create_second_budget_response.json()
        assert create_second_budget_response.json()['category_id'] == filled_category_ids[0]

        reassign_second_budget_response = await ac.put(f'/api/budget/{create_second_budget_response.json()["id"]}', json={
            'category_id': filled_category_ids[1],
            'value': 100
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert reassign_second_budget_response.status_code == 400

        create_budget_for_assigned_category_response = await ac.post('/api/budget', json={
            'category_id': filled_category_ids[1],
            'value': 100
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert create_budget_for_assigned_category_response.status_code == 400

