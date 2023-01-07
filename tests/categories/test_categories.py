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

        post_categories_response = await ac.post('/api/categories', json={
            'name': 'Test Category',
        }, headers={'Authorization': f'Bearer {bearer}'})
        assert post_categories_response.status_code == 200
        assert 'name' in post_categories_response.json()
        assert 'id' in post_categories_response.json()

        get_categories_response = await ac.get('/api/categories', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100})
        assert get_categories_response.status_code == 200
        assert 'name' in get_categories_response.json()[0]
        assert 'id' in get_categories_response.json()[0]
        assert get_categories_response.json()[0]['name'] == 'Test Category'
        assert get_categories_response.json()[0]['id'] == post_categories_response.json()['id']

        category_id = get_categories_response.json()[0]['id']

        put_categories_response = await ac.put(f'/api/categories/{category_id}', json={ 'name': 'Test Category 2' }, headers={'Authorization': f'Bearer {bearer}'})
        assert put_categories_response.status_code == 200
        assert 'name' in put_categories_response.json()
        assert 'id' in put_categories_response.json()
        assert put_categories_response.json()['name'] == 'Test Category 2'

        get_categories_after_put_response = await ac.get('/api/categories', headers={'Authorization': f'Bearer {bearer}'},
        params={'skip': 0, 'limit': 100})
        assert get_categories_after_put_response.status_code == 200
        assert 'name' in get_categories_after_put_response.json()[0]
        assert 'id' in get_categories_after_put_response.json()[0]
        assert get_categories_after_put_response.json()[0]['name'] == 'Test Category 2'
        assert get_categories_after_put_response.json()[0]['id'] == post_categories_response.json()['id']

        delete_categories_response = await ac.delete(f'/api/categories/{post_categories_response.json()["id"]}', headers={'Authorization': f'Bearer {bearer}'})
        assert delete_categories_response.status_code == 200
        assert 'name' in delete_categories_response.json()
        assert 'id' in delete_categories_response.json()
        assert delete_categories_response.json()['name'] == 'Test Category 2'

        get_categories_after_delete_response = await ac.get('/api/categories', headers={'Authorization': f'Bearer {bearer}'}, params={'skip': 0, 'limit': 100})
        assert get_categories_after_delete_response.status_code == 200
        assert len(get_categories_after_delete_response.json()) == 0
