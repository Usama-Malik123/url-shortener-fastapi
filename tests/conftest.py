import pytest
import redis as redis_lib
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.db import engine
from app.main import app
from app.redis_client import redis_pool


@pytest.fixture()
def db_session():
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.execute(text("TRUNCATE TABLE urls RESTART IDENTITY"))
        session.commit()
        session.close()


@pytest.fixture()
def redis_client():
    client = redis_lib.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        for key in client.scan_iter("url:*"):
            client.delete(key)


@pytest.fixture()
def client(db_session, redis_client):
    return TestClient(app)
