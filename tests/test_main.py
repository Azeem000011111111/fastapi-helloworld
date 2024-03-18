import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel, Field 

from fastapi_helloworld.main import app, get_session, Todo
from fastapi_helloworld import settings


# Use the TEST_DATABASE_URL setting
connection_string = str(settings.TEST_DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={"sslmode": "require"})


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="module")
def test_app():
    SQLModel.metadata.create_all(engine)  # Create tables for testing
    with TestClient(app) as client:
        yield client  # Testing happens here
    SQLModel.metadata.drop_all(engine)  # Cleanup


# Your test functions here (see below)
def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_create_todo(test_app):
    response = test_app.post("/todos/", json={"content": "test todo"})
    assert response.status_code == 200

    data = response.json()
    assert data["content"] == "test todo"
    assert "id" in data


def test_read_todos(test_app):
    response = test_app.get("/todos/")
    assert response.status_code == 200
    # Add more assertions to check the content of the response


def test_read_todo(test_app):
    response = test_app.post("/todos/", json={"content": "test todo"})
    todo_id = response.json()["id"]

    response = test_app.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    # Add more assertions about the returned data


def test_update_todo(test_app):
    response = test_app.post("/todos/", json={"content": "test todo"})
    todo_id = response.json()["id"]

    response = test_app.put(f"/todos/{todo_id}", json={"content": "updated todo"})
    assert response.status_code == 200

    data = response.json()
    assert data["content"] == "updated todo"
    assert "id" in data and data["id"] == todo_id




def test_delete_todo(test_app):
    response = test_app.post("/todos/", json={"content": "test todo"})
    todo_id = response.json()["id"]

    response = test_app.delete(f"/todos/{todo_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["content"] == "test todo"
    assert "id" in data and data["id"] == todo_id
    
