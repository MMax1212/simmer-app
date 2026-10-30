from tests.conftest import auth_headers

# -- US2.2 Task 2.1: EndPoint Exists & Returns 200 ---
def test_search_empty_database(client):
    res = client.get("/api/v1/recipes")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []
