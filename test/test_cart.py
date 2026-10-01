import pytest
import fakeredis
from src.api import app, db
import src

@pytest.fixture(autouse=True)
def client(monkeypatch):
    app.config['TESTING'] = True
    fake_db = fakeredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(src, 'db', fake_db)

    return app.test_client()



def test_empty_get(client):
    user_id = 0

    response = client.get(f'/cart/{user_id}')

    assert response.status_code == 200