import pytest
import pdb as pdb

from httpx import AsyncClient

from tests.conf_test_db import app

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

        # TODO: Fix this test, None category_id is not working
        # post_non_category_financial_records_response = await ac.post('/api/financial-record', json={
        #     'date': '2023-01-01',
        #     'amount': 150,
        #     'category_id': None,
        #     'description': 'Test Financial Record1'
        # }, headers={'Authorization': f'Bearer {bearer}'})
        # assert post_non_category_financial_records_response.status_code == 200
        # assert 'date' in post_non_category_financial_records_response.json()
        # assert 'amount' in post_non_category_financial_records_response.json()
        # assert 'category_id' in post_non_category_financial_records_response.json()
        # assert 'description' in post_non_category_financial_records_response.json()
        # assert 'id' in post_non_category_financial_records_response.json()

        get_financial_records_response = await ac.get('/api/financial-record', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100})
        assert get_financial_records_response.status_code == 200
        assert 'date' in get_financial_records_response.json()[0]
        assert 'amount' in get_financial_records_response.json()[0]
        # assert 'category' in get_financial_records_response.json()[0]
        assert 'description' in get_financial_records_response.json()[0]
        assert 'id' in get_financial_records_response.json()[0]
        assert get_financial_records_response.json()[0]['date'] == '2023-01-01'

        financial_record_id = get_financial_records_response.json()[0]['id']

        get_financial_record_response = await ac.get(f'/api/financial-record', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100, 'query': 'Test'})

        assert get_financial_record_response.status_code == 200
        assert 'date' in get_financial_record_response.json()[0]
        assert 'amount' in get_financial_record_response.json()[0]
        # assert 'category' in get_financial_record_response.json()[0]
        assert 'description' in get_financial_record_response.json()[0]
        assert 'id' in get_financial_record_response.json()[0]

        put_financial_record_response = await ac.put(f'/api/financial-record/{financial_record_id}', headers={'Authorization': f'Bearer {bearer}'},
        json={
            'date': '2023-01-01',
            'amount': 200,
            'category_id': category_id,
            'description': 'Test Financial Record'
        })
        assert put_financial_record_response.status_code == 200
        assert 'date' in put_financial_record_response.json()
        assert 'amount' in put_financial_record_response.json()
        assert 'category' in put_financial_record_response.json()
        assert 'description' in put_financial_record_response.json()
        assert 'id' in put_financial_record_response.json()

        # Change category_id to second category
        put_financial_record_response = await ac.put(f'/api/financial-record/{financial_record_id}', headers={'Authorization': f'Bearer {bearer}'},
        json={
            'date': '2023-01-01',
            'amount': 200,
            'category_id': second_category_id,
            'description': 'Test Financial Record'
        })
        assert put_financial_record_response.status_code == 200
        assert 'date' in put_financial_record_response.json()
        assert 'amount' in put_financial_record_response.json()
        assert 'category' in put_financial_record_response.json()
        assert 'description' in put_financial_record_response.json()
        assert 'id' in put_financial_record_response.json()

        delete_financial_record_response = await ac.delete(f'/api/financial-record/{financial_record_id}', headers={'Authorization': f'Bearer {bearer}'})
        assert delete_financial_record_response.status_code == 200

        delete_category_response = await ac.delete(f'/api/categories/{category_id}', headers
        ={'Authorization': f'Bearer {bearer}'})
        assert delete_category_response.status_code == 200
