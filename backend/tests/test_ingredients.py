from copy import deepcopy
import pytest
from sqlalchemy import select
from app.models import RecipeTool
from tests.conftest import auth_headers
from tests.test_recipes import PASTA


def test_tools_round_trip_edit_and_delete(client, db_session):
    headers = auth_headers(client)
    body = {**deepcopy(PASTA), 'tools': [' Large Pot ', 'large pot', 'Colander']}
    created = client.post('/api/v1/recipes', headers=headers, json=body)
    assert created.status_code == 201
    recipe = created.json()
    assert recipe['tools'] == ['Large Pot', 'Colander']
    assert client.get(f"/api/v1/recipes/{recipe['id']}").json()['tools'] == recipe['tools']
    assert client.get('/api/v1/recipes/my-recipes', headers=headers).json()[0]['tools'] == recipe['tools']
    body['tools'] = ['Skillet']
    assert client.put(f"/api/v1/recipes/{recipe['id']}", headers=headers, json=body).json()['tools'] == ['Skillet']
    assert len(db_session.scalars(select(RecipeTool)).all()) == 1
    assert client.delete(f"/api/v1/recipes/{recipe['id']}", headers=headers).status_code == 204
    assert db_session.scalars(select(RecipeTool)).all() == []


@pytest.mark.parametrize('unit', ['g', 'kg', 'oz', 'lb', 'cup', 'tbsp', 'tsp', 'ml', 'l', 'count', 'pinch'])
def test_supported_units(client, unit):
    headers = auth_headers(client)
    body = deepcopy(PASTA)
    body['ingredients'][0]['unit'] = unit
    assert client.post('/api/v1/recipes', headers=headers, json=body).status_code == 201


@pytest.mark.parametrize('changes', [
    {'tools': [' ']}, {'tools': ['x' * 81]}, {'tools': ['pot'] * 51},
    {'ingredients': [{'name': 'Salt', 'amount': 1, 'unit': 'bucket'}]},
    {'ingredients': [{'name': 'Salt', 'amount': -1, 'unit': 'g'}]},
    {'ingredients': [{'name': 'Salt', 'amount': 'oops', 'unit': 'g'}]},
])
def test_invalid_ingredients_and_tools(client, changes):
    headers = auth_headers(client)
    assert client.post('/api/v1/recipes', headers=headers, json={**deepcopy(PASTA), **changes}).status_code == 422
