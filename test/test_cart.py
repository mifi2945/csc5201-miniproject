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

@pytest.fixture
def post_one_to_each(client):
    user_id_1 = 10
    user_id_2 = 20
    product_1 = Product(100, 'prod', 'good product', 1.99, ['kitchen', 'bath'])
    product_2 = Product(2000, 'produce', 'bad product', 100.95, [])

    client.post(f'/cart/{user_id_1}', json=asdict(product_1))
    client.post(f'/cart/{user_id_2}', json=asdict(product_2))

    return ((user_id_1, product_1), (user_id_2, product_2))

@pytest.fixture
def post_two_items(client):
    user_id = 10
    product_1 = Product(100, 'prod', 'good product', 1.99, ['kitchen', 'bath'])
    product_2 = Product(2000, 'produce', 'bad product', 100.95, [])

    client.post(f'/cart/{user_id}', json=asdict(product_1))
    client.post(f'/cart/{user_id}', json=asdict(product_2))

    return (user_id, product_1, product_2)


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

def test_get_from_different_users(client, post_one_to_each):
    user_id_1, product_1 = post_one_to_each[0]
    user_id_2, product_2 = post_one_to_each[1]

    response_1 = client.get(f'/cart/{user_id_1}')
    response_2 = client.get(f'/cart/{user_id_2}')

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_1.json == [asdict(product_1)]
    assert response_2.json == [asdict(product_2)]

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
    expected_items = [asdict(product_1), asdict(product_2)]

    client.post(f'/cart/{user_id}', json=asdict(product_1))
    post_response = client.post(f'/cart/{user_id}', json=asdict(product_2))
    get_response = client.get(f'/cart/{user_id}')

    assert post_response.status_code == 201
    assert get_response.status_code == 200
    assert len(get_response.json) == 2
    assert sorted(get_response.json, key=lambda item: item['product_id']) == \
            sorted(expected_items, key=lambda item: item['product_id'])


##########
# DELETE
##########

def test_delete(client, post_two_items):
    user_id, _, _ = post_two_items

    delete_response = client.delete(f'/cart/{user_id}')
    get_response = client.get(f'/cart/{user_id}')

    assert delete_response.status_code == 204
    assert get_response.json == []
