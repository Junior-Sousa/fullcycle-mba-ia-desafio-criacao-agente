import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "API do Assistente Virtual do Residencial Aurora está online!"

def test_chat_success():
    payload = {
        "user_id": "test_user",
        "session_id": "test_session",
        "message": "Quais são os apartamentos?"
    }
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
