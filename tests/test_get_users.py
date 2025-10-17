from fastapi.testclient import TestClient

def test_get_users(client: TestClient) -> None:
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_get_user_by_id(client: TestClient) -> None:
    user_id = 1
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    