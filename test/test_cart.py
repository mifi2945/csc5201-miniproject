import pytest
import fakeredis
from dataclasses import asdict
import json

from src.api import app, Product
import src



@pytest.fixture(autouse=True)
def client(monkeypatch):
    app.config['TESTING'] = True
    fake_db = fakeredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(src.api, 'db', fake_db)

    return app.test_client()

@pytest.fixture
def post_one(client):
    user_id = 0

    product = Product(100, 'prod', 'good product', 1.99, ['kitchen', 'bath'])
    client.post(f'/cart/{user_id}', json=asdict(product))

    return (user_id, product)


##########
# GET
##########

def test_empty_get(client):
    user_id = 0

    response = client.get(f'/cart/{user_id}')

    assert response.status_code == 200
    assert response.json == []

def test_item_get(client, post_one):
    user_id, product = post_one

    response = client.get(f'/cart/{user_id}')

    assert response.status_code == 200
    assert response.json == [asdict(product)]

##########
# POST
##########

def test_post_success(client):
    user_id = 0
    product = Product(100, 'prod', 'good product', 1.99, ['kitchen', 'bath'])

    response = client.post(f'/cart/{user_id}', json=asdict(product))

    assert response.status_code == 201
    assert response.json == asdict(product)

def test_post_fail(client):
    user_id = 0
    product = {'name': 'broken product'}

    response = client.post(f'/cart/{user_id}', json=product)

    assert response.status_code == 400

def test_post_two_items(client):
    user_id = 10
    product_1 = Product(100, 'prod', 'good product', 1.99, ['kitchen', 'bath'])
    product_2 = Product(2000, 'produce', 'bad product', 100.95, [])

    client.post(f'/cart/{user_id}', json=asdict(product_1))
    post_response = client.post(f'/cart/{user_id}', json=asdict(product_2))
    get_response = client.get(f'/cart/{user_id}')

    assert post_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json == [asdict(product_1), asdict(product_2)]


##########
# DELETE
##########