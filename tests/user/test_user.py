import sys
import pytest
import pdb as pdb

from httpx import AsyncClient

# pdb.set_trace()
from db.services import user_service
from tests.conf_test_db import app


@pytest.mark.asyncio
async def test_all_users():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.post('/api/register', json={
            'email': 'test-user@example.com',
            'name': 'Test',
            'surname': 'User',
            'hashed_password': 'test-password'
        })
        assert response.status_code == 200
        # assert response.json() == []


