
import asyncio
import uuid
from httpx import AsyncClient
import pytest

from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.chatbot import ChatbotCreateRequest, ChatRequest
from app.models.users import User
from app.models.chatbot import Chatbot
from app.services.chatbot import ChatbotService
from app.models.base import Base

@pytest.mark.asyncio
async def test_create_chatbot_with_invalid_user(client, db_session):
    from sqlalchemy.exc import IntegrityError
    from app.models.chatbot import Chatbot
    import uuid

    print(f"Test loop: {asyncio.get_running_loop()}")
    chatbot = Chatbot(
        name="Test Chatbot",
        description="A description of the test chatbot",
        owner_id=uuid.uuid4(),  # Invalid user ID not in the User table
        is_public=True,
        settings={
            "embedding_model": {
                "provider": "openai",
                "name": "text-embedding-3-large",
                "dimensions": 3072
            }
        }
    )
    print(f"Session type: {type(db_session)}")
    db_session.add(chatbot)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

@pytest.mark.asyncio
async def test_create_chatbot_with_valid_user(client, db_session):

    from app.models.chatbot import Chatbot
    fake_user = User(
        cognito_id="fake-cognito-id",
        handle="testuser"
    )
    print(f"Test loop: {asyncio.get_running_loop()}")
    db_session.add(fake_user)
    await db_session.commit()

    chatbot = Chatbot(
        name="Test Chatbot",
        description="A description",
        owner_id=fake_user.id,
        is_public=True,
        settings={
            "embedding_model": {
                "provider": "openai",
                "name": "text-embedding-3-large",
                "dimensions": 3072
            }
        }
    )
    db_session.add(chatbot)
    await db_session.commit()

    result = await db_session.get(Chatbot, chatbot.id)
    assert result is not None
    assert result.name == "Test Chatbot"

@pytest.fixture
async def mock_chatbot(client, db_session):
    """Create a mock chatbot for testing purposes."""
    fake_user = User(
        cognito_id="fake-cognito-id",
        handle="testuser"
    )
    db_session.add(fake_user)
    await db_session.commit()
    
    chatbot_data = {
        "name": "Test Chatbot",
        "description":"A description",
        "is_public": True,
        "settings": {
            "embedding_model": {
                "provider": "openai",
                "name": "text-embedding-3-large",
                "dimensions": 3072
            }
        }
    }
    headers = {
        "Authorization": "Bearer fake.token.value"
    }
    response = client.post(
        "/api/v1/chatbots/",
        json=chatbot_data,
        headers=headers
    )
    assert response.status_code == 200
    return response.json()

# @pytest.mark.asyncio
# async def test_create_chatbot(client, db_session):
#     """Test creating a new chatbot."""
#     fake_user = User(
#         cognito_id="fake-cognito-id",
#         handle="testuser"
#     )
#     print(f"Test loop: {asyncio.get_running_loop()}")
#     db_session.add(fake_user)
#     await db_session.commit()

@pytest.mark.asyncio
async def test_create_chatbot(client, db_session):
    fake_user = User(cognito_id="fake-cognito-id", handle="testuser")
    db_session.add(fake_user)
    await db_session.commit()
    chatbot_data = {
        "name": "Test Chatbot",
        "description":"A description",
        "is_public": True,
        "settings": {
            "embedding_model": {
                "provider": "openai",
                "name": "text-embedding-3-large",
                "dimensions": 3072
            }
        }
    }
    headers = {
        "Authorization": "Bearer fake.token.value"
    }
    response = client.post(
        "/api/v1/chatbots/",
        json=chatbot_data,
        headers=headers 
    )
    print("RESPONSE:", response.status_code, response.text)

    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == chatbot_data["name"]
    assert response.json()["description"] == chatbot_data["description"]
    assert response.json()["is_public"] == chatbot_data["is_public"]

# @pytest.mark.asyncio
# async def test_create_chatbot(client, db_session):
#     headers = {
#         "Authorization": "Bearer fake.token.value"
#     }
#     response = await client.post(
#         "/api/v1/chatbots/",
#         json={
#             "name": "Test Chatbot",
#             "description": "A description",
#             "is_public": True,
#             "settings": {
#                 "embedding_model": {
#                     "provider": "openai",
#                     "name": "text-embedding-3-large",
#                     "dimensions": 3072
#                 }
#             }
#         },
#         headers=headers
#     )

#     assert response.status_code == 200


# def test_get_all_chatbots(client, mock_chatbot):
#     """Test getting all chatbots for the authenticated user."""
#     headers = {
#         "Authorization": "Bearer fake.token.value"
#     }
#     response = client.get("/api/v1/chatbots/",headers=headers )
#     assert response.status_code == 200
#     chatbots = response.json()["chatbots"]
#     assert len(chatbots) > 0
#     assert chatbots[0]["id"] == mock_chatbot["id"]
#     assert chatbots[0]["name"] == mock_chatbot["name"]
#     assert chatbots[0]["description"] == mock_chatbot["description"]


# def test_get_chatbot_by_id(client, mock_chatbot):
#     """Test getting a chatbot by ID."""
#     chatbot_id = mock_chatbot["id"]
#     headers = {
#         "Authorization": "Bearer fake.token.value"
#     }
#     response = client.get(f"/api/v1/chatbots/{chatbot_id}", headers=headers )
#     assert response.status_code == 200
#     assert response.json()["id"] == chatbot_id
#     assert response.json()["name"] == mock_chatbot["name"]


# def test_chat_with_chatbot(client, mock_chatbot):
#     """Test chatting with a chatbot."""
#     chatbot_id = mock_chatbot["id"]
#     message = "Hello, chatbot!"
    
#     chat_request = {
#         "chatbot_id": chatbot_id,
#         "message": message
#     }
#     headers = {
#         "Authorization": "Bearer fake.token.value"
#     }
#     response = client.post(
#         "/api/v1/chatbots/public/chat",
#         json=chat_request,
#         headers=headers 
#     )
    
#     assert response.status_code == 200
#     assert "data" in response.text  # Ensure there's some response text
#     assert "message" in response.json()  # Ensure the response has a message

#     # Since we mock the response, we can check if the chatbot is working as expected
#     assert response.json()["message"] == "Singapore Management University is located at 81 Victoria St, Singapore 188065"


# @pytest.mark.asyncio
# async def test_create_chatbot_with_invalid_data(client):
#     """Test creating a chatbot with invalid data."""
#     # Missing required name field
#     invalid_data = {
#         "description": "A chatbot without a name",
#         "is_public": True
#     }
#     headers = {
#         "Authorization": "Bearer fake.token.value"
#     }
#     response = client.post(
#         "/api/v1/chatbots/",
#         json=invalid_data,
#         headers=headers 
#     )
#     assert response.status_code == 422  # Unprocessable entity
#     assert "name" in response.json()["detail"][0]["loc"]  # Ensure the error points to 'name'


# @pytest.mark.asyncio
# async def test_chat_with_nonexistent_chatbot(client):
#     """Test chatting with a non-existent chatbot."""
#     invalid_chatbot_id = uuid.uuid4()  # Random non-existent ID
#     headers = {
#         "Authorization": "Bearer fake.token.value"
#     }
#     chat_request = {
#         "chatbot_id": str(invalid_chatbot_id),
#         "message": "Hello"
#     }
    
#     response = client.post(
#         "/api/v1/chatbots/public/chat",
#         json=chat_request,
#         headers=headers 
#     )
#     assert response.status_code == 404  # Not found
#     assert response.json()["detail"] == "Chatbot not found"
