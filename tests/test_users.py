from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.models.users import User



@pytest.mark.asyncio
async def test_get_user_profile(client, db_session):
    # fake_user = User(
    #     cognito_id="fake-cognito-id",
    #     handle="testuser"
    # )
    # db_session.add(fake_user)
    # await db_session.commit()
    headers = {
        "Authorization": "Bearer fake.token.value"
    }
    response = client.get("/api/v1/users/profile",
        headers=headers)
    assert response.status_code == 200
    assert response.json()["handle"] == "testuser"

