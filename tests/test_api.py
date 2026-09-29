import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "API do Assistente Virtual do Residencial Aurora está online!"

from unittest.mock import patch, AsyncMock
from google.adk.events import Event
from google.genai import types

def test_chat_success():
    payload = {
        "user_id": "test_user",
        "session_id": "test_session",
        "message": "Quais são os apartamentos?"
    }
    
    async def mock_run_async(*args, **kwargs):
        # yields a mock Event
        content = types.Content(role="model", parts=[types.Part.from_text(text="101 e 102")])
        yield Event(content=content)
        
    with patch("api.main.runner.run_async", new=mock_run_async):
        response = client.post("/chat", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert data["session_id"] == "test_session"
    assert "101" in data["response"] or "102" in data["response"]

def test_chat_invalid_payload():
    payload = {
        "message": "Falta user_id e session_id"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (FastAPI validation error)
