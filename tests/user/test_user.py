import sys
import pytest
import pdb as pdb

from httpx import AsyncClient

# pdb.set_trace()
from db.services import user_service
from tests.conf_test_db import app
from tests.conftest import create_dummy_user


@pytest.mark.asyncio
async def test_all_users():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        user_access_token = await user_service.create_token(create_dummy_user)
        pdb.set_trace()
        response = await ac.get('/api/users/me', headers={'Authorization': f'Bearer {user_access_token}'})
        assert response.status_code == 200
        assert response.json() == []


