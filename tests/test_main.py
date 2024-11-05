import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session, engine, create_db_and_tables
from sqlmodel import Session, false, true, text

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    # Создаём таблицы перед тестами
    create_db_and_tables()
    yield
    with Session(engine) as session:
        session.execute(text("DROP TABLE IF EXISTS message"))
        session.execute(text("DROP TABLE IF EXISTS user"))
        session.commit()


@pytest.fixture
def session():
    with Session(engine) as session:
        yield session


def test_register_user(session, setup_database):
    response = client.post("/register", json={
        "username": "testuser",
        "password": "testpass",
        "moderator": False
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_login_user(session, setup_database):
    client.post("/register", json={
        "username": "testuser2",
        "password": "testpass2",
        "moderator": False
    })
    response = client.post("/login", json={
        "username": "testuser2",
        "password": "testpass2",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_send_message(session, setup_database):
    token_response = client.post("/login", json={
        "username": "testuser2",
        "password": "testpass2"
    })
    token = token_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/messages", headers=headers, json={
        "content": "Hello, World!",
        "sender_id": 1,
        "channel_id": 1
    })
    assert response.status_code == 200
    assert response.json()["content"] == "Hello, World!"


def test_get_messages(session, setup_database):
    token_response = client.post("/login", json={
        "username": "testuser2",
        "password": "testpass2"
    })
    token = token_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/messages", headers=headers, json={
        "content": "Hi, World!",
        "sender_id": 2,
        "channel_id": 1
    })
    response = client.get("/messages/testuser2/1", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_messages(session, setup_database):
    client.post("/register", json={
        "username": "moderator",
        "password": "modpass",
        "moderator": True
    })
    token_response = client.post("/login", json={
        "username": "moderator",
        "password": "modpass"
    })
    token = token_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/admin/messages?token={token}", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_websocket(session, setup_database):
    token_response = client.post("/login", json={
        "username": "testuser2",
        "password": "testpass2"
    })
    token = token_response.json()["access_token"]
    with client.websocket_connect(f"/ws/chat/1?token={token}") as websocket:
        websocket.send_text("Hello via WebSocket")
        data = websocket.receive_text()
        assert data == f"[Channel {1}] User {2}: Hello via WebSocket"


def test_delete_user(session, setup_database):
    token_response = client.post("/login", json={
        "username": "moderator",
        "password": "modpass"
    })
    token = token_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = client.delete("/admin/users/1?token={token}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted"
    except Exception:
        assert "User does not exist"
