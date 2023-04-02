import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import models, oauth2
from app.config import settings
from app.database import get_db, Base
from fastapi.testclient import TestClient
from app.main import app

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "test@gmail.com", "password": "testpassword"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "test2@gmail.com", "password": "testpassword2"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return oauth2.create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    posts_data = [{
        "title": "First Title",
        "content": "First content",
        "owner_id": test_user['id']
    }, {
        "title": "Second Title",
        "content": "Second content",
        "owner_id": test_user['id']
    }, {
        "title": "Third Title",
        "content": "Third content",
        "owner_id": test_user['id']
    }, {
        "title": "Fourth Title",
        "content": "Fourth content",
        "owner_id": test_user2['id']
    }]

    def create_post_model(post):
        return models.Post(**post)
    posts_mapping = map(create_post_model, posts_data)
    posts = list(posts_mapping)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts
